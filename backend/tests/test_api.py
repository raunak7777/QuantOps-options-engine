"""
API endpoint integration tests.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_price_bs(client):
    resp = await client.post("/api/price", json={
        "S": 100, "K": 100, "T": 1, "r": 0.05, "sigma": 0.2,
        "option_type": "call", "model": "black-scholes",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "black_scholes" in data
    assert data["black_scholes"]["price"] > 0


@pytest.mark.anyio
async def test_price_all_models(client):
    resp = await client.post("/api/price", json={
        "S": 100, "K": 100, "T": 1, "r": 0.05, "sigma": 0.2,
        "option_type": "call", "model": "all",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "black_scholes" in data
    assert "binomial" in data
    assert "monte_carlo" in data


@pytest.mark.anyio
async def test_greeks(client):
    resp = await client.post("/api/greeks", json={
        "S": 100, "K": 100, "T": 1, "r": 0.05, "sigma": 0.2,
        "option_type": "call",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "analytical" in data
    assert "chart_data" in data


@pytest.mark.anyio
async def test_surface(client):
    resp = await client.post("/api/surface", json={
        "S": 100, "r": 0.05, "base_sigma": 0.25,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "strikes" in data
    assert "iv_matrix" in data


@pytest.mark.anyio
async def test_monte_carlo(client):
    resp = await client.post("/api/monte-carlo", json={
        "S": 100, "K": 100, "T": 1, "r": 0.05, "sigma": 0.2,
        "option_type": "call", "n_paths": 1000, "seed": 42,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "price" in data
    assert "paths" in data


@pytest.mark.anyio
async def test_implied_vol(client):
    resp = await client.post("/api/implied-vol", json={
        "market_price": 10.45, "S": 100, "K": 100, "T": 1,
        "r": 0.05, "option_type": "call",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "implied_vol" in data


@pytest.mark.anyio
async def test_predict_vol(client):
    resp = await client.post("/api/predict-vol", json={
        "ticker": "AAPL", "horizon": 10,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "ensemble" in data


@pytest.mark.anyio
async def test_invalid_model(client):
    resp = await client.post("/api/price", json={
        "S": 100, "K": 100, "T": 1, "r": 0.05, "sigma": 0.2,
        "option_type": "call", "model": "invalid",
    })
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_validation_error(client):
    resp = await client.post("/api/price", json={
        "S": -100, "K": 100, "T": 1, "sigma": 0.2,
    })
    assert resp.status_code == 422  # Validation error
