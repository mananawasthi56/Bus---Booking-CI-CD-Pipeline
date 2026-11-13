
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models

from app.routes import (
    buses,
    trips,
    seats,
    bookings,
    auth,
    dashboard
)


# CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)


# INITIALIZE APPLICATION
app = FastAPI(
    title="Bus Booking Platform",
    description="Bus Trip and Seat Reservation Platform",
    version="1.0.0"
)


# CORS CONFIGURATION
allowed_origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# REGISTER ROUTERS
app.include_router(auth.router)
app.include_router(buses.router)
app.include_router(trips.router)
app.include_router(seats.router)
app.include_router(bookings.router)
app.include_router(dashboard.router)


# HOME
@app.get("/")
def home():
    return {
        "message": "Bus Booking Platform API is running!",
        "status": "success"
    }


# HEALTH CHECK
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# API INFORMATION
@app.get("/api/v1")
def api_info():
    return {
        "application": "Bus Booking Platform",
        "version": "1.0.0"
    }
