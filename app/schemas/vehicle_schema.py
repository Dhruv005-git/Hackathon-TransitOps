"""
app/schemas/vehicle_schema.py

Purpose:
    Pydantic validation schemas for Vehicle create and update operations.

Reason:
    Business rule validation lives here, not in the UI or service layer.
    The service layer receives a validated schema object — if it arrives,
    it's already clean. The UI catches ValidationError and shows user-friendly messages.
"""

from __future__ import annotations
import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator
from app.constants import VehicleStatus, VehicleType


class VehicleCreate(BaseModel):
    registration_no:  str
    model_name:       str
    type:             str
    max_capacity_kg:  float
    acquisition_cost: float
    odometer:         float = 0.0

    @field_validator("registration_no")
    @classmethod
    def reg_not_empty(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("Registration number cannot be empty.")
        return v

    @field_validator("model_name")
    @classmethod
    def model_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Model name cannot be empty.")
        return v

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: str) -> str:
        allowed = [t.value for t in VehicleType]
        if v not in allowed:
            raise ValueError(f"Vehicle type must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("max_capacity_kg")
    @classmethod
    def capacity_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Max capacity must be greater than 0 kg.")
        return v

    @field_validator("acquisition_cost")
    @classmethod
    def cost_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Acquisition cost must be greater than 0.")
        return v

    @field_validator("odometer")
    @classmethod
    def odometer_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Odometer reading cannot be negative.")
        return v


class VehicleUpdate(BaseModel):
    """All fields optional — only provided fields are updated."""
    model_name:       Optional[str]   = None
    type:             Optional[str]   = None
    max_capacity_kg:  Optional[float] = None
    acquisition_cost: Optional[float] = None
    odometer:         Optional[float] = None
    status:           Optional[str]   = None

    @field_validator("type")
    @classmethod
    def type_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [t.value for t in VehicleType]
        if v not in allowed:
            raise ValueError(f"Vehicle type must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [s.value for s in VehicleStatus]
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("max_capacity_kg")
    @classmethod
    def capacity_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Max capacity must be greater than 0 kg.")
        return v

    @field_validator("acquisition_cost")
    @classmethod
    def cost_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Acquisition cost must be greater than 0.")
        return v
