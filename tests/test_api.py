
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_info():
    response = client.get("/api/v1")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_get_buses():
    response = client.get("/api/v1/buses/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_trips():
    response = client.get("/api/v1/trips/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_bookings():
    response = client.get("/api/v1/bookings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
