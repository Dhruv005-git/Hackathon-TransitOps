"""
app/constants.py

Purpose:
    All status enums and fixed-value constants used across the application.

Reason:
    Replaces magic strings like "Available", "On Trip", "Draft" scattered
    throughout the codebase. Using str-based enums means SQLAlchemy, pandas,
    and Streamlit all accept them without casting, while giving IDE autocomplete
    and preventing typos in Phase 2+ forms.
"""

from enum import Enum


class VehicleStatus(str, Enum):
    AVAILABLE = "Available"
    ON_TRIP   = "On Trip"
    IN_SHOP   = "In Shop"
    RETIRED   = "Retired"


class DriverStatus(str, Enum):
    AVAILABLE = "Available"
    ON_TRIP   = "On Trip"
    OFF_DUTY  = "Off Duty"
    SUSPENDED = "Suspended"


class TripStatus(str, Enum):
    DRAFT      = "Draft"
    DISPATCHED = "Dispatched"
    COMPLETED  = "Completed"
    CANCELLED  = "Cancelled"


class MaintenanceStatus(str, Enum):
    ACTIVE    = "Active"
    COMPLETED = "Completed"


class UserRole(str, Enum):
    FLEET_MANAGER     = "Fleet Manager"
    DISPATCHER        = "Dispatcher"
    SAFETY_OFFICER    = "Safety Officer"
    FINANCIAL_ANALYST = "Financial Analyst"


class VehicleType(str, Enum):
    VAN   = "Van"
    TRUCK = "Truck"
    MINI  = "Mini"


class LicenseCategory(str, Enum):
    LMV = "LMV"
    HMV = "HMV"


# --- UI Color Maps (used by CSS badge classes and Plotly charts) ---
VEHICLE_STATUS_COLORS: dict[str, str] = {
    VehicleStatus.AVAILABLE: "#10b981",
    VehicleStatus.ON_TRIP:   "#f59e0b",
    VehicleStatus.IN_SHOP:   "#ef4444",
    VehicleStatus.RETIRED:   "#6b7280",
}

DRIVER_STATUS_COLORS: dict[str, str] = {
    DriverStatus.AVAILABLE: "#10b981",
    DriverStatus.ON_TRIP:   "#f59e0b",
    DriverStatus.OFF_DUTY:  "#6b7280",
    DriverStatus.SUSPENDED: "#ef4444",
}

TRIP_STATUS_COLORS: dict[str, str] = {
    TripStatus.DRAFT:      "#3b82f6",
    TripStatus.DISPATCHED: "#f59e0b",
    TripStatus.COMPLETED:  "#10b981",
    TripStatus.CANCELLED:  "#ef4444",
}
