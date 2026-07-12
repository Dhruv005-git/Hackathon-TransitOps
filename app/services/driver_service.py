"""
app/services/driver_service.py

Purpose:
    Business logic for Driver CRUD operations.

Reason:
    Keeps all driver-related DB mutations and validation in one place,
    away from the Streamlit UI layer. License validation and uniqueness
    checks are enforced here so the UI simply displays any ValueError raised.
"""

import datetime
from typing import Optional

from app.database.engine import get_session
from app.models.driver import Driver
from app.constants import DriverStatus


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def list_drivers(
    search: str = "",
    status_filter: Optional[str] = None,
) -> list[Driver]:
    """
    Return all drivers, optionally filtered by search string and/or status.

    search:        Case-insensitive match against name or license_no.
    status_filter: If provided, only return drivers with this status.
    """
    with get_session() as session:
        query = session.query(Driver)

        if search:
            term = f"%{search.lower()}%"
            query = query.filter(
                (Driver.name.ilike(term)) |
                (Driver.license_no.ilike(term))
            )

        if status_filter and status_filter != "All":
            query = query.filter(Driver.status == status_filter)

        drivers = query.order_by(Driver.name).all()

    return drivers


def get_driver(driver_id: int) -> Optional[Driver]:
    """Return a single driver by PK, or None if not found."""
    with get_session() as session:
        return session.query(Driver).filter(Driver.id == driver_id).first()


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_driver(
    name: str,
    license_no: str,
    license_category: str,
    license_expiry: datetime.date,
    contact_no: str,
    safety_score: float = 100.0,
    status: str = DriverStatus.AVAILABLE,
) -> Driver:
    """
    Create and persist a new driver.

    Raises:
        ValueError: If license_no already exists or required fields are invalid.
    """
    name = name.strip()
    license_no = license_no.strip().upper()

    if not name:
        raise ValueError("Driver name cannot be blank.")
    if not license_no:
        raise ValueError("License number cannot be blank.")
    if not contact_no.strip():
        raise ValueError("Contact number cannot be blank.")
    if not (0.0 <= safety_score <= 100.0):
        raise ValueError("Safety score must be between 0 and 100.")
    if license_expiry < datetime.date.today():
        raise ValueError(
            f"License expiry ({license_expiry.strftime('%d %b %Y')}) is already in the past. "
            "Cannot add a driver with an expired license."
        )

    with get_session() as session:
        existing = (
            session.query(Driver)
            .filter(Driver.license_no == license_no)
            .first()
        )
        if existing:
            raise ValueError(
                f"License number '{license_no}' is already registered to another driver."
            )

        driver = Driver(
            name=name,
            license_no=license_no,
            license_category=license_category,
            license_expiry=license_expiry,
            contact_no=contact_no.strip(),
            safety_score=safety_score,
            status=status,
        )
        session.add(driver)

    return driver


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_driver(
    driver_id: int,
    *,
    name: Optional[str] = None,
    license_no: Optional[str] = None,
    license_category: Optional[str] = None,
    license_expiry: Optional[datetime.date] = None,
    contact_no: Optional[str] = None,
    safety_score: Optional[float] = None,
    status: Optional[str] = None,
) -> Driver:
    """
    Update an existing driver by ID. Only supplied (non-None) fields are changed.

    Raises:
        ValueError: If driver not found, license_no taken, or invalid values.
    """
    with get_session() as session:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if driver is None:
            raise ValueError(f"Driver with ID {driver_id} not found.")

        if name is not None:
            if not name.strip():
                raise ValueError("Driver name cannot be blank.")
            driver.name = name.strip()

        if license_no is not None:
            lic = license_no.strip().upper()
            conflict = (
                session.query(Driver)
                .filter(Driver.license_no == lic, Driver.id != driver_id)
                .first()
            )
            if conflict:
                raise ValueError(
                    f"License number '{lic}' is already registered to another driver."
                )
            driver.license_no = lic

        if license_category is not None:
            driver.license_category = license_category

        if license_expiry is not None:
            driver.license_expiry = license_expiry

        if contact_no is not None:
            if not contact_no.strip():
                raise ValueError("Contact number cannot be blank.")
            driver.contact_no = contact_no.strip()

        if safety_score is not None:
            if not (0.0 <= safety_score <= 100.0):
                raise ValueError("Safety score must be between 0 and 100.")
            driver.safety_score = safety_score

        if status is not None:
            driver.status = status

    return driver


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_driver(driver_id: int) -> None:
    """
    Permanently delete a driver from the system.

    Raises:
        ValueError: If driver not found.
    """
    with get_session() as session:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if driver is None:
            raise ValueError(f"Driver with ID {driver_id} not found.")
        session.delete(driver)
