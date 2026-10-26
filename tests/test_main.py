from fastapi.testclient import TestClient

from app.main import app, risk_level

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready():
    assert client.get("/ready").status_code == 200


def test_filter_by_lifecycle():
    r = client.get("/assets", params={"lifecycle": "discontinued"})
    assert r.status_code == 200
    assert all(a["lifecycle"] == "DISCONTINUED" for a in r.json())


def test_asset_not_found():
    assert client.get("/assets/X-999").status_code == 404


def test_risk_rules():
    assert risk_level({"lifecycle": "DISCONTINUED", "stock": 0}) == "HIGH"
    assert risk_level({"lifecycle": "END OF LIFE", "stock": 3}) == "MEDIUM"
    assert risk_level({"lifecycle": "ACTIVE", "stock": 0}) == "MEDIUM"
    assert risk_level({"lifecycle": "ACTIVE", "stock": 5}) == "LOW"
