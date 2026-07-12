"""
app/models/__init__.py

Purpose:
    Re-exports all SQLAlchemy models from a single import point.

Reason:
    Allows `from app.models import Vehicle, Driver, Trip` etc.
    Also exposes `Base` for init_db() and reset_database().
"""

from app.models.base import Base
from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import MaintenanceLog
from app.models.fuel_log import FuelLog
from app.models.expense import Expense

__all__ = [
    "Base",
    "Role",
    "User",
    "Vehicle",
    "Driver",
    "Trip",
    "MaintenanceLog",
    "FuelLog",
    "Expense",
]
