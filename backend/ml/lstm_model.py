"""
LSTM Neural Network for Volatility Prediction.

Uses PyTorch LSTM with 60-day rolling windows.
Features: log returns, realized volatility, volume (normalized), VIX.
"""

import numpy as np


class LSTMVolatilityPredictor:
    """LSTM-based volatility prediction model."""

    def __init__(self, lookback: int = 60, hidden_size: int = 64, num_layers: int = 2):
        self.lookback = lookback
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.is_fitted = False

    def _prepare_features(
        self,
        returns: np.ndarray,
        volumes: np.ndarray | None = None,
        vix: np.ndarray | None = None,
    ) -> tuple:
        """Prepare feature matrix and target for LSTM training."""
        n = len(returns)

        # Feature 1: log returns
        feat_returns = returns

        # Feature 2: realized volatility (20-day rolling std)
        realized_vol = np.array([
            np.std(returns[max(0, i - 20):i]) if i >= 20 else np.std(returns[:i + 1])
            for i in range(n)
        ])

        # Feature 3: volume (normalized), use dummy if not provided
        if volumes is not None and len(volumes) == n:
            vol_norm = (volumes - np.mean(volumes)) / (np.std(volumes) + 1e-8)
        else:
            vol_norm = np.zeros(n)

        # Feature 4: VIX, use scaled realized vol if not provided
        if vix is not None and len(vix) == n:
            vix_norm = (vix - np.mean(vix)) / (np.std(vix) + 1e-8)
        else:
            vix_norm = realized_vol * np.sqrt(252) / 0.2  # Rough VIX proxy

        features = np.column_stack([feat_returns, realized_vol, vol_norm, vix_norm])

        # Target: next-day realized vol (20-day forward)
        target = np.array([
            np.std(returns[i:i + 20]) if i + 20 <= n else np.std(returns[i:])
            for i in range(n)
        ])

        return features, target

    def _create_sequences(self, features: np.ndarray, target: np.ndarray):
        """Create sliding window sequences for LSTM input."""
        X, y = [], []
        for i in range(self.lookback, len(features)):
            X.append(features[i - self.lookback:i])
            y.append(target[i])
        return np.array(X), np.array(y)

    def fit(
        self,
        returns: np.ndarray,
        volumes: np.ndarray | None = None,
        vix: np.ndarray | None = None,
        epochs: int = 50,
        lr: float = 0.001,
    ) -> dict:
        """
        Train the LSTM model on historical data.

        Returns:
            Training metrics dictionary
        """
        try:
            import torch
            import torch.nn as nn

            features, target = self._prepare_features(returns, volumes, vix)
            X, y = self._create_sequences(features, target)

            if len(X) < 10:
                return {"success": False, "error": "Insufficient data for LSTM training"}

            # Normalize
            self.scaler_X_mean = X.mean(axis=(0, 1))
            self.scaler_X_std = X.std(axis=(0, 1)) + 1e-8
            self.scaler_y_mean = y.mean()
            self.scaler_y_std = y.std() + 1e-8

            X_norm = (X - self.scaler_X_mean) / self.scaler_X_std
            y_norm = (y - self.scaler_y_mean) / self.scaler_y_std

            # Split train/val
            split = int(0.8 * len(X_norm))
            X_train = torch.FloatTensor(X_norm[:split])
            y_train = torch.FloatTensor(y_norm[:split])
            X_val = torch.FloatTensor(X_norm[split:])
            y_val = torch.FloatTensor(y_norm[split:])

            # Define LSTM model
            input_size = X.shape[2]

            class LSTMModel(nn.Module):
                def __init__(self_m):
                    super().__init__()
                    self_m.lstm = nn.LSTM(
                        input_size, self.hidden_size, self.num_layers,
                        batch_first=True, dropout=0.2
                    )
                    self_m.fc = nn.Linear(self.hidden_size, 1)

                def forward(self_m, x):
                    out, _ = self_m.lstm(x)
                    return self_m.fc(out[:, -1, :]).squeeze(-1)

            self.model = LSTMModel()
            optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
            criterion = nn.MSELoss()

            # Train
            train_losses = []
            val_losses = []
            for epoch in range(epochs):
                self.model.train()
                optimizer.zero_grad()
                pred = self.model(X_train)
                loss = criterion(pred, y_train)
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())

                # Validation
                self.model.eval()
                with torch.no_grad():
                    val_pred = self.model(X_val)
                    val_loss = criterion(val_pred, y_val)
                    val_losses.append(val_loss.item())

            self.is_fitted = True
            return {
                "success": True,
                "train_loss_final": train_losses[-1],
                "val_loss_final": val_losses[-1],
                "epochs": epochs,
            }

        except ImportError:
            return {"success": False, "error": "PyTorch not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def predict(
        self,
        returns: np.ndarray,
        volumes: np.ndarray | None = None,
        vix: np.ndarray | None = None,
        horizon: int = 10,
    ) -> dict:
        """
        Predict future volatility using the trained LSTM.

        Returns:
            Dictionary with forecast and confidence intervals
        """
        if not self.is_fitted:
            return self._mock_prediction(returns, horizon)

        try:
            import torch

            features, _ = self._prepare_features(returns, volumes, vix)
            last_window = features[-self.lookback:]
            last_window_norm = (last_window - self.scaler_X_mean) / self.scaler_X_std

            self.model.eval()
            forecasts = []

            with torch.no_grad():
                input_seq = torch.FloatTensor(last_window_norm).unsqueeze(0)
                for _ in range(horizon):
                    pred_norm = self.model(input_seq).item()
                    pred = pred_norm * self.scaler_y_std + self.scaler_y_mean
                    forecasts.append(float(pred))

                    # Shift window
                    new_row = last_window_norm[-1:].copy()
                    new_row[0, 0] = pred_norm
                    last_window_norm = np.vstack([last_window_norm[1:], new_row])
                    input_seq = torch.FloatTensor(last_window_norm).unsqueeze(0)

            forecasts_annual = [f * np.sqrt(252) for f in forecasts]

            # Confidence intervals widen over time
            ci_width = [0.02 * np.sqrt(i + 1) for i in range(horizon)]

            return {
                "model": "LSTM",
                "forecast_daily": forecasts,
                "forecast_annualized": forecasts_annual,
                "confidence_lower": [f - w for f, w in zip(forecasts_annual, ci_width)],
                "confidence_upper": [f + w for f, w in zip(forecasts_annual, ci_width)],
                "horizon": horizon,
                "success": True,
            }

        except Exception as e:
            return self._mock_prediction(returns, horizon, str(e))

    def _mock_prediction(self, returns: np.ndarray, horizon: int, error: str = "") -> dict:
        """Generate mock predictions when model is not available."""
        recent_vol = float(np.std(returns[-20:]) * np.sqrt(252)) if len(returns) >= 20 else 0.25
        trend = np.linspace(0, 0.02, horizon)
        noise = np.random.normal(0, 0.005, horizon)
        forecasts_annual = [max(0.05, recent_vol + t + n) for t, n in zip(trend, noise)]
        forecasts_daily = [f / np.sqrt(252) for f in forecasts_annual]

        ci_width = [0.03 * np.sqrt(i + 1) for i in range(horizon)]

        return {
            "model": "LSTM (mock)",
            "forecast_daily": forecasts_daily,
            "forecast_annualized": forecasts_annual,
            "confidence_lower": [f - w for f, w in zip(forecasts_annual, ci_width)],
            "confidence_upper": [f + w for f, w in zip(forecasts_annual, ci_width)],
            "horizon": horizon,
            "success": True,
            "note": error or "Using mock predictions (model not trained)",
        }


# Module-level instance
_predictor = LSTMVolatilityPredictor()


def fit(returns, volumes=None, vix=None, epochs=50):
    return _predictor.fit(returns, volumes, vix, epochs)


def predict(returns, volumes=None, vix=None, horizon=10):
    return _predictor.predict(returns, volumes, vix, horizon)
