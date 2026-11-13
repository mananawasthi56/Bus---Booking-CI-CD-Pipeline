
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Trip, Bus, Booking
from app.schemas import TripCreate, TripResponse
from app.routes.auth import get_admin_user


router = APIRouter(
    prefix="/api/v1/trips",
    tags=["Trips"]
)


# SEARCH TRIPS
# Keep this route BEFORE /{trip_id}
@router.get("/search", response_model=list[TripResponse])
def search_trips(
    source: str = Query(min_length=2),
    destination: str = Query(min_length=2),
    travel_date: date | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Trip).filter(
        Trip.source.ilike(f"%{source.strip()}%"),
        Trip.destination.ilike(f"%{destination.strip()}%")
    )

    if travel_date:
        start_time = datetime.combine(travel_date, time.min)
        end_time = start_time + timedelta(days=1)

        query = query.filter(
            Trip.departure_time >= start_time,
            Trip.departure_time < end_time
        )

    return (
        query.order_by(Trip.departure_time.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# GET ALL TRIPS
@router.get("/", response_model=list[TripResponse])
def get_all_trips(db: Session = Depends(get_db)):
    return db.query(Trip).order_by(
        Trip.departure_time.asc()
    ).all()


# CREATE TRIP - ADMIN ONLY
@router.post("/", response_model=TripResponse)
def create_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    bus = db.query(Bus).filter(
        Bus.id == trip_data.bus_id
    ).first()

    if not bus:
        raise HTTPException(
            status_code=404,
            detail="Bus not found"
        )

    if trip_data.source.strip().lower() == trip_data.destination.strip().lower():
        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be same"
        )

    if trip_data.fare <= 0:
        raise HTTPException(
            status_code=400,
            detail="Fare must be greater than zero"
        )

    new_trip = Trip(
        source=trip_data.source.strip(),
        destination=trip_data.destination.strip(),
        departure_time=trip_data.departure_time,
        fare=trip_data.fare,
        bus_id=trip_data.bus_id
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return new_trip


# GET TRIP BY ID
@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip


# UPDATE TRIP - ADMIN ONLY
@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int,
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    bus = db.query(Bus).filter(
        Bus.id == trip_data.bus_id
    ).first()

    if not bus:
        raise HTTPException(
            status_code=404,
            detail="Bus not found"
        )

    if trip_data.source.strip().lower() == trip_data.destination.strip().lower():
        raise HTTPException(
            status_code=400,
            detail="Source and destination cannot be same"
        )

    trip.source = trip_data.source.strip()
    trip.destination = trip_data.destination.strip()
    trip.departure_time = trip_data.departure_time
    trip.fare = trip_data.fare
    trip.bus_id = trip_data.bus_id

    db.commit()
    db.refresh(trip)

    return trip


# DELETE TRIP - ADMIN ONLY
@router.delete("/{trip_id}")
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    trip = db.query(Trip).filter(
        Trip.id == trip_id
    ).first()

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    existing_booking = db.query(Booking).filter(
        Booking.trip_id == trip_id
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete trip with existing bookings"
        )

    db.delete(trip)
    db.commit()

    return {"message": "Trip deleted successfully"}
