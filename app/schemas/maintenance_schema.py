"""
app/schemas/maintenance_schema.py — Phase 4
"""
from __future__ import annotations
import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

SERVICE_TYPES = ["Oil Change", "Tyre Replacement", "Engine Repair",
                 "Brake Service", "AC Repair", "General Service", "Body Work", "Other"]

class MaintenanceCreate(BaseModel):
    vehicle_id:   int
    service_type: str
    cost:         float
    date:         datetime.date = None  # type: ignore

    def model_post_init(self, __context):
        if self.date is None:
            object.__setattr__(self, "date", datetime.date.today())

    @field_validator("service_type")
    @classmethod
    def service_valid(cls, v: str) -> str:
        if v not in SERVICE_TYPES:
            raise ValueError(f"Service type must be one of: {', '.join(SERVICE_TYPES)}.")
        return v

    @field_validator("cost")
    @classmethod
    def cost_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Cost cannot be negative.")
        return v


class MaintenanceClose(BaseModel):
    """Payload for closing (completing) an active maintenance record."""
    actual_cost: Optional[float] = None

    @field_validator("actual_cost")
    @classmethod
    def cost_non_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Actual cost cannot be negative.")
        return v
