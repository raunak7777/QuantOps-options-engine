"""
Unit tests for the pricing engine models.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from models import black_scholes, binomial_tree, monte_carlo, greeks, implied_vol


# ─── Black-Scholes Tests ─────────────────────────────────────────────────────

class TestBlackScholes:
    """Tests for the Black-Scholes model."""

    def test_call_price_positive(self):
        price = black_scholes.price(100, 100, 1, 0.05, 0.2, "call")
        assert price > 0

    def test_put_price_positive(self):
        price = black_scholes.price(100, 100, 1, 0.05, 0.2, "put")
        assert price > 0

    def test_put_call_parity(self):
        """C - P = S - K*exp(-rT)"""
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        call = black_scholes.price(S, K, T, r, sigma, "call")
        put = black_scholes.price(S, K, T, r, sigma, "put")
        parity = S - K * np.exp(-r * T)
        assert abs((call - put) - parity) < 1e-10

    def test_deep_itm_call(self):
        """Deep ITM call ≈ S - K*exp(-rT)"""
        price = black_scholes.price(200, 100, 1, 0.05, 0.2, "call")
        intrinsic = 200 - 100 * np.exp(-0.05)
        assert abs(price - intrinsic) < 2.0  # Close to intrinsic

    def test_deep_otm_call(self):
        """Deep OTM call ≈ 0"""
        price = black_scholes.price(50, 200, 0.1, 0.05, 0.2, "call")
        assert price < 0.01

    def test_expired_option(self):
        assert black_scholes.price(110, 100, 0, 0.05, 0.2, "call") == 10.0
        assert black_scholes.price(90, 100, 0, 0.05, 0.2, "call") == 0.0

    def test_call_delta_range(self):
        d = black_scholes.delta(100, 100, 1, 0.05, 0.2, "call")
        assert 0 < d < 1

    def test_put_delta_range(self):
        d = black_scholes.delta(100, 100, 1, 0.05, 0.2, "put")
        assert -1 < d < 0

    def test_gamma_positive(self):
        g = black_scholes.gamma(100, 100, 1, 0.05, 0.2)
        assert g > 0

    def test_vega_positive(self):
        v = black_scholes.vega(100, 100, 1, 0.05, 0.2)
        assert v > 0


# ─── Binomial Tree Tests ─────────────────────────────────────────────────────

class TestBinomialTree:
    """Tests for the Binomial Tree model."""

    def test_converges_to_bs(self):
        """Binomial should converge to BS for European options."""
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        bs_price = black_scholes.price(S, K, T, r, sigma, "call")
        bt_price = binomial_tree.price(S, K, T, r, sigma, "call", american=False, steps=500)
        assert abs(bt_price - bs_price) / bs_price < 0.005  # Within 0.5%

    def test_american_put_geq_european(self):
        """American put ≥ European put (early exercise premium)."""
        S, K, T, r, sigma = 100, 110, 1, 0.05, 0.3
        eu_put = binomial_tree.price(S, K, T, r, sigma, "put", american=False)
        am_put = binomial_tree.price(S, K, T, r, sigma, "put", american=True)
        assert am_put >= eu_put - 1e-10

    def test_price_with_tree(self):
        """Test tree visualization output."""
        result = binomial_tree.price_with_tree(100, 100, 1, 0.05, 0.2, steps=10)
        assert "price" in result
        assert "tree" in result
        assert result["price"] > 0


# ─── Monte Carlo Tests ───────────────────────────────────────────────────────

class TestMonteCarlo:
    """Tests for Monte Carlo simulation."""

    def test_price_near_bs(self):
        """MC price should be close to BS for European options."""
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        bs_price = black_scholes.price(S, K, T, r, sigma, "call")
        mc_result = monte_carlo.price(S, K, T, r, sigma, "call", n_paths=50000, seed=42)
        assert abs(mc_result["price"] - bs_price) / bs_price < 0.02  # Within 2%

    def test_returns_paths(self):
        result = monte_carlo.price(100, 100, 1, 0.05, 0.2, n_paths=100, seed=42)
        assert "paths" in result
        assert len(result["paths"]) > 0

    def test_payoff_distribution(self):
        result = monte_carlo.price(100, 100, 1, 0.05, 0.2, n_paths=1000, seed=42)
        dist = result["payoff_distribution"]
        assert "mean" in dist
        assert "histogram" in dist

    def test_put_price(self):
        result = monte_carlo.price(100, 100, 1, 0.05, 0.2, "put", n_paths=10000, seed=42)
        assert result["price"] > 0


# ─── Greeks Tests ─────────────────────────────────────────────────────────────

class TestGreeks:
    """Tests for Greeks calculator."""

    def test_analytical_vs_numerical(self):
        """Analytical and numerical Greeks should be close."""
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        a = greeks.analytical(S, K, T, r, sigma, "call")
        n = greeks.numerical(S, K, T, r, sigma, "call")

        for key in ["delta", "gamma", "vega", "rho"]:
            if abs(a[key]) > 1e-6:
                rel_diff = abs(a[key] - n[key]) / abs(a[key])
                assert rel_diff < 0.05, f"{key}: analytical={a[key]}, numerical={n[key]}"

    def test_greeks_vs_spot(self):
        result = greeks.greeks_vs_spot(100, 100, 1, 0.05, 0.2)
        assert len(result["spot_prices"]) == 50
        assert len(result["delta"]) == 50


# ─── Implied Volatility Tests ────────────────────────────────────────────────

class TestImpliedVol:
    """Tests for IV solver."""

    def test_round_trip(self):
        """Price with sigma → solve IV → should recover sigma."""
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.3
        market_price = black_scholes.price(S, K, T, r, sigma, "call")
        result = implied_vol.solve(market_price, S, K, T, r, "call")
        assert result["converged"]
        assert abs(result["implied_vol"] - sigma) < 1e-4

    def test_bisection_fallback(self):
        result = implied_vol.solve_bisection(
            10.0, 100, 100, 1, 0.05, "call"
        )
        assert "implied_vol" in result

    def test_volatility_surface(self):
        surface = implied_vol.volatility_surface(100, 0.05)
        assert "strikes" in surface
        assert "maturities" in surface
        assert "iv_matrix" in surface
        assert len(surface["iv_matrix"]) == len(surface["maturities"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
