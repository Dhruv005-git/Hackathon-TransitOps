"""
app/models/expense.py

Purpose:
    ORM model for the Expenses table.

Reason:
    Captures non-fuel costs (tolls, misc) per vehicle/trip.
    Combined with fuel and maintenance costs for total operational cost.
"""

import datetime

from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    trip_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trips.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # Toll / Misc
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="expenses")
    trip = relationship("Trip", back_populates="expenses")

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, vehicle_id={self.vehicle_id}, category='{self.category}')>"
