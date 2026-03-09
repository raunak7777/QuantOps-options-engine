from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import time
import numpy as np

from models import black_scholes, binomial_tree, monte_carlo, greeks, implied_vol
from ml import ensemble

router = APIRouter(prefix="/api")

# ──────────────────────────── Request / Response Models ────────────────────────

class PriceRequest(BaseModel):
    S: float = Field(..., description="Spot price", gt=0)
    K: float = Field(..., description="Strike price", gt=0)
    T: float = Field(..., description="Time to expiration (years)", gt=0)
    r: float = Field(0.05, description="Risk-free rate")
    sigma: float = Field(..., description="Volatility", gt=0)
    option_type: str = Field("call", description="'call' or 'put'")
    model: str = Field("black-scholes", description="Pricing model: 'black-scholes', 'binomial', 'monte-carlo', or 'all'")
    american: bool = Field(False, description="American option (binomial only)")
    steps: int = Field(200, description="Binomial tree steps")
    n_paths: int = Field(10000, description="Monte Carlo paths", le=100000)


class GreeksRequest(BaseModel):
    S: float = Field(..., gt=0)
    K: float = Field(..., gt=0)
    T: float = Field(..., gt=0)
    r: float = Field(0.05)
    sigma: float = Field(..., gt=0)
    option_type: str = Field("call")
    method: str = Field("both", description="'analytical', 'numerical', or 'both'")
    spot_range: float = Field(0.3, description="Range for Greeks vs spot chart (fraction)")
    n_points: int = Field(50, description="Number of chart points")


class SurfaceRequest(BaseModel):
    S: float = Field(..., gt=0, description="Spot price")
    r: float = Field(0.05)
    base_sigma: float = Field(0.25, description="Base volatility")
    skew_factor: float = Field(0.1)
    term_factor: float = Field(0.05)
    n_strikes: int = Field(20, ge=5, le=50)
    ticker: str = Field("", description="Optional ticker for live data")


class MonteCarloRequest(BaseModel):
    S: float = Field(..., gt=0)
    K: float = Field(..., gt=0)
    T: float = Field(..., gt=0)
    r: float = Field(0.05)
    sigma: float = Field(..., gt=0)
    option_type: str = Field("call")
    n_paths: int = Field(10000, le=100000)
    n_steps: int = Field(252, le=504)
    antithetic: bool = Field(True)
    control_variate: bool = Field(True)
    seed: int | None = Field(None)


class PredictVolRequest(BaseModel):
    ticker: str = Field("AAPL", description="Stock ticker")
    horizon: int = Field(10, description="Forecast horizon (days)", ge=1, le=60)
    history_days: int = Field(365, description="Days of history to use")


class ImpliedVolRequest(BaseModel):
    market_price: float = Field(..., gt=0)
    S: float = Field(..., gt=0)
    K: float = Field(..., gt=0)
    T: float = Field(..., gt=0)
    r: float = Field(0.05)
    option_type: str = Field("call")
    initial_guess: float = Field(0.3, gt=0)


# ──────────────────────────── Endpoints ───────────────────────────────────────

