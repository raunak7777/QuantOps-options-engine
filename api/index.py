"""
Vercel serverless function entry point.
Re-exports the FastAPI `app` object so Vercel can serve it.
"""

import sys
import os

# Add the backend directory to sys.path so all backend imports resolve
_backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(_backend_dir))

# Import the FastAPI app – Vercel detects the `app` variable automatically
from main import app  # noqa: E402, F401
