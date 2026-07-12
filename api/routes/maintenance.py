from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.services import maintenance_service
from app.schemas.maintenance_schema import MaintenanceCreate, MaintenanceResponse
from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MaintenanceResponse])
def get_logs(status_filter: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    return maintenance_service.list_maintenance_logs(status_filter=status_filter)

@router.post("/", response_model=MaintenanceResponse)
def create_log(log_in: MaintenanceCreate, current_user: dict = Depends(get_current_user)):
    try:
        return maintenance_service.create_maintenance_log(
            vehicle_id=log_in.vehicle_id,
            service_type=log_in.service_type,
            cost=log_in.cost,
            date=log_in.date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{log_id}/close", response_model=MaintenanceResponse)
def close_log(log_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return maintenance_service.close_maintenance_log(log_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
