
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Booking
from app.schemas import BookingCreate, BookingResponse
from app.services.booking_service import book_seat, cancel_seat
from app.routes.auth import get_current_user, get_admin_user

router = APIRouter(
    prefix="/api/v1/bookings",
    tags=["Bookings"]
)


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return book_seat(
        db=db,
        trip_id=booking_data.trip_id,
        passenger_name=current_user.full_name,
        seat_number=booking_data.seat_number,
        user_id=current_user.id
    )


@router.get("/", response_model=list[BookingResponse])
def get_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(Booking).all()

    return db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).all()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this booking"
        )

    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cancel_seat(
        db=db,
        booking_id=booking_id,
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )
