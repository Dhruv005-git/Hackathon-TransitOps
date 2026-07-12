from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExpenseBase(BaseModel):
    vehicle_id: int
    trip_id: Optional[int] = None
    category: str
    amount: float
    date: date

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int

    class Config:
        from_attributes = True
