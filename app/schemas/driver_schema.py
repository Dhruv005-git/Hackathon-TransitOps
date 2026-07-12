"""
app/schemas/driver_schema.py

Purpose:
    Pydantic validation schemas for Driver create and update operations.

Reason:
    Keeps business rule validation (safety score range, license category,
    contact format) out of both the UI and service layer.
"""

from __future__ import annotations
import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.constants import DriverStatus, LicenseCategory


class DriverCreate(BaseModel):
    name:              str
    license_no:        str
    license_category:  str
    license_expiry:    datetime.date
    contact_no:        str
    safety_score:      float = 100.0

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Driver name cannot be empty.")
        return v

    @field_validator("license_no")
    @classmethod
    def license_not_empty(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError("License number cannot be empty.")
        return v

    @field_validator("license_category")
    @classmethod
    def category_valid(cls, v: str) -> str:
        allowed = [c.value for c in LicenseCategory]
        if v not in allowed:
            raise ValueError(f"License category must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("contact_no")
    @classmethod
    def contact_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Contact number cannot be empty.")
        if not v.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise ValueError("Contact number must contain only digits, +, -, and spaces.")
        return v

    @field_validator("safety_score")
    @classmethod
    def score_range(cls, v: float) -> float:
        if not (0.0 <= v <= 100.0):
            raise ValueError("Safety score must be between 0 and 100.")
        return round(v, 1)


class DriverUpdate(BaseModel):
    """All fields optional — only provided fields are updated."""
    name:             Optional[str]            = None
    license_no:       Optional[str]            = None
    license_category: Optional[str]            = None
    license_expiry:   Optional[datetime.date]  = None
    contact_no:       Optional[str]            = None
    safety_score:     Optional[float]          = None
    status:           Optional[str]            = None

    @field_validator("license_category")
    @classmethod
    def category_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [c.value for c in LicenseCategory]
        if v not in allowed:
            raise ValueError(f"License category must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("safety_score")
    @classmethod
    def score_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0.0 <= v <= 100.0):
            raise ValueError("Safety score must be between 0 and 100.")
        return round(v, 1) if v is not None else v

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = [s.value for s in DriverStatus]
        if v not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}.")
        return v
