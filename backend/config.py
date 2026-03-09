"""Application configuration and settings."""
import os
from dotenv import load_dotenv

load_dotenv()

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Pricing defaults
DEFAULT_MC_PATHS = 10000
DEFAULT_MC_STEPS = 252
DEFAULT_BINOMIAL_STEPS = 200
DEFAULT_RISK_FREE_RATE = 0.05

# ML defaults
LSTM_LOOKBACK = 60
LSTM_EPOCHS = 50
HMM_N_STATES = 3
