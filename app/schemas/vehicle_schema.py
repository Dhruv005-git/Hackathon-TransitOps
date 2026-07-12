from typing import Optional
from pydantic import BaseModel, ConfigDict

class VehicleBase(BaseModel):
    registration_no: str
    model_name: str
    type: str
    max_capacity_kg: float
    odometer: float
    acquisition_cost: float
    status: str

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    registration_no: Optional[str] = None
    model_name: Optional[str] = None
    type: Optional[str] = None
    max_capacity_kg: Optional[float] = None
    odometer: Optional[float] = None
    acquisition_cost: Optional[float] = None
    status: Optional[str] = None

class VehicleResponse(VehicleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
