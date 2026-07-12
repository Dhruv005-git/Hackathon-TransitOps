"""
app/models/vehicle.py

Purpose:
    ORM model for the Vehicles table.

Reason:
    Master registry of fleet assets. Status field drives dispatch eligibility
    and maintenance workflows across the entire application.
"""

from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    registration_no: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # Van / Truck / Mini
    max_capacity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    odometer: Mapped[float] = mapped_column(Float, default=0.0)
    acquisition_cost: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Available")  # Available/On Trip/In Shop/Retired

    # Relationships
    trips = relationship("Trip", back_populates="vehicle")
    maintenance_logs = relationship("MaintenanceLog", back_populates="vehicle")
    fuel_logs = relationship("FuelLog", back_populates="vehicle")
    expenses = relationship("Expense", back_populates="vehicle")

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, reg='{self.registration_no}', status='{self.status}')>"
