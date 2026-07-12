"""
app/schemas/fuel_schema.py — Phase 4
"""
from __future__ import annotations
import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

EXPENSE_CATEGORIES = ["Toll", "Insurance", "Fine", "Parking", "Loading/Unloading",
                      "Driver Allowance", "Miscellaneous"]

class FuelCreate(BaseModel):
    vehicle_id: int
    trip_id:    Optional[int] = None
    liters:     float
    cost:       float
    date:       datetime.date = None  # type: ignore

    def model_post_init(self, __context):
        if self.date is None:
            object.__setattr__(self, "date", datetime.date.today())

    @field_validator("liters")
    @classmethod
    def liters_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Liters must be greater than 0.")
        return v

    @field_validator("cost")
    @classmethod
    def cost_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Total fuel cost must be greater than 0.")
        return v


class ExpenseCreate(BaseModel):
    vehicle_id: int
    trip_id:    Optional[int] = None
    category:   str
    amount:     float
    date:       datetime.date = None  # type: ignore

    def model_post_init(self, __context):
        if self.date is None:
            object.__setattr__(self, "date", datetime.date.today())

    @field_validator("category")
    @classmethod
    def category_valid(cls, v: str) -> str:
        if v not in EXPENSE_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(EXPENSE_CATEGORIES)}.")
        return v

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0.")
        return v
