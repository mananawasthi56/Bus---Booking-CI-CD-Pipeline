
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Index,
    text
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="customer", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_name = Column(String(100), nullable=False)
    bus_number = Column(String(30), unique=True, nullable=False)
    total_seats = Column(Integer, nullable=False)


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    fare = Column(Integer, nullable=False)

    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)

    bus = relationship("Bus", backref="trips")
    bookings = relationship("Booking", back_populates="trip")


class Booking(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        Index(
            "uq_confirmed_trip_seat",
            "trip_id",
            "seat_number",
            unique=True,
            postgresql_where=text("status = 'confirmed'")
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    passenger_name = Column(String(100), nullable=False)
    seat_number = Column(Integer, nullable=False)
    status = Column(String(20), default="confirmed", nullable=False)

    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)

    # Nullable temporarily to preserve existing bookings
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    trip = relationship("Trip", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
