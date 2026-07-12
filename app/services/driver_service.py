"""
app/services/driver_service.py

Purpose:
    All Driver business logic — CRUD operations, status management, filters.

Reason:
    Zero Streamlit imports. Returns plain Python dicts.

Business Rules:
    - License number must be unique
    - Cannot hard-delete a driver with trip history (soft-retire)
    - Safety score < 70 → status flagged as Suspended automatically on update
    - License expiry within 30 days → warning returned in response
"""

from __future__ import annotations
import datetime
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.database.engine import get_session
from app.models import Driver, Trip
from app.constants import DriverStatus, TripStatus
from app.schemas.driver_schema import DriverCreate, DriverUpdate
from app.logger import get_logger

log = get_logger(__name__)

LICENSE_WARN_DAYS = 30   # warn if expiring within this many days
SAFETY_SUSPEND_THRESHOLD = 70.0  # auto-suspend below this score


def _to_dict(d: Driver) -> dict:
    """Convert a Driver ORM object to a plain dict."""
    today = datetime.date.today()
    days_to_expiry = (d.license_expiry - today).days
    return {
        "id":               d.id,
        "name":             d.name,
        "license_no":       d.license_no,
        "license_category": d.license_category,
        "license_expiry":   d.license_expiry,
        "contact_no":       d.contact_no,
        "safety_score":     d.safety_score,
        "status":           d.status,
        # Derived fields for UI convenience
        "license_expired":  days_to_expiry < 0,
        "license_expiring_soon": 0 <= days_to_expiry <= LICENSE_WARN_DAYS,
        "days_to_expiry":   days_to_expiry,
    }


def get_all_drivers(
    status_filter:   Optional[str] = None,
    category_filter: Optional[str] = None,
    name_search:     Optional[str] = None,
) -> list[dict]:
    """Return all drivers, optionally filtered."""
    with get_session() as session:
        q = session.query(Driver)
        if status_filter and status_filter != "All":
            q = q.filter(Driver.status == status_filter)
        if category_filter and category_filter != "All":
            q = q.filter(Driver.license_category == category_filter)
        drivers = q.order_by(Driver.name).all()
        results = [_to_dict(d) for d in drivers]
        if name_search:
            name_search = name_search.lower()
            results = [d for d in results if name_search in d["name"].lower()]
        return results


def get_driver_by_id(driver_id: int) -> Optional[dict]:
    """Return a single driver by ID, or None."""
    with get_session() as session:
        d = session.query(Driver).filter(Driver.id == driver_id).first()
        return _to_dict(d) if d else None


def create_driver(data: DriverCreate) -> dict:
    """
    Create a new driver record.

    Raises:
        ValueError: If license_no already exists.
    """
    with get_session() as session:
        driver = Driver(
            name              = data.name,
            license_no        = data.license_no,
            license_category  = data.license_category,
            license_expiry    = data.license_expiry,
            contact_no        = data.contact_no,
            safety_score      = data.safety_score,
            status            = DriverStatus.AVAILABLE,
        )

        # Auto-suspend if safety score is critically low on creation
        if data.safety_score < SAFETY_SUSPEND_THRESHOLD:
            driver.status = DriverStatus.SUSPENDED
            log.warning(
                "New driver created with low safety score (%.1f) — auto-suspended: %s",
                data.safety_score, data.name,
            )

        session.add(driver)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            raise ValueError(
                f"License number '{data.license_no}' is already registered. "
                "Each driver must have a unique license number."
            )

        log.info("Driver created: name=%s license=%s", driver.name, driver.license_no)
        return _to_dict(driver)


def update_driver(driver_id: int, data: DriverUpdate) -> dict:
    """
    Update a driver's fields. Only non-None fields are changed.

    Business Rule:
        If safety_score drops below threshold, status → Suspended.

    Raises:
        ValueError: If driver not found.
    """
    with get_session() as session:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise ValueError(f"Driver with ID {driver_id} not found.")

        if data.name              is not None: driver.name              = data.name
        if data.license_no        is not None: driver.license_no        = data.license_no
        if data.license_category  is not None: driver.license_category  = data.license_category
        if data.license_expiry    is not None: driver.license_expiry    = data.license_expiry
        if data.contact_no        is not None: driver.contact_no        = data.contact_no
        if data.status            is not None: driver.status            = data.status

        if data.safety_score is not None:
            driver.safety_score = data.safety_score
            if data.safety_score < SAFETY_SUSPEND_THRESHOLD and driver.status == DriverStatus.AVAILABLE:
                driver.status = DriverStatus.SUSPENDED
                log.warning(
                    "Driver safety score dropped below %.0f — auto-suspended: id=%s name=%s",
                    SAFETY_SUSPEND_THRESHOLD, driver.id, driver.name,
                )

        session.flush()
        log.info("Driver updated: id=%s name=%s", driver.id, driver.name)
        return _to_dict(driver)


def delete_driver(driver_id: int) -> str:
    """
    Remove a driver record.

    Business Rule:
        - Active (Dispatched) trips → raise ValueError (block).
        - Any historical trips → soft-retire (status = Off Duty).
        - No trips → hard delete.

    Returns:
        "deleted" or "retired" depending on action taken.
    """
    with get_session() as session:
        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise ValueError(f"Driver with ID {driver_id} not found.")

        trips = session.query(Trip).filter(Trip.driver_id == driver_id).all()

        active = [t for t in trips if t.status == TripStatus.DISPATCHED]
        if active:
            raise ValueError(
                f"Cannot remove driver '{driver.name}': they have {len(active)} "
                "active trip(s) in progress. Complete or cancel those trips first."
            )

        if trips:
            driver.status = DriverStatus.OFF_DUTY
            log.info("Driver retired (has trip history): id=%s name=%s", driver.id, driver.name)
            return "retired"

        session.delete(driver)
        log.info("Driver deleted: id=%s name=%s", driver_id, driver.name)
        return "deleted"


def get_driver_summary() -> dict:
    """Return KPI counts for the Drivers page header."""
    with get_session() as session:
        drivers = session.query(Driver).all()
        today = datetime.date.today()
        return {
            "total":          len(drivers),
            "available":      sum(1 for d in drivers if d.status == DriverStatus.AVAILABLE),
            "on_trip":        sum(1 for d in drivers if d.status == DriverStatus.ON_TRIP),
            "suspended":      sum(1 for d in drivers if d.status == DriverStatus.SUSPENDED),
            "expired_license":sum(1 for d in drivers if d.license_expiry < today),
            "expiring_soon":  sum(
                1 for d in drivers
                if 0 <= (d.license_expiry - today).days <= LICENSE_WARN_DAYS
            ),
        }
