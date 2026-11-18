from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_search_validation_error():
    # max_followers < min_followers must fail validation
    response = client.post("/api/creators/search", json={
        "min_followers": 100000,
        "max_followers": 10000
    })
    assert response.status_code == 400
