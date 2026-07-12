from fastapi import APIRouter, Depends
from app.services import analytics_service
from api.routes.auth import get_current_user

router = APIRouter()

from typing import Optional

@router.get("/kpis")
def get_kpis(
    vehicle_type: Optional[str] = None,
    status: Optional[str] = None,
    region: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    return analytics_service.get_dashboard_kpis(vehicle_type, status, region)
