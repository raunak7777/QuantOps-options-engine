import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import router
from config import API_HOST, API_PORT


def _sanitize(obj):
    """Recursively replace NaN/Infinity floats with None for JSON safety."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    return obj


class SafeJSONResponse(JSONResponse):
    """JSONResponse that converts NaN/Infinity to null."""
    def render(self, content) -> bytes:
        return json.dumps(
            _sanitize(content),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="Options Pricing Engine",
    description="Quantitative options pricing platform with AI-driven volatility prediction",
    version="1.0.0",
    default_response_class=SafeJSONResponse,
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "name": "Options Pricing Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/price",
            "POST /api/greeks",
            "POST /api/surface",
            "POST /api/monte-carlo",
            "POST /api/predict-vol",
            "POST /api/implied-vol",
            "GET  /api/health",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)
