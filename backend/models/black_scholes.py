"""
Black-Scholes Analytical Option Pricing Model.

Implements the closed-form solution for European call and put options.
"""

import numpy as np
from scipy.stats import norm


def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Calculate d1 parameter."""
    return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def _d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Calculate d2 parameter."""
    return _d1(S, K, T, r, sigma) - sigma * np.sqrt(T)


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
) -> float:
    """
    Calculate European option price using Black-Scholes formula.

    Args:
        S: Current stock price (spot)
        K: Strike price
        T: Time to expiration in years
        r: Risk-free interest rate (annualized)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'

    Returns:
        Option price
    """
    if T <= 0:
        if option_type.lower() == "call":
            return max(S - K, 0.0)
        return max(K - S, 0.0)

    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)

    if option_type.lower() == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type.lower() == "put":
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError(f"Invalid option_type: {option_type}. Use 'call' or 'put'.")


def delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Analytical Delta: dPrice/dS."""
    if T <= 0:
        if option_type.lower() == "call":
            return 1.0 if S > K else 0.0
        return -1.0 if S < K else 0.0
    d1 = _d1(S, K, T, r, sigma)
    if option_type.lower() == "call":
        return norm.cdf(d1)
    return norm.cdf(d1) - 1.0


def gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Analytical Gamma: d²Price/dS² (same for call and put)."""
    if T <= 0:
        return 0.0
    d1 = _d1(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))


def theta(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Analytical Theta: dPrice/dT (per year, negate for time decay per day divide by 365)."""
    if T <= 0:
        return 0.0
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)

    term1 = -(S * norm.pdf(d1) * sigma) / (2.0 * np.sqrt(T))

    if option_type.lower() == "call":
        term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
    else:
        term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)

    return (term1 + term2) / 365.0  # Per-day theta


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Analytical Vega: dPrice/dSigma (same for call and put). Per 1% move."""
    if T <= 0:
        return 0.0
    d1 = _d1(S, K, T, r, sigma)
    return S * norm.pdf(d1) * np.sqrt(T) * 0.01  # Per 1% change in vol


def rho(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> float:
    """Analytical Rho: dPrice/dR. Per 1% move in rate."""
    if T <= 0:
        return 0.0
    d2 = _d2(S, K, T, r, sigma)
    if option_type.lower() == "call":
        return K * T * np.exp(-r * T) * norm.cdf(d2) * 0.01
    return -K * T * np.exp(-r * T) * norm.cdf(-d2) * 0.01
