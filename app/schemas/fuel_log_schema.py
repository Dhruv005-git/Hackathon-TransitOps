from pydantic import BaseModel
from typing import Optional
from datetime import date

class FuelLogBase(BaseModel):
    vehicle_id: int
    trip_id: Optional[int] = None
    liters: float
    cost: float
    date: date

class FuelLogCreate(FuelLogBase):
    pass

class FuelLogResponse(FuelLogBase):
    id: int

    class Config:
        from_attributes = True
