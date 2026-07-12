"""
app/services/vehicle_service.py

Purpose:
    All Vehicle business logic — CRUD operations, status management, filters.

Reason:
    Zero Streamlit imports. The UI layer calls these functions and receives
    plain Python dicts. Switching UI frameworks later requires no changes here.

Business Rules enforced here (beyond Pydantic):
    - Registration number must be unique (IntegrityError → friendly message)
    - Cannot hard-delete a vehicle that has any trip history (use retire instead)
    - Status change to "In Shop" is only valid if vehicle is not On Trip
"""

from __future__ import annotations
import datetime
from typing import Optional

from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.database.engine import get_session
from app.models import Vehicle, Trip
from app.constants import VehicleStatus, TripStatus
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate
from app.logger import get_logger

log = get_logger(__name__)


def _to_dict(v: Vehicle) -> dict:
    """Convert a Vehicle ORM object to a plain dict."""
    return {
        "id":               v.id,
        "registration_no":  v.registration_no,
        "model_name":       v.model_name,
        "type":             v.type,
        "max_capacity_kg":  v.max_capacity_kg,
        "odometer":         v.odometer,
        "acquisition_cost": v.acquisition_cost,
        "status":           v.status,
    }


def get_all_vehicles(
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> list[dict]:
    """Return all vehicles, optionally filtered by type and/or status."""
    with get_session() as session:
        q = session.query(Vehicle)
        if type_filter and type_filter != "All":
            q = q.filter(Vehicle.type == type_filter)
        if status_filter and status_filter != "All":
            q = q.filter(Vehicle.status == status_filter)
        return [_to_dict(v) for v in q.order_by(Vehicle.registration_no).all()]


def get_vehicle_by_id(vehicle_id: int) -> Optional[dict]:
    """Return a single vehicle by ID, or None if not found."""
    with get_session() as session:
        v = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        return _to_dict(v) if v else None


def create_vehicle(data: VehicleCreate) -> dict:
    """
    Create a new vehicle record.

    Raises:
        ValueError: If registration_no already exists.
    """
    with get_session() as session:
        vehicle = Vehicle(
            registration_no  = data.registration_no,
            model_name       = data.model_name,
            type             = data.type,
            max_capacity_kg  = data.max_capacity_kg,
            acquisition_cost = data.acquisition_cost,
            odometer         = data.odometer,
            status           = VehicleStatus.AVAILABLE,
        )
        session.add(vehicle)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            raise ValueError(
                f"Registration number '{data.registration_no}' is already in use. "
                "Each vehicle must have a unique registration."
            )
        log.info("Vehicle created: reg=%s model=%s", vehicle.registration_no, vehicle.model_name)
        return _to_dict(vehicle)


def update_vehicle(vehicle_id: int, data: VehicleUpdate) -> dict:
    """
    Update a vehicle's fields. Only provided (non-None) fields are changed.

    Raises:
        ValueError: If vehicle not found.
    """
    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")

        if data.model_name       is not None: vehicle.model_name       = data.model_name
        if data.type             is not None: vehicle.type             = data.type
        if data.max_capacity_kg  is not None: vehicle.max_capacity_kg  = data.max_capacity_kg
        if data.acquisition_cost is not None: vehicle.acquisition_cost = data.acquisition_cost
        if data.odometer         is not None: vehicle.odometer         = data.odometer
        if data.status           is not None: vehicle.status           = data.status

        session.flush()
        log.info("Vehicle updated: id=%s reg=%s", vehicle.id, vehicle.registration_no)
        return _to_dict(vehicle)


def delete_vehicle(vehicle_id: int) -> str:
    """
    Delete a vehicle record.

    Business Rule:
        - If the vehicle has any ACTIVE (Dispatched) trips → raise ValueError.
        - If the vehicle has historical trips → retire it instead of hard delete.
        - If no trip history at all → hard delete.

    Returns:
        "deleted" or "retired" depending on action taken.
    """
    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")

        trips = session.query(Trip).filter(Trip.vehicle_id == vehicle_id).all()

        # Block if any active trip
        active = [t for t in trips if t.status == TripStatus.DISPATCHED]
        if active:
            raise ValueError(
                f"Cannot remove vehicle '{vehicle.registration_no}': "
                f"it has {len(active)} active trip(s) in progress. "
                "Complete or cancel those trips first."
            )

        # Soft-delete if has any trip history
        if trips:
            vehicle.status = VehicleStatus.RETIRED
            log.info(
                "Vehicle retired (has trip history): id=%s reg=%s",
                vehicle.id, vehicle.registration_no,
            )
            return "retired"

        # Hard delete — no trip references
        session.delete(vehicle)
        log.info("Vehicle deleted: id=%s reg=%s", vehicle_id, vehicle.registration_no)
        return "deleted"


def get_fleet_summary() -> dict:
    """Return KPI counts for the Fleet page header."""
    with get_session() as session:
        vehicles = session.query(Vehicle).all()
        return {
            "total":     len(vehicles),
            "available": sum(1 for v in vehicles if v.status == VehicleStatus.AVAILABLE),
            "on_trip":   sum(1 for v in vehicles if v.status == VehicleStatus.ON_TRIP),
            "in_shop":   sum(1 for v in vehicles if v.status == VehicleStatus.IN_SHOP),
            "retired":   sum(1 for v in vehicles if v.status == VehicleStatus.RETIRED),
        }
