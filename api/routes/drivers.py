from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.services import driver_service
from app.schemas.driver_schema import DriverCreate, DriverUpdate, DriverResponse
from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DriverResponse])
def get_drivers(
    search: str = "",
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    return driver_service.get_all_drivers(status_filter=status_filter, name_search=search)

@router.post("/", response_model=DriverResponse)
def create_driver(
    driver_in: DriverCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        driver = driver_service.create_driver(driver_in)
        return driver
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: int,
    driver_in: DriverUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        driver = driver_service.update_driver(driver_id, driver_in)
        return driver
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{driver_id}")
def delete_driver(
    driver_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        driver_service.delete_driver(driver_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
