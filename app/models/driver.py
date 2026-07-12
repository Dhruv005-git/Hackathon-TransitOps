"""
app/models/driver.py

Purpose:
    ORM model for the Drivers table.

Reason:
    Driver profiles with license tracking and safety scores.
    Status and license_expiry are key fields for dispatch validation rules.
"""

from sqlalchemy import Integer, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

import datetime


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    license_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    license_category: Mapped[str] = mapped_column(String(10), nullable=False)  # LMV / HMV
    license_expiry: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    contact_no: Mapped[str] = mapped_column(String(20), nullable=False)
    safety_score: Mapped[float] = mapped_column(Float, default=100.0)  # 0-100
    status: Mapped[str] = mapped_column(String(20), default="Available")  # Available/On Trip/Off Duty/Suspended

    # Relationships
    trips = relationship("Trip", back_populates="driver")

    def __repr__(self) -> str:
        return f"<Driver(id={self.id}, name='{self.name}', status='{self.status}')>"
