
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bus, Trip
from app.schemas import BusCreate, BusResponse
from app.routes.auth import get_admin_user

router = APIRouter(
    prefix="/api/v1/buses",
    tags=["Buses"]
)


# Create bus - Admin only
@router.post("/", response_model=BusResponse, status_code=201)
def create_bus(
    bus_data: BusCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    existing_bus = db.query(Bus).filter(
        Bus.bus_number == bus_data.bus_number
    ).first()

    if existing_bus:
        raise HTTPException(409, "Bus number already exists")

    new_bus = Bus(**bus_data.model_dump())

    db.add(new_bus)
    db.commit()
    db.refresh(new_bus)

    return new_bus


# Get all buses - Public
@router.get("/", response_model=list[BusResponse])
def get_buses(db: Session = Depends(get_db)):
    return db.query(Bus).all()


# Get single bus - Public
@router.get("/{bus_id}", response_model=BusResponse)
def get_bus(
    bus_id: int,
    db: Session = Depends(get_db)
):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(404, "Bus not found")

    return bus


# Update bus - Admin only
@router.put("/{bus_id}", response_model=BusResponse)
def update_bus(
    bus_id: int,
    bus_data: BusCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(404, "Bus not found")

    duplicate = db.query(Bus).filter(
        Bus.bus_number == bus_data.bus_number,
        Bus.id != bus_id
    ).first()

    if duplicate:
        raise HTTPException(409, "Bus number already exists")

    for key, value in bus_data.model_dump().items():
        setattr(bus, key, value)

    db.commit()
    db.refresh(bus)

    return bus


# Delete bus - Admin only
@router.delete("/{bus_id}")
def delete_bus(
    bus_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user)
):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()

    if not bus:
        raise HTTPException(404, "Bus not found")

    existing_trip = db.query(Trip).filter(
        Trip.bus_id == bus_id
    ).first()

    if existing_trip:
        raise HTTPException(
            409,
            "Cannot delete bus because trips are associated with it"
        )

    db.delete(bus)
    db.commit()

    return {"message": "Bus deleted successfully"}
