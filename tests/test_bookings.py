
from datetime import datetime, timedelta
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models import Bus, Trip, Booking, User


client = TestClient(app)


@pytest.fixture
def setup_booking_data():
    db = next(get_db())

    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "TestPassword123"

    try:
        user = User(
            full_name="Test User",
            email=email,
            hashed_password="",
            role="customer",
            is_active=True
        )

        from app.services.auth_service import hash_password
        user.hashed_password = hash_password(password)

        db.add(user)
        db.commit()
        db.refresh(user)

        bus = Bus(
            bus_name="Test Volvo",
            bus_number=f"TEST{uuid.uuid4().hex[:8]}",
            total_seats=40
        )

        db.add(bus)
        db.commit()
        db.refresh(bus)

        trip = Trip(
            source="Delhi",
            destination="Chandigarh",
            departure_time=datetime.now() + timedelta(days=1),
            fare=500,
            bus_id=bus.id
        )

        db.add(trip)
        db.commit()
        db.refresh(trip)

        yield {
            "trip_id": trip.id,
            "user_id": user.id,
            "email": email,
            "password": password
        }

    finally:
        db.close()


@pytest.fixture
def auth_headers(setup_booking_data):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": setup_booking_data["email"],
            "password": setup_booking_data["password"]
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_successful_booking(setup_booking_data, auth_headers):
    response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json={
            "seat_number": 1,
            "trip_id": setup_booking_data["trip_id"]
        }
    )

    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"


def test_duplicate_seat_booking(setup_booking_data, auth_headers):
    booking_data = {
        "seat_number": 2,
        "trip_id": setup_booking_data["trip_id"]
    }

    first_response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json=booking_data
    )

    second_response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json=booking_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_invalid_seat_number(setup_booking_data, auth_headers):
    response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json={
            "seat_number": 50,
            "trip_id": setup_booking_data["trip_id"]
        }
    )

    assert response.status_code == 400


def test_booking_cancellation(setup_booking_data, auth_headers):
    response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json={
            "seat_number": 3,
            "trip_id": setup_booking_data["trip_id"]
        }
    )

    assert response.status_code == 201
    booking_id = response.json()["id"]

    cancel_response = client.patch(
        f"/api/v1/bookings/{booking_id}/cancel",
        headers=auth_headers
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


def test_cancelled_seat_can_be_booked_again(
    setup_booking_data, auth_headers
):
    booking_data = {
        "seat_number": 4,
        "trip_id": setup_booking_data["trip_id"]
    }

    first_response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json=booking_data
    )

    assert first_response.status_code == 201

    booking_id = first_response.json()["id"]

    cancel_response = client.patch(
        f"/api/v1/bookings/{booking_id}/cancel",
        headers=auth_headers
    )

    assert cancel_response.status_code == 200

    second_response = client.post(
        "/api/v1/bookings/",
        headers=auth_headers,
        json=booking_data
    )

    assert second_response.status_code == 201
    assert second_response.json()["status"] == "confirmed"
