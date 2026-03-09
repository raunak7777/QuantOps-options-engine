"""
Hidden Markov Model for Volatility Regime Detection.

Identifies market regimes (low, medium, high volatility) using
Gaussian HMM from the hmmlearn library.
"""

import numpy as np


def detect_regimes(
    returns: np.ndarray | list,
    n_states: int = 3,
) -> dict:
    """
    Fit HMM to returns and detect volatility regimes.

    Args:
        returns: Array of daily log returns
        n_states: Number of hidden states (default 3: low/med/high vol)

    Returns:
        Dictionary with regime labels, probabilities, and parameters
    """
    returns = np.asarray(returns, dtype=float).reshape(-1, 1)

    try:
        from hmmlearn.hmm import GaussianHMM

        model = GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=200,
            random_state=42,
        )
        model.fit(returns)

        # Predict states
        states = model.predict(returns)
        state_probs = model.predict_proba(returns)

        # Sort states by volatility (std of each state)
        state_vols = []
        for i in range(n_states):
            mask = states == i
            if mask.sum() > 0:
                state_vols.append(np.std(returns[mask]))
            else:
                state_vols.append(0.0)

        # Map to ordered labels (low, medium, high vol)
        sorted_indices = np.argsort(state_vols)
        label_map = {}
        labels = ["low", "medium", "high"] if n_states == 3 else [f"state_{i}" for i in range(n_states)]
        for new_idx, old_idx in enumerate(sorted_indices):
            label_map[int(old_idx)] = labels[min(new_idx, len(labels) - 1)]

        regime_labels = [label_map[int(s)] for s in states]
        current_regime = regime_labels[-1]
        current_probs = {label_map[i]: float(state_probs[-1, i]) for i in range(n_states)}

        # Transition matrix (re-ordered)
        trans_matrix = model.transmat_[np.ix_(sorted_indices, sorted_indices)]

        return {
            "model": "HMM",
            "n_states": n_states,
            "current_regime": current_regime,
            "current_probabilities": current_probs,
            "regime_history": regime_labels[-60:],  # Last 60 days
            "state_means": {
                label_map[i]: float(model.means_[i, 0])
                for i in range(n_states)
            },
            "state_volatilities": {
                label_map[i]: float(np.sqrt(model.covars_[i, 0, 0]) * np.sqrt(252))
                for i in range(n_states)
            },
            "transition_matrix": trans_matrix.tolist(),
            "regime_labels": labels[:n_states],
            "success": True,
        }

    except Exception as e:
        return _fallback_regimes(returns.flatten(), n_states, str(e))


def _fallback_regimes(returns: np.ndarray, n_states: int, error_msg: str) -> dict:
    """Fallback regime detection based on rolling volatility percentiles."""
    window = 20
    n = len(returns)
    rolling_vol = np.array([
        np.std(returns[max(0, i - window):i]) * np.sqrt(252)
        for i in range(1, n + 1)
    ])

    # Classify based on percentiles
    p33 = np.percentile(rolling_vol, 33)
    p66 = np.percentile(rolling_vol, 66)

    regime_labels = []
    for v in rolling_vol:
        if v <= p33:
            regime_labels.append("low")
        elif v <= p66:
            regime_labels.append("medium")
        else:
            regime_labels.append("high")

    current_regime = regime_labels[-1]

    return {
        "model": "HMM (fallback - percentile-based)",
        "n_states": n_states,
        "current_regime": current_regime,
        "current_probabilities": {
            "low": 1.0 if current_regime == "low" else 0.0,
            "medium": 1.0 if current_regime == "medium" else 0.0,
            "high": 1.0 if current_regime == "high" else 0.0,
        },
        "regime_history": regime_labels[-60:],
        "state_volatilities": {
            "low": float(np.mean(rolling_vol[rolling_vol <= p33])),
            "medium": float(np.mean(rolling_vol[(rolling_vol > p33) & (rolling_vol <= p66)])),
            "high": float(np.mean(rolling_vol[rolling_vol > p66])),
        },
        "regime_labels": ["low", "medium", "high"],
        "success": True,
        "fallback_reason": error_msg,
    }
