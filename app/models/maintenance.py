"""
app/models/maintenance.py

Purpose:
    ORM model for the Maintenance Logs table.

Reason:
    Tracks service records per vehicle. Active records flip vehicle
    status to In Shop; closing them restores Available.
"""

import datetime

from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Oil Change, Tyre Replace, etc.
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Active")  # Active / Completed

    # Relationship
    vehicle = relationship("Vehicle", back_populates="maintenance_logs")

    def __repr__(self) -> str:
        return f"<MaintenanceLog(id={self.id}, vehicle_id={self.vehicle_id}, status='{self.status}')>"