@router.post("/price")
async def price_option(req: PriceRequest):
    """Price an option using the specified model."""
    try:
        result = {}

        if req.model in ("black-scholes", "all"):
            result["black_scholes"] = {
                "price": black_scholes.price(req.S, req.K, req.T, req.r, req.sigma, req.option_type),
                "model": "Black-Scholes",
            }

        if req.model in ("binomial", "all"):
            result["binomial"] = {
                "price": binomial_tree.price(
                    req.S, req.K, req.T, req.r, req.sigma,
                    req.option_type, req.american, req.steps
                ),
                "model": "Binomial Tree (CRR)",
                "steps": req.steps,
                "american": req.american,
            }

        if req.model in ("monte-carlo", "all"):
            mc_result = monte_carlo.price(
                req.S, req.K, req.T, req.r, req.sigma, req.option_type,
                req.n_paths,
            )
            result["monte_carlo"] = {
                "price": mc_result["price"],
                "std_error": mc_result["std_error"],
                "confidence_interval_95": mc_result["confidence_interval_95"],
                "model": "Monte Carlo",
                "n_paths": req.n_paths,
            }

        if req.model not in ("black-scholes", "binomial", "monte-carlo", "all"):
            raise HTTPException(400, f"Unknown model: {req.model}")

        result["parameters"] = {
            "S": req.S, "K": req.K, "T": req.T,
            "r": req.r, "sigma": req.sigma,
            "option_type": req.option_type,
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/greeks")
async def compute_greeks(req: GreeksRequest):
    """Compute option Greeks (analytical and/or numerical)."""
    try:
        result = {}

        if req.method in ("analytical", "both"):
            result["analytical"] = greeks.analytical(
                req.S, req.K, req.T, req.r, req.sigma, req.option_type
            )

        if req.method in ("numerical", "both"):
            result["numerical"] = greeks.numerical(
                req.S, req.K, req.T, req.r, req.sigma, req.option_type
            )

        # Greeks vs spot for charting
        result["chart_data"] = greeks.greeks_vs_spot(
            req.S, req.K, req.T, req.r, req.sigma, req.option_type,
            req.spot_range, req.n_points
        )

        result["parameters"] = {
            "S": req.S, "K": req.K, "T": req.T,
            "r": req.r, "sigma": req.sigma,
            "option_type": req.option_type,
        }

        return result

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/surface")
async def volatility_surface(req: SurfaceRequest):
    """Generate volatility surface data."""
    try:
        strikes = np.linspace(req.S * 0.7, req.S * 1.3, req.n_strikes).tolist()
        surface = implied_vol.volatility_surface(
            req.S, req.r, strikes=strikes,
            base_sigma=req.base_sigma,
            skew_factor=req.skew_factor,
            term_factor=req.term_factor,
        )
        return surface

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/monte-carlo")
async def monte_carlo_simulation(req: MonteCarloRequest):
    """Run Monte Carlo simulation and return paths + distribution."""
    try:
        result = monte_carlo.price(
            req.S, req.K, req.T, req.r, req.sigma, req.option_type,
            req.n_paths, req.n_steps, req.antithetic, req.control_variate,
            req.seed,
        )
        result["parameters"] = {
            "S": req.S, "K": req.K, "T": req.T,
            "r": req.r, "sigma": req.sigma,
            "option_type": req.option_type,
        }
        return result

    except Exception as e:
        raise HTTPException(500, str(e))


def _mock_historical(ticker: str, days: int) -> dict:
    """Generate realistic mock historical data for volatility prediction."""
    np.random.seed(hash(ticker) % 2**32)
    n = min(days, 252)

    base_prices = {"AAPL": 175, "MSFT": 380, "TSLA": 250, "SPY": 450, "AMZN": 180}
    S0 = base_prices.get(ticker.upper(), 150)

    mu = 0.08 / 252
    sigma = 0.25 / np.sqrt(252)
    returns = np.random.normal(mu, sigma, n)
    log_prices = np.log(S0) + np.cumsum(returns)
    closes = np.exp(log_prices).tolist()

    avg_vol = 50_000_000
    volumes = (np.random.lognormal(np.log(avg_vol), 0.5, n)).astype(int).tolist()

    now = int(time.time() * 1000)
    day_ms = 86400 * 1000
    dates = [now - (n - i) * day_ms for i in range(n)]

    return {
        "ticker": ticker,
        "dates": dates,
        "closes": closes,
        "volumes": volumes,
        "log_returns": returns.tolist(),
        "n_days": n,
    }


@router.post("/predict-vol")
async def predict_volatility(req: PredictVolRequest):
    """Get AI-driven volatility forecast with regime detection."""
    try:
        # Generate mock historical data
        hist = _mock_historical(req.ticker, req.history_days)
        returns = np.array(hist["log_returns"])
        volumes = np.array(hist.get("volumes", []))

        if len(returns) < 60:
            raise HTTPException(400, "Insufficient data for prediction (need ≥60 days)")

        # Get ensemble prediction
        result = ensemble.predict(
            returns,
            volumes=volumes if len(volumes) == len(returns) + 1 else None,
            horizon=req.horizon,
        )

        result["ticker"] = req.ticker
        result["data_info"] = {
            "n_days": hist["n_days"],
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/implied-vol")
async def solve_implied_vol(req: ImpliedVolRequest):
    """Solve for implied volatility from market price."""
    try:
        result = implied_vol.solve(
            req.market_price, req.S, req.K, req.T, req.r,
            req.option_type, req.initial_guess,
        )
        result["parameters"] = {
            "market_price": req.market_price,
            "S": req.S, "K": req.K, "T": req.T,
            "r": req.r, "option_type": req.option_type,
        }
        return result

    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Options Pricing Engine"}
