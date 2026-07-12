from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DriverBase(BaseModel):
    name: str
    license_no: str
    license_category: str
    license_expiry: date
    contact_no: str
    safety_score: float
    status: str

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    license_no: Optional[str] = None
    license_category: Optional[str] = None
    license_expiry: Optional[date] = None
    contact_no: Optional[str] = None
    safety_score: Optional[float] = None
    status: Optional[str] = None

class DriverResponse(DriverBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
