"""
app/services/vehicle_service.py

Purpose:
    Business logic for Vehicle CRUD operations.

Reason:
    Keeps all vehicle-related DB mutations and validation in one place,
    away from the Streamlit UI layer. Each function raises ValueError with
    a human-readable message on validation failure so the UI can display it.
"""

from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.database.engine import get_session
from app.models.vehicle import Vehicle
from app.constants import VehicleStatus


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def list_vehicles(
    search: str = "",
    status_filter: Optional[str] = None,
) -> list[Vehicle]:
    """
    Return all vehicles, optionally filtered by search string and/or status.

    search:        Case-insensitive match against registration_no or model_name.
    status_filter: If provided, only return vehicles with this status.
    """
    with get_session() as session:
        query = session.query(Vehicle)

        if search:
            term = f"%{search.lower()}%"
            query = query.filter(
                (Vehicle.registration_no.ilike(term)) |
                (Vehicle.model_name.ilike(term))
            )

        if status_filter and status_filter != "All":
            query = query.filter(Vehicle.status == status_filter)

        vehicles = query.order_by(Vehicle.registration_no).all()

    return vehicles


def get_vehicle(vehicle_id: int) -> Optional[Vehicle]:
    """Return a single vehicle by PK, or None if not found."""
    with get_session() as session:
        return session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_vehicle(
    registration_no: str,
    model_name: str,
    vehicle_type: str,
    max_capacity_kg: float,
    odometer: float,
    acquisition_cost: float,
    status: str = VehicleStatus.AVAILABLE,
) -> Vehicle:
    """
    Create and persist a new vehicle.

    Raises:
        ValueError: If registration_no already exists or required fields invalid.
    """
    registration_no = registration_no.strip().upper()

    if not registration_no:
        raise ValueError("Registration number cannot be blank.")
    if max_capacity_kg <= 0:
        raise ValueError("Max capacity must be greater than 0.")
    if acquisition_cost < 0:
        raise ValueError("Acquisition cost cannot be negative.")
    if odometer < 0:
        raise ValueError("Odometer cannot be negative.")

    with get_session() as session:
        # Uniqueness check with a friendly error
        existing = (
            session.query(Vehicle)
            .filter(Vehicle.registration_no == registration_no)
            .first()
        )
        if existing:
            raise ValueError(
                f"Registration number '{registration_no}' is already in use."
            )

        vehicle = Vehicle(
            registration_no=registration_no,
            model_name=model_name.strip(),
            type=vehicle_type,
            max_capacity_kg=max_capacity_kg,
            odometer=odometer,
            acquisition_cost=acquisition_cost,
            status=status,
        )
        session.add(vehicle)

    return vehicle


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_vehicle(
    vehicle_id: int,
    *,
    registration_no: Optional[str] = None,
    model_name: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    max_capacity_kg: Optional[float] = None,
    odometer: Optional[float] = None,
    acquisition_cost: Optional[float] = None,
    status: Optional[str] = None,
) -> Vehicle:
    """
    Update an existing vehicle by ID. Only supplied (non-None) fields are changed.

    Raises:
        ValueError: If vehicle not found, or registration_no already taken by another vehicle.
    """
    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")

        if registration_no is not None:
            reg = registration_no.strip().upper()
            conflict = (
                session.query(Vehicle)
                .filter(Vehicle.registration_no == reg, Vehicle.id != vehicle_id)
                .first()
            )
            if conflict:
                raise ValueError(f"Registration number '{reg}' is already in use.")
            vehicle.registration_no = reg

        if model_name is not None:
            vehicle.model_name = model_name.strip()
        if vehicle_type is not None:
            vehicle.type = vehicle_type
        if max_capacity_kg is not None:
            if max_capacity_kg <= 0:
                raise ValueError("Max capacity must be greater than 0.")
            vehicle.max_capacity_kg = max_capacity_kg
        if odometer is not None:
            if odometer < 0:
                raise ValueError("Odometer cannot be negative.")
            vehicle.odometer = odometer
        if acquisition_cost is not None:
            if acquisition_cost < 0:
                raise ValueError("Acquisition cost cannot be negative.")
            vehicle.acquisition_cost = acquisition_cost
        if status is not None:
            vehicle.status = status

    return vehicle


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_vehicle(vehicle_id: int) -> None:
    """
    Permanently delete a vehicle from the registry.

    Raises:
        ValueError: If vehicle not found.
    """
    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")
        session.delete(vehicle)
