"""
Implied Volatility Solver.

Back-calculates the volatility from a market-observed option price
using Newton-Raphson (primary) with Bisection fallback.
"""

import numpy as np
from scipy.stats import norm
from models import black_scholes


def solve_newton_raphson(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    initial_guess: float = 0.3,
    tolerance: float = 1e-6,
    max_iterations: int = 100,
) -> dict:
    """
    Solve for implied volatility using Newton-Raphson method.

    Uses Vega as the derivative for faster convergence.

    Args:
        market_price: Observed market price of the option
        S, K, T, r: Standard option parameters
        option_type: 'call' or 'put'
        initial_guess: Starting volatility estimate
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations

    Returns:
        Dictionary with implied_vol, converged, iterations, and price_error
    """
    sigma = initial_guess
    iterations = 0

    for i in range(max_iterations):
        iterations = i + 1
        bs_price = black_scholes.price(S, K, T, r, sigma, option_type)
        diff = bs_price - market_price

        if abs(diff) < tolerance:
            return {
                "implied_vol": sigma,
                "converged": True,
                "iterations": iterations,
                "price_error": abs(diff),
                "method": "newton-raphson",
            }

        # Vega (un-scaled, raw dP/dSigma)
        d1 = black_scholes._d1(S, K, T, r, sigma)
        vega_raw = S * norm.pdf(d1) * np.sqrt(T)

        if abs(vega_raw) < 1e-12:
            break  # Vega too small, switch to bisection

        sigma = sigma - diff / vega_raw
        sigma = max(sigma, 1e-6)  # Keep sigma positive

    # Newton-Raphson failed, fall back to bisection
    return solve_bisection(market_price, S, K, T, r, option_type, tolerance, max_iterations)


def solve_bisection(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    tolerance: float = 1e-6,
    max_iterations: int = 200,
    low: float = 1e-6,
    high: float = 5.0,
) -> dict:
    """
    Solve for implied volatility using Bisection method.

    More robust but slower than Newton-Raphson.

    Args:
        market_price: Observed market price
        S, K, T, r, option_type: Standard parameters
        tolerance: Convergence tolerance
        max_iterations: Maximum iterations
        low: Lower bound for volatility search
        high: Upper bound for volatility search

    Returns:
        Dictionary with implied_vol, converged, iterations, and price_error
    """
    iterations = 0

    for i in range(max_iterations):
        iterations = i + 1
        mid = (low + high) / 2.0
        bs_price = black_scholes.price(S, K, T, r, mid, option_type)
        diff = bs_price - market_price

        if abs(diff) < tolerance or (high - low) / 2.0 < tolerance:
            return {
                "implied_vol": mid,
                "converged": True,
                "iterations": iterations,
                "price_error": abs(diff),
                "method": "bisection",
            }

        if diff > 0:
            high = mid
        else:
            low = mid

    return {
        "implied_vol": (low + high) / 2.0,
        "converged": False,
        "iterations": iterations,
        "price_error": abs(black_scholes.price(S, K, T, r, (low + high) / 2.0, option_type) - market_price),
        "method": "bisection",
    }


def solve(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = "call",
    initial_guess: float = 0.3,
    tolerance: float = 1e-6,
) -> dict:
    """
    Convenience function: tries Newton-Raphson first, falls back to Bisection.
    """
    return solve_newton_raphson(
        market_price, S, K, T, r, option_type, initial_guess, tolerance
    )


def volatility_surface(
    S: float,
    r: float,
    strikes: list[float] | None = None,
    maturities: list[float] | None = None,
    base_sigma: float = 0.25,
    skew_factor: float = 0.1,
    term_factor: float = 0.05,
) -> dict:
    """
    Generate a synthetic volatility surface (strike × maturity → IV).

    Creates a realistic volatility smile/skew pattern.

    Args:
        S: Current spot price
        r: Risk-free rate
        strikes: List of strike prices (default: ±30% around S)
        maturities: List of maturities in years (default: 1 week to 1 year)
        base_sigma: Base volatility level
        skew_factor: Controls skew steepness
        term_factor: Controls term structure slope

    Returns:
        Dictionary with strikes, maturities, and iv_matrix (2D grid)
    """
    if strikes is None:
        strikes = np.linspace(S * 0.7, S * 1.3, 20).tolist()
    if maturities is None:
        maturities = [1/52, 2/52, 1/12, 2/12, 3/12, 6/12, 9/12, 1.0]

    iv_matrix = []
    for T in maturities:
        row = []
        for K in strikes:
            moneyness = np.log(K / S)
            # Volatility smile: higher IV for OTM options
            smile = skew_factor * moneyness**2
            # Skew: slightly higher IV for OTM puts (negative moneyness)
            skew = -0.03 * moneyness
            # Term structure: IV decreases slightly with longer maturities
            term = -term_factor * np.sqrt(T)
            iv = base_sigma + smile + skew + term
            iv = max(iv, 0.05)  # Floor
            row.append(round(iv, 4))
        iv_matrix.append(row)

    return {
        "strikes": [round(k, 2) for k in strikes],
        "maturities": [round(t, 4) for t in maturities],
        "iv_matrix": iv_matrix,
        "spot": S,
    }
