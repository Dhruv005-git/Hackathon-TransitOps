from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services import vehicle_service
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehicleResponse
from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(
    search: str = "",
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    return vehicle_service.list_vehicles(search=search, status_filter=status_filter)

@router.post("/", response_model=VehicleResponse)
def create_vehicle(
    vehicle_in: VehicleCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        vehicle = vehicle_service.create_vehicle(
            registration_no=vehicle_in.registration_no,
            model_name=vehicle_in.model_name,
            vehicle_type=vehicle_in.type,
            max_capacity_kg=vehicle_in.max_capacity_kg,
            odometer=vehicle_in.odometer,
            acquisition_cost=vehicle_in.acquisition_cost,
            status=vehicle_in.status
        )
        return vehicle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        vehicle = vehicle_service.update_vehicle(
            vehicle_id,
            registration_no=vehicle_in.registration_no,
            model_name=vehicle_in.model_name,
            vehicle_type=vehicle_in.type,
            max_capacity_kg=vehicle_in.max_capacity_kg,
            odometer=vehicle_in.odometer,
            acquisition_cost=vehicle_in.acquisition_cost,
            status=vehicle_in.status
        )
        return vehicle
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        vehicle_service.delete_vehicle(vehicle_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
