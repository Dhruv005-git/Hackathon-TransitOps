"""
app/models/fuel_log.py

Purpose:
    ORM model for the Fuel Logs table.

Reason:
    Tracks fuel consumption per vehicle (optionally linked to a trip).
    Feeds operational cost calculation and fuel efficiency analytics.
"""

import datetime

from sqlalchemy import Integer, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    trip_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trips.id"), nullable=True)
    liters: Mapped[float] = mapped_column(Float, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    trip = relationship("Trip", back_populates="fuel_logs")

    def __repr__(self) -> str:
        return f"<FuelLog(id={self.id}, vehicle_id={self.vehicle_id}, liters={self.liters})>"
