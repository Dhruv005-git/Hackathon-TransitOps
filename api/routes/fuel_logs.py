from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.engine import get_session
from app.models.fuel_log import FuelLog
from app.models.vehicle import Vehicle
from app.schemas.fuel_log_schema import FuelLogCreate, FuelLogResponse

from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[FuelLogResponse])
def get_fuel_logs(current_user: dict = Depends(get_current_user)):
    with get_session() as session:
        return session.query(FuelLog).order_by(FuelLog.date.desc()).all()

@router.post("/", response_model=FuelLogResponse)
def create_fuel_log(log_data: FuelLogCreate, current_user: dict = Depends(get_current_user)):
    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == log_data.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        new_log = FuelLog(**log_data.model_dump())
        session.add(new_log)
        session.commit()
        session.refresh(new_log)
        return new_log
