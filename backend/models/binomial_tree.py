"""
Binomial Tree (Cox-Ross-Rubinstein) Option Pricing Model.

Recombining lattice model that supports both European and American options.
Converges to Black-Scholes as the number of steps increases.
"""

import numpy as np


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
    american: bool = False,
    steps: int = 200,
) -> float:
    """
    Price an option using the CRR Binomial Tree model.

    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration in years
        r: Risk-free rate (annualized)
        sigma: Volatility (annualized)
        option_type: 'call' or 'put'
        american: If True, allows early exercise
        steps: Number of time steps in the tree

    Returns:
        Option price
    """
    if T <= 0:
        if option_type.lower() == "call":
            return max(S - K, 0.0)
        return max(K - S, 0.0)

    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))       # Up factor
    d = 1.0 / u                            # Down factor
    p = (np.exp(r * dt) - d) / (u - d)    # Risk-neutral probability
    disc = np.exp(-r * dt)                 # Discount factor per step

    # Build stock prices at maturity (step N)
    stock_prices = S * u ** np.arange(steps, -1, -1) * d ** np.arange(0, steps + 1)

    # Calculate terminal payoffs
    if option_type.lower() == "call":
        option_values = np.maximum(stock_prices - K, 0.0)
    elif option_type.lower() == "put":
        option_values = np.maximum(K - stock_prices, 0.0)
    else:
        raise ValueError(f"Invalid option_type: {option_type}.")

    # Backward induction through the tree
    for step in range(steps - 1, -1, -1):
        # Stock prices at this step
        stock_at_step = S * u ** np.arange(step, -1, -1) * d ** np.arange(0, step + 1)

        # Continuation value
        option_values = disc * (p * option_values[:-1] + (1 - p) * option_values[1:])

        # American option: check early exercise
        if american:
            if option_type.lower() == "call":
                exercise = np.maximum(stock_at_step - K, 0.0)
            else:
                exercise = np.maximum(K - stock_at_step, 0.0)
            option_values = np.maximum(option_values, exercise)

    return float(option_values[0])


def price_with_tree(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call",
    american: bool = False,
    steps: int = 50,
) -> dict:
    """
    Price an option and return the full tree structure (for visualization).
    Limited to smaller step counts for performance.

    Returns:
        Dictionary with 'price' and 'tree' (list of lists with stock prices and option values).
    """
    steps = min(steps, 50)  # Cap for visualization
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    # Build full stock tree
    stock_tree = []
    for i in range(steps + 1):
        level = [S * u ** j * d ** (i - j) for j in range(i, -1, -1)]
        stock_tree.append(level)

    # Terminal payoffs
    if option_type.lower() == "call":
        option_values = [max(s - K, 0) for s in stock_tree[-1]]
    else:
        option_values = [max(K - s, 0) for s in stock_tree[-1]]

    option_tree = [None] * (steps + 1)
    option_tree[steps] = option_values[:]

    # Backward induction
    for step in range(steps - 1, -1, -1):
        new_values = []
        for j in range(step + 1):
            cont = disc * (p * option_tree[step + 1][j] + (1 - p) * option_tree[step + 1][j + 1])
            if american:
                if option_type.lower() == "call":
                    ex = max(stock_tree[step][j] - K, 0)
                else:
                    ex = max(K - stock_tree[step][j], 0)
                cont = max(cont, ex)
            new_values.append(cont)
        option_tree[step] = new_values

    return {
        "price": option_tree[0][0],
        "tree": {
            "stock_prices": stock_tree,
            "option_values": option_tree,
            "u": u,
            "d": d,
            "p": p,
        },
    }
