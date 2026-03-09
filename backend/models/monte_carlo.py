"""
Monte Carlo Option Pricing via Geometric Brownian Motion (GBM).

Implements variance reduction techniques:
  - Antithetic variates
  - Control variates (using Black-Scholes as control)
"""

import numpy as np
from models import black_scholes


def simulate_paths(
    S: float,
    T: float,
    r: float,
    sigma: float,
    n_paths: int = 10000,
    n_steps: int = 252,
    antithetic: bool = True,
    seed: int | None = None,
) -> np.ndarray:
    """
    Simulate GBM price paths.

    Args:
        S: Initial stock price
        T: Time horizon in years
        r: Risk-free rate
        sigma: Volatility
        n_paths: Number of simulation paths
        n_steps: Number of time steps per path
        antithetic: Whether to use antithetic variates
        seed: Random seed for reproducibility

    Returns:
        Array of shape (n_paths, n_steps + 1) with price paths
    """
    if seed is not None:
        np.random.seed(seed)

    dt = T / n_steps
    nudt = (r - 0.5 * sigma**2) * dt
    sigdt = sigma * np.sqrt(dt)

    if antithetic:
        half = n_paths // 2
        Z = np.random.standard_normal((half, n_steps))
        Z = np.vstack([Z, -Z])  # Antithetic pairs
    else:
        Z = np.random.standard_normal((n_paths, n_steps))

    # Log-price increments
    log_returns = nudt + sigdt * Z
    log_paths = np.zeros((Z.shape[0], n_steps + 1))
    log_paths[:, 0] = np.log(S)
    log_paths[:, 1:] = np.log(S) + np.cumsum(log_returns, axis=1)

    return np.exp(log_paths)


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
    n_paths: int = 10000,
    n_steps: int = 252,
    antithetic: bool = True,
    control_variate: bool = True,
    seed: int | None = None,
) -> dict:
    """
    Price a European option using Monte Carlo simulation.

    Args:
        S, K, T, r, sigma, option_type: Standard option parameters
        n_paths: Number of simulation paths
        n_steps: Time steps per path
        antithetic: Use antithetic variates
        control_variate: Use Black-Scholes as control variate
        seed: Random seed

    Returns:
        Dictionary with price, std_error, paths (subset), and payoff distribution
    """
    paths = simulate_paths(S, T, r, sigma, n_paths, n_steps, antithetic, seed)
    final_prices = paths[:, -1]

    # Calculate payoffs
    if option_type.lower() == "call":
        payoffs = np.maximum(final_prices - K, 0.0)
    elif option_type.lower() == "put":
        payoffs = np.maximum(K - final_prices, 0.0)
    else:
        raise ValueError(f"Invalid option_type: {option_type}.")

    discounted_payoffs = np.exp(-r * T) * payoffs

    # Control variate adjustment
    if control_variate and T > 0:
        bs_price = black_scholes.price(S, K, T, r, sigma, option_type)

        # Use final stock price as control
        control = np.exp(-r * T) * final_prices
        expected_control = S  # E[exp(-rT) * S_T] = S under risk-neutral

        # Optimal beta via covariance
        cov_matrix = np.cov(discounted_payoffs, control)
        if cov_matrix[1, 1] > 0:
            beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        else:
            beta = 0.0

        adjusted_payoffs = discounted_payoffs - beta * (control - expected_control)
        mc_price = float(np.mean(adjusted_payoffs))
        mc_std = float(np.std(adjusted_payoffs) / np.sqrt(n_paths))
    else:
        mc_price = float(np.mean(discounted_payoffs))
        mc_std = float(np.std(discounted_payoffs) / np.sqrt(n_paths))

    # Select subset of paths for visualization (max 200)
    n_viz = min(200, n_paths)
    viz_indices = np.linspace(0, n_paths - 1, n_viz, dtype=int)
    viz_paths = paths[viz_indices].tolist()

    return {
        "price": mc_price,
        "std_error": mc_std,
        "confidence_interval_95": [mc_price - 1.96 * mc_std, mc_price + 1.96 * mc_std],
        "n_paths": n_paths,
        "n_steps": n_steps,
        "paths": viz_paths,
        "payoff_distribution": {
            "mean": float(np.mean(payoffs)),
            "std": float(np.std(payoffs)),
            "percentiles": {
                "5": float(np.percentile(payoffs, 5)),
                "25": float(np.percentile(payoffs, 25)),
                "50": float(np.percentile(payoffs, 50)),
                "75": float(np.percentile(payoffs, 75)),
                "95": float(np.percentile(payoffs, 95)),
            },
            "histogram": _compute_histogram(payoffs),
        },
    }


def _compute_histogram(payoffs: np.ndarray, bins: int = 50) -> dict:
    """Compute histogram data for the payoff distribution."""
    counts, edges = np.histogram(payoffs, bins=bins)
    return {
        "counts": counts.tolist(),
        "bin_edges": edges.tolist(),
    }
