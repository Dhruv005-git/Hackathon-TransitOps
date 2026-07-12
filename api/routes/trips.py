from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.services import trip_service
from app.schemas.trip_schema import TripCreate, TripComplete, TripResponse
from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TripResponse])
def get_trips(status_filter: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    return trip_service.list_trips(status_filter=status_filter)

@router.post("/", response_model=TripResponse)
def create_trip(trip_in: TripCreate, current_user: dict = Depends(get_current_user)):
    try:
        return trip_service.create_trip(
            trip_code=trip_in.trip_code,
            source=trip_in.source,
            destination=trip_in.destination,
            vehicle_id=trip_in.vehicle_id,
            driver_id=trip_in.driver_id,
            cargo_weight_kg=trip_in.cargo_weight_kg,
            planned_distance_km=trip_in.planned_distance_km,
            revenue=trip_in.revenue
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{trip_id}/dispatch", response_model=TripResponse)
def dispatch_trip(trip_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return trip_service.dispatch_trip(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{trip_id}/complete", response_model=TripResponse)
def complete_trip(trip_id: int, data: TripComplete, current_user: dict = Depends(get_current_user)):
    try:
        return trip_service.complete_trip(trip_id, fuel_consumed_l=data.fuel_consumed_l, final_odometer=data.final_odometer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{trip_id}/cancel", response_model=TripResponse)
def cancel_trip(trip_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return trip_service.cancel_trip(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
