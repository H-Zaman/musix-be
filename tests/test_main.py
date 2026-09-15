import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_invalid_url():
    response = client.post("/api/jobs", json={"url": "not a url"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid YouTube URL."

def test_valid_youtube_url():
    # Job manager will put this in queue, but we don't really run the worker in this simple test.
    response = client.post("/api/jobs", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["status"] == "queued"
    
def test_job_not_found():
    response = client.get("/api/jobs/fake-id")
    assert response.status_code == 404
