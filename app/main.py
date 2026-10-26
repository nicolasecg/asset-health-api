"""Asset Health API: a small inventory/lifecycle service for industrial assets."""
import json
import os
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException

APP_ENV = os.getenv("APP_ENV", "dev")          # comes from a Kubernetes ConfigMap
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DATA_FILE = Path(__file__).parent / "assets.json"

# Lifecycle statuses that represent an obsolescence risk
RISK_STATUSES = {"END OF LIFE", "DISCONTINUED"}

app = FastAPI(title="Asset Health API", version=APP_VERSION)


def load_assets() -> list[dict]:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def risk_level(asset: dict) -> str:
    """Simple rule to classify the risk of an asset."""
    if asset["lifecycle"] in RISK_STATUSES and asset["stock"] == 0:
        return "HIGH"
    if asset["lifecycle"] in RISK_STATUSES or asset["stock"] == 0:
        return "MEDIUM"
    return "LOW"


@app.get("/")
def root():
    return {"service": "asset-health-api", "env": APP_ENV, "version": APP_VERSION}


@app.get("/health")
def health():
    """Liveness probe: is the process alive?"""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Readiness probe: can the app serve traffic (data file readable)?"""
    try:
        load_assets()
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=503, detail="data not available")
    return {"status": "ready"}


@app.get("/assets")
def list_assets(lifecycle: str | None = None):
    assets = load_assets()
    if lifecycle:
        assets = [a for a in assets if a["lifecycle"] == lifecycle.upper()]
    return [{**a, "risk": risk_level(a)} for a in assets]


@app.get("/assets/summary")
def summary():
    assets = load_assets()
    return {
        "total_assets": len(assets),
        "by_lifecycle": Counter(a["lifecycle"] for a in assets),
        "by_risk": Counter(risk_level(a) for a in assets),
        "out_of_stock": [a["id"] for a in assets if a["stock"] == 0],
    }


@app.get("/assets/{asset_id}")
def get_asset(asset_id: str):
    for a in load_assets():
        if a["id"] == asset_id.upper():
            return {**a, "risk": risk_level(a)}
    raise HTTPException(status_code=404, detail=f"asset {asset_id} not found")
