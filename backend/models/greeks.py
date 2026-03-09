"""
Greeks Calculator.

Provides both analytical (from Black-Scholes) and numerical (finite difference)
methods for computing option sensitivities.
"""

import numpy as np
from models import black_scholes


def analytical(
    S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call"
) -> dict:
    """
    Calculate all Greeks using Black-Scholes analytical formulas.

    Returns:
        Dictionary with delta, gamma, theta, vega, rho
    """
    return {
        "delta": black_scholes.delta(S, K, T, r, sigma, option_type),
        "gamma": black_scholes.gamma(S, K, T, r, sigma),
        "theta": black_scholes.theta(S, K, T, r, sigma, option_type),
        "vega": black_scholes.vega(S, K, T, r, sigma),
        "rho": black_scholes.rho(S, K, T, r, sigma, option_type),
    }


def numerical(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
    dS: float | None = None,
    dT: float = 1.0 / 365.0,
    dSigma: float = 0.01,
    dR: float = 0.01,
) -> dict:
    """
    Calculate all Greeks using central finite differences.

    Args:
        S, K, T, r, sigma, option_type: Standard option parameters
        dS: Bump size for spot (default: 1% of S)
        dT: Bump size for time (default: 1 day)
        dSigma: Bump size for volatility
        dR: Bump size for interest rate

    Returns:
        Dictionary with delta, gamma, theta, vega, rho
    """
    if dS is None:
        dS = S * 0.01  # 1% of spot

    bs = black_scholes.price

    # Delta: central difference dP/dS
    p_up = bs(S + dS, K, T, r, sigma, option_type)
    p_down = bs(S - dS, K, T, r, sigma, option_type)
    delta_val = (p_up - p_down) / (2 * dS)

    # Gamma: second derivative d²P/dS²
    p_mid = bs(S, K, T, r, sigma, option_type)
    gamma_val = (p_up - 2 * p_mid + p_down) / (dS**2)

    # Theta: dP/dT (forward difference since T decreases)
    if T > dT:
        p_t_down = bs(S, K, T - dT, r, sigma, option_type)
        theta_val = (p_t_down - p_mid) / dT / 365.0  # Per-day
    else:
        theta_val = 0.0

    # Vega: dP/dSigma (per 1% move)
    p_vol_up = bs(S, K, T, r, sigma + dSigma, option_type)
    p_vol_down = bs(S, K, T, r, sigma - dSigma, option_type)
    vega_val = (p_vol_up - p_vol_down) / (2 * dSigma) * 0.01

    # Rho: dP/dR (per 1% move)
    p_r_up = bs(S, K, T, r + dR, sigma, option_type)
    p_r_down = bs(S, K, T, r - dR, sigma, option_type)
    rho_val = (p_r_up - p_r_down) / (2 * dR) * 0.01

    return {
        "delta": delta_val,
        "gamma": gamma_val,
        "theta": theta_val,
        "vega": vega_val,
        "rho": rho_val,
    }


def greeks_vs_spot(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
    spot_range: float = 0.3,
    n_points: int = 50,
) -> dict:
    """
    Calculate Greeks across a range of spot prices for charting.

    Args:
        spot_range: Fraction of S for the range (e.g., 0.3 = ±30%)
        n_points: Number of points

    Returns:
        Dictionary with spot_prices array and arrays for each Greek
    """
    spots = np.linspace(S * (1 - spot_range), S * (1 + spot_range), n_points)
    result = {
        "spot_prices": spots.tolist(),
        "delta": [],
        "gamma": [],
        "theta": [],
        "vega": [],
        "rho": [],
    }

    for s in spots:
        g = analytical(s, K, T, r, sigma, option_type)
        for key in ["delta", "gamma", "theta", "vega", "rho"]:
            result[key].append(g[key])

    return result
