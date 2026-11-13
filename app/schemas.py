
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# BUS SCHEMAS

class BusCreate(BaseModel):
    bus_name: str
    bus_number: str
    total_seats: int = Field(gt=0)


class BusResponse(BaseModel):
    id: int
    bus_name: str
    bus_number: str
    total_seats: int

    model_config = ConfigDict(from_attributes=True)


# TRIP SCHEMAS

class TripCreate(BaseModel):
    source: str
    destination: str
    departure_time: datetime
    fare: int = Field(gt=0)
    bus_id: int


class TripResponse(BaseModel):
    id: int
    source: str
    destination: str
    departure_time: datetime
    fare: int
    bus_id: int

    model_config = ConfigDict(from_attributes=True)


# BOOKING SCHEMAS

class BookingCreate(BaseModel):
    seat_number: int = Field(gt=0)
    trip_id: int


class BookingResponse(BaseModel):
    id: int
    passenger_name: str
    seat_number: int
    status: str
    trip_id: int
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


# AUTHENTICATION SCHEMAS

class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ACCOUNT MANAGEMENT SCHEMAS

class UserUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
