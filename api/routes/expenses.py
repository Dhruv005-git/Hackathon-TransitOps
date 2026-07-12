from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.engine import get_session
from app.models.expense import Expense
from app.models.vehicle import Vehicle
from app.schemas.expense_schema import ExpenseCreate, ExpenseResponse

from api.routes.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(current_user: dict = Depends(get_current_user)):
    with get_session() as session:
        return session.query(Expense).order_by(Expense.date.desc()).all()

@router.post("/", response_model=ExpenseResponse)
def create_expense(expense_data: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == expense_data.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        new_expense = Expense(**expense_data.model_dump())
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return new_expense
