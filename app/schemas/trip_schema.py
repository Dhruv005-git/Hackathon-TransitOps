"""
app/schemas/trip_schema.py — Phase 3
Pydantic schemas for Trip create / complete operations.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator


class TripCreate(BaseModel):
    vehicle_id:          int
    driver_id:           int
    source:              str
    destination:         str
    cargo_description:   str   = ""
    cargo_weight_kg:     float = 0.0
    planned_distance_km: float
    revenue:             float = 0.0

    @field_validator("source", "destination")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Source and destination cannot be empty.")
        return v

    @field_validator("planned_distance_km")
    @classmethod
    def distance_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Planned distance must be greater than 0 km.")
        return v

    @field_validator("cargo_weight_kg")
    @classmethod
    def cargo_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Cargo weight cannot be negative.")
        return v

    @field_validator("revenue")
    @classmethod
    def revenue_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Revenue cannot be negative.")
        return v


class TripUpdate(BaseModel):
    """Only allowed on Draft trips."""
    source:              Optional[str]   = None
    destination:         Optional[str]  = None
    cargo_description:   Optional[str]  = None
    cargo_weight_kg:     Optional[float]= None
    planned_distance_km: Optional[float]= None
    revenue:             Optional[float]= None
    vehicle_id:          Optional[int]  = None
    driver_id:           Optional[int]  = None


class TripComplete(BaseModel):
    """Payload for completing a dispatched trip."""
    fuel_consumed_l:   Optional[float] = None
    final_odometer:    Optional[float] = None

    @field_validator("fuel_consumed_l")
    @classmethod
    def fuel_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Fuel consumed must be greater than 0.")
        return v
