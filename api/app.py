"""Minimal FastAPI service for stock-analyzer."""
from __future__ import annotations

from fastapi import FastAPI

from api.routes_health import router as health_router
from api.routes_signals import router as signals_router

app = FastAPI(title="stock-analyzer API", version="0.1.0")

app.include_router(health_router)
app.include_router(signals_router)
