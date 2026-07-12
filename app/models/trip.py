"""
app/models/trip.py

Purpose:
    ORM model for the Trips table.

Reason:
    Core operational entity. Each trip links a vehicle + driver to a route,
    tracks cargo weight, distance, revenue, and lifecycle status.
    Revenue field is required for the ROI formula in Analytics.
"""

import datetime

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trip_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=False)
    cargo_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    planned_distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="Draft")  # Draft/Dispatched/Completed/Cancelled
    fuel_consumed_l: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_odometer: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    fuel_logs = relationship("FuelLog", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")

    def __repr__(self) -> str:
        return f"<Trip(id={self.id}, code='{self.trip_code}', status='{self.status}')>"
