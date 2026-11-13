
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Booking, Trip


def book_seat(
    db: Session,
    trip_id: int,
    passenger_name: str,
    seat_number: int,
    user_id: int
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id
    ).first()

    if not trip:
        raise HTTPException(404, "Trip not found")

    if not passenger_name.strip():
        raise HTTPException(400, "Passenger name cannot be empty")

    if seat_number < 1 or seat_number > trip.bus.total_seats:
        raise HTTPException(400, "Invalid seat number")

    existing_booking = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.seat_number == seat_number,
        Booking.status == "confirmed"
    ).first()

    if existing_booking:
        raise HTTPException(409, "Seat already booked")

    booking = Booking(
        passenger_name=passenger_name.strip(),
        seat_number=seat_number,
        trip_id=trip_id,
        user_id=user_id,
        status="confirmed"
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            "Seat already booked by another user"
        )

    except Exception:
        db.rollback()
        raise HTTPException(500, "Booking failed")


def cancel_seat(
    db: Session,
    booking_id: int,
    user_id: int,
    is_admin: bool = False
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            403,
            "You cannot cancel another user's booking"
        )

    if booking.status == "cancelled":
        raise HTTPException(400, "Booking is already cancelled")

    booking.status = "cancelled"

    try:
        db.commit()
        db.refresh(booking)
        return booking

    except Exception:
        db.rollback()
        raise HTTPException(500, "Cancellation failed")
