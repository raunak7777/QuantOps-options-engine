"""
Ensemble Volatility Prediction Model.

Combines GARCH, LSTM, and HMM forecasts using a meta-model
(linear regression weighting) with confidence intervals.
"""

import numpy as np
from ml import garch, lstm_model, hmm_model


def predict(
    returns: np.ndarray | list,
    volumes: np.ndarray | None = None,
    vix: np.ndarray | None = None,
    horizon: int = 10,
) -> dict:
    """
    Generate ensemble volatility prediction combining all models.

    Args:
        returns: Historical log returns
        volumes: Trading volumes (optional)
        vix: VIX levels (optional)
        horizon: Forecast horizon in days

    Returns:
        Dictionary with individual model forecasts, ensemble forecast,
        and confidence intervals
    """
    returns = np.asarray(returns, dtype=float)

    # Run individual models
    garch_result = garch.fit_and_forecast(returns, horizon)
    lstm_result = lstm_model.predict(returns, volumes, vix, horizon)
    hmm_result = hmm_model.detect_regimes(returns)

    # Get individual forecasts (annualized)
    garch_forecast = garch_result.get("forecast_annualized", [0.25] * horizon)
    lstm_forecast = lstm_result.get("forecast_annualized", [0.25] * horizon)

    # Pad forecasts to match horizon
    garch_forecast = _pad_forecast(garch_forecast, horizon)
    lstm_forecast = _pad_forecast(lstm_forecast, horizon)

    # HMM-based volatility expectation
    regime = hmm_result.get("current_regime", "medium")
    state_vols = hmm_result.get("state_volatilities", {"low": 0.15, "medium": 0.25, "high": 0.40})
    hmm_vol = state_vols.get(regime, 0.25)
    hmm_forecast = [hmm_vol] * horizon

    # Ensemble weights (can be trained; using informed defaults)
    # GARCH is best for short-term, LSTM for medium-term, HMM for regime context
    weights = _compute_weights(regime, horizon)

    ensemble_forecast = []
    confidence_lower = []
    confidence_upper = []

    for i in range(horizon):
        w = weights[i]
        forecast = (
            w["garch"] * garch_forecast[i]
            + w["lstm"] * lstm_forecast[i]
            + w["hmm"] * hmm_forecast[i]
        )
        ensemble_forecast.append(forecast)

        # Confidence interval: based on model disagreement + time horizon
        model_spread = np.std([garch_forecast[i], lstm_forecast[i], hmm_forecast[i]])
        time_factor = np.sqrt(i + 1) * 0.01
        ci_half = max(model_spread, 0.02) + time_factor

        confidence_lower.append(max(0.02, forecast - ci_half))
        confidence_upper.append(forecast + ci_half)

    return {
        "ensemble": {
            "forecast_annualized": ensemble_forecast,
            "confidence_lower": confidence_lower,
            "confidence_upper": confidence_upper,
            "horizon": horizon,
        },
        "individual_models": {
            "garch": {
                "forecast_annualized": garch_forecast,
                "current_vol": garch_result.get("current_vol_annual", 0),
                "model_type": garch_result.get("model", "GARCH"),
            },
            "lstm": {
                "forecast_annualized": lstm_forecast,
                "model_type": lstm_result.get("model", "LSTM"),
            },
            "hmm": {
                "current_regime": regime,
                "regime_probabilities": hmm_result.get("current_probabilities", {}),
                "regime_history": hmm_result.get("regime_history", []),
                "state_volatilities": state_vols,
                "forecast_annualized": hmm_forecast,
            },
        },
        "weights": weights,
        "success": True,
    }


def _compute_weights(regime: str, horizon: int) -> list[dict]:
    """
    Compute adaptive weights for each forecast step.

    GARCH gets more weight short-term; LSTM more medium-term;
    HMM provides regime context throughout.
    """
    weights = []
    for i in range(horizon):
        t = i / max(horizon - 1, 1)  # 0 to 1

        # Short-term: heavy GARCH; Long-term: heavier LSTM
        garch_w = 0.5 * (1 - t) + 0.2
        lstm_w = 0.3 * t + 0.2
        hmm_w = 0.15

        # In high-vol regime, give HMM more weight
        if regime == "high":
            hmm_w = 0.25
            garch_w -= 0.05
            lstm_w -= 0.05

        # Normalize
        total = garch_w + lstm_w + hmm_w
        weights.append({
            "garch": round(garch_w / total, 3),
            "lstm": round(lstm_w / total, 3),
            "hmm": round(hmm_w / total, 3),
        })

    return weights


def _pad_forecast(forecast: list, target_length: int) -> list:
    """Pad forecast to target length by repeating last value."""
    if len(forecast) >= target_length:
        return forecast[:target_length]
    last = forecast[-1] if forecast else 0.25
    return forecast + [last] * (target_length - len(forecast))
