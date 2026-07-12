from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .vehicle_schema import VehicleResponse
from .driver_schema import DriverResponse

class TripCreate(BaseModel):
    trip_code: str
    source: str
    destination: str
    vehicle_id: int
    driver_id: int
    cargo_weight_kg: float
    planned_distance_km: float
    revenue: float

class TripComplete(BaseModel):
    fuel_consumed_l: float
    final_odometer: float

class TripResponse(TripCreate):
    id: int
    status: str
    created_at: datetime
    fuel_consumed_l: Optional[float] = None
    final_odometer: Optional[float] = None
    
    # Include nested relations for UI convenience
    vehicle: Optional[VehicleResponse] = None
    driver: Optional[DriverResponse] = None

    model_config = ConfigDict(from_attributes=True)
