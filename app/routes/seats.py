
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip, Booking

router = APIRouter(
    prefix="/api/v1/trips",
    tags=["Seats"]
)


@router.get("/{trip_id}/seats")
def get_seat_availability(
    trip_id: int,
    db: Session = Depends(get_db)
):
    # Find trip
    trip = db.query(Trip).filter(
        Trip.id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    # Get all confirmed bookings
    bookings = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.status == "confirmed"
    ).all()

    booked_seats = sorted(
        [booking.seat_number for booking in bookings]
    )

    # Calculate available seats
    total_seats = trip.bus.total_seats

    available_seats = [
        seat for seat in range(1, total_seats + 1)
        if seat not in booked_seats
    ]

    return {
        "trip_id": trip.id,
        "source": trip.source,
        "destination": trip.destination,
        "bus_name": trip.bus.bus_name,
        "total_seats": total_seats,
        "booked_count": len(booked_seats),
        "available_count": len(available_seats),
        "booked_seats": booked_seats,
        "available_seats": available_seats
    }
