
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Bus, Trip, Booking
from app.routes.auth import get_admin_user


router = APIRouter(
    prefix="/api/v1/admin/dashboard",
    tags=["Admin Dashboard"]
)


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    total_users = db.query(func.count(User.id)).scalar() or 0

    total_buses = db.query(func.count(Bus.id)).scalar() or 0

    total_trips = db.query(func.count(Trip.id)).scalar() or 0

    total_bookings = db.query(
        func.count(Booking.id)
    ).scalar() or 0

    confirmed_bookings = db.query(
        func.count(Booking.id)
    ).filter(
        Booking.status == "confirmed"
    ).scalar() or 0

    cancelled_bookings = db.query(
        func.count(Booking.id)
    ).filter(
        Booking.status == "cancelled"
    ).scalar() or 0

    total_revenue = db.query(
        func.coalesce(func.sum(Trip.fare), 0)
    ).join(
        Booking,
        Booking.trip_id == Trip.id
    ).filter(
        Booking.status == "confirmed"
    ).scalar()

    return {
        "total_users": total_users,
        "total_buses": total_buses,
        "total_trips": total_trips,
        "total_bookings": total_bookings,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "total_revenue": float(total_revenue)
    }
