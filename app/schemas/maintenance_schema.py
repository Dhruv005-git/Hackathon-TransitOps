from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .vehicle_schema import VehicleResponse

class MaintenanceCreate(BaseModel):
    vehicle_id: int
    service_type: str
    cost: float
    date: date

class MaintenanceResponse(MaintenanceCreate):
    id: int
    status: str
    vehicle: Optional[VehicleResponse] = None

    model_config = ConfigDict(from_attributes=True)
