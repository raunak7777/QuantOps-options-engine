"""
GARCH(1,1) Volatility Model.

Industry-standard model for capturing volatility clustering.
Uses the `arch` library for estimation.
"""

import numpy as np


def fit_and_forecast(
    returns: np.ndarray | list,
    horizon: int = 10,
) -> dict:
    """
    Fit GARCH(1,1) to historical log returns and forecast volatility.

    Args:
        returns: Array of log returns (daily)
        horizon: Number of days to forecast

    Returns:
        Dictionary with fitted parameters, conditional volatility,
        and forecasted volatility
    """
    returns = np.asarray(returns, dtype=float)

    try:
        from arch import arch_model

        # Fit GARCH(1,1) — returns scaled by 100 for numerical stability
        model = arch_model(returns * 100, vol="Garch", p=1, q=1, mean="Zero")
        result = model.fit(disp="off", show_warning=False)

        # Get conditional volatility (in-sample)
        cond_vol = result.conditional_volatility / 100.0  # Scale back

        # Forecast
        forecast = result.forecast(horizon=horizon)
        forecast_variance = forecast.variance.values[-1] / (100**2)
        forecast_vol = np.sqrt(forecast_variance).tolist()

        # Annualize
        forecast_vol_annual = [v * np.sqrt(252) for v in forecast_vol]

        return {
            "model": "GARCH(1,1)",
            "params": {
                "omega": float(result.params.get("omega", 0)) / (100**2),
                "alpha": float(result.params.get("alpha[1]", 0)),
                "beta": float(result.params.get("beta[1]", 0)),
            },
            "conditional_volatility": cond_vol.tolist()[-60:],  # Last 60 days
            "forecast_daily": forecast_vol,
            "forecast_annualized": forecast_vol_annual,
            "current_vol_daily": float(cond_vol.iloc[-1]) if len(cond_vol) > 0 else 0,
            "current_vol_annual": float(cond_vol.iloc[-1] * np.sqrt(252)) if len(cond_vol) > 0 else 0,
            "horizon": horizon,
            "success": True,
        }

    except Exception as e:
        # Fallback: simple exponentially weighted volatility
        return _fallback_ewma(returns, horizon, str(e))


def _fallback_ewma(returns: np.ndarray, horizon: int, error_msg: str = "") -> dict:
    """Fallback EWMA volatility when GARCH fitting fails."""
    lam = 0.94  # RiskMetrics lambda
    n = len(returns)
    var = np.var(returns)
    variances = [var]

    for i in range(1, n):
        var = lam * var + (1 - lam) * returns[i - 1] ** 2
        variances.append(var)

    current_vol = np.sqrt(variances[-1])
    forecast_vol = [float(current_vol)] * horizon
    forecast_annual = [float(current_vol * np.sqrt(252))] * horizon

    return {
        "model": "EWMA (fallback)",
        "params": {"lambda": lam},
        "conditional_volatility": [np.sqrt(v) for v in variances[-60:]],
        "forecast_daily": forecast_vol,
        "forecast_annualized": forecast_annual,
        "current_vol_daily": float(current_vol),
        "current_vol_annual": float(current_vol * np.sqrt(252)),
        "horizon": horizon,
        "success": True,
        "fallback_reason": error_msg,
    }
