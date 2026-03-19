"""Tests for the FastAPI endpoints."""

from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_db_responds():
    resp = client.get("/health/db")
    assert resp.status_code == 200
    assert "status" in resp.json()


def test_signals_score_200():
    payload = {
        "bars": [
            {"date": "2025-01-01", "open": 100, "high": 110, "low": 95, "close": 105, "volume": 1000},
            {"date": "2025-01-02", "open": 105, "high": 115, "low": 100, "close": 112, "volume": 1500},
            {"date": "2025-01-03", "open": 112, "high": 120, "low": 108, "close": 118, "volume": 2000},
        ]
    }
    resp = client.post("/signals/score", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "date" in body
    assert "score" in body
    assert "bucket" in body
    assert body["bucket"] in ("LOW", "MEDIUM", "HIGH")
    assert "reasons" in body
    assert isinstance(body["reasons"], list)
