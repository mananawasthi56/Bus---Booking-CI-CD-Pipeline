
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine
from app.models import Bus, Trip, Booking


client = TestClient(app)


@pytest.fixture
def setup_booking_data():
    # Clean existing test records
    db = next(
        __import__("app.database", fromlist=["get_db"]).get_db()
    )

    try:
        db.query(Booking).delete()
        db.query(Trip).delete()
        db.query(Bus).delete()
        db.commit()

        bus = Bus(
            bus_name="Test Volvo",
            bus_number="TEST1001",
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

        yield trip.id

    finally:
        db.close()


def test_successful_booking(setup_booking_data):
    trip_id = setup_booking_data

    response = client.post(
        "/api/v1/bookings/",
        json={
            "passenger_name": "Rahul",
            "seat_number": 1,
            "trip_id": trip_id
        }
    )

    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"


def test_duplicate_seat_booking(setup_booking_data):
    trip_id = setup_booking_data

    booking_data = {
        "passenger_name": "Rahul",
        "seat_number": 2,
        "trip_id": trip_id
    }

    first_response = client.post(
        "/api/v1/bookings/",
        json=booking_data
    )

    second_response = client.post(
        "/api/v1/bookings/",
        json={
            **booking_data,
            "passenger_name": "Amit"
        }
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_invalid_seat_number(setup_booking_data):
    trip_id = setup_booking_data

    response = client.post(
        "/api/v1/bookings/",
        json={
            "passenger_name": "Rahul",
            "seat_number": 50,
            "trip_id": trip_id
        }
    )

    assert response.status_code == 400


def test_booking_cancellation(setup_booking_data):
    trip_id = setup_booking_data

    response = client.post(
        "/api/v1/bookings/",
        json={
            "passenger_name": "Rahul",
            "seat_number": 3,
            "trip_id": trip_id
        }
    )

    booking_id = response.json()["id"]

    cancel_response = client.patch(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


def test_cancelled_seat_can_be_booked_again(setup_booking_data):
    trip_id = setup_booking_data

    first_response = client.post(
        "/api/v1/bookings/",
        json={
            "passenger_name": "Rahul",
            "seat_number": 4,
            "trip_id": trip_id
        }
    )

    booking_id = first_response.json()["id"]

    client.patch(
        f"/api/v1/bookings/{booking_id}/cancel"
    )

    second_response = client.post(
        "/api/v1/bookings/",
        json={
            "passenger_name": "Amit",
            "seat_number": 4,
            "trip_id": trip_id
        }
    )

    assert second_response.status_code == 201
    assert second_response.json()["status"] == "confirmed"
