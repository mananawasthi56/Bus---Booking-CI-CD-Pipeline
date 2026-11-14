
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import User
from app.services.auth_service import hash_password

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
    db = next(get_db())
    email = f"api_test_{uuid.uuid4().hex}@example.com"
    password = "TestPassword123"

    try:
        user = User(
            full_name="API Test User",
            email=email,
            hashed_password=hash_password(password),
            role="customer",
            is_active=True
        )

        db.add(user)
        db.commit()

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )

        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/bookings/",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    finally:
        db.query(User).filter(User.email == email).delete()
        db.commit()
        db.close()
