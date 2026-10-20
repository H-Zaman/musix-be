from fastapi.testclient import TestClient

from app.config import config
from app.main import app

client = TestClient(app)  # no `with`: skip lifespan, no workers needed


def test_api_requires_key_when_configured(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "secret")
    assert client.get("/api/jobs/nope").status_code == 401
    assert client.get("/api/jobs/nope", headers={"x-api-key": "wrong"}).status_code == 401
    # right key gets past the check and reaches the route (unknown job -> 404)
    assert client.get("/api/jobs/nope", headers={"x-api-key": "secret"}).status_code == 404


def test_health_stays_open_and_no_key_means_open(monkeypatch):
    monkeypatch.setattr(config, "API_KEY", "secret")
    assert client.get("/health").status_code == 200
    monkeypatch.setattr(config, "API_KEY", "")
    assert client.get("/api/jobs/nope").status_code == 404
