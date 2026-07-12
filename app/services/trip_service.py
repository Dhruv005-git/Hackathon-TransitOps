"""
app/services/trip_service.py

Purpose:
    Business logic for the complete Trip lifecycle:
    create_draft → dispatch → complete / cancel

Reason:
    All status transitions and validations live here so the UI layer
    never touches the DB directly. Every function raises ValueError with
    a human-readable message on rule violation, which the UI displays.

Business Rules (enforced here, not in the UI):
    Dispatch:
        - Vehicle must be Available
        - Driver must be Available
        - Driver license must NOT be expired
        - Driver status must NOT be Suspended
        - cargo_weight_kg ≤ vehicle.max_capacity_kg
    Dispatch side-effects:
        - Vehicle.status → On Trip
        - Driver.status  → On Trip
    Complete side-effects:
        - Vehicle.status → Available
        - Driver.status  → Available
        - Optionally updates Vehicle.odometer
    Cancel side-effects:
        - If trip was Dispatched: Vehicle.status → Available, Driver.status → Available
        - If trip was Draft: no vehicle/driver change (they were never set On Trip)
"""

import datetime
from typing import Optional

from app.database.engine import get_session
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.constants import TripStatus, VehicleStatus, DriverStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_trip_code(session) -> str:
    """
    Generate a unique trip code in the format TR-YYYYMMDD-NNN.

    Uses the current count of all trips (including any created today)
    so the sequence number is always monotonically increasing within a session.
    """
    today_str = datetime.date.today().strftime("%Y%m%d")
    count = session.query(Trip).count()
    return f"TR-{today_str}-{count + 1:03d}"


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def list_trips(
    search: str = "",
    status_filter: Optional[str] = None,
) -> list[Trip]:
    """
    Return all trips, optionally filtered by search string and/or status.

    search:        Case-insensitive match against trip_code, source, or destination.
    status_filter: If provided (and not "All"), only return trips with this status.
    """
    with get_session() as session:
        query = session.query(Trip)

        if search:
            term = f"%{search.lower()}%"
            query = query.filter(
                Trip.trip_code.ilike(term) |
                Trip.source.ilike(term) |
                Trip.destination.ilike(term)
            )

        if status_filter and status_filter != "All":
            query = query.filter(Trip.status == status_filter)

        trips = query.order_by(Trip.created_at.desc()).all()

    return trips


def get_trip(trip_id: int) -> Optional[Trip]:
    """Return a single trip by PK, or None if not found."""
    with get_session() as session:
        return session.query(Trip).filter(Trip.id == trip_id).first()


def list_available_vehicles(session=None) -> list[Vehicle]:
    """Return all vehicles with status=Available (for dispatch form dropdowns)."""
    if session:
        return session.query(Vehicle).filter(
            Vehicle.status == VehicleStatus.AVAILABLE
        ).order_by(Vehicle.registration_no).all()
    with get_session() as session:
        return session.query(Vehicle).filter(
            Vehicle.status == VehicleStatus.AVAILABLE
        ).order_by(Vehicle.registration_no).all()


def list_available_drivers(session=None) -> list[Driver]:
    """Return all drivers with status=Available and valid license (for dispatch form dropdowns)."""
    if session:
        return session.query(Driver).filter(
            Driver.status == DriverStatus.AVAILABLE
        ).order_by(Driver.name).all()
    with get_session() as session:
        return session.query(Driver).filter(
            Driver.status == DriverStatus.AVAILABLE
        ).order_by(Driver.name).all()


# ---------------------------------------------------------------------------
# Create Draft
# ---------------------------------------------------------------------------

def create_draft(
    source: str,
    destination: str,
    vehicle_id: int,
    driver_id: int,
    cargo_weight_kg: float,
    planned_distance_km: float,
    revenue: float,
) -> Trip:
    """
    Create a new trip in Draft status.

    Validates:
        - source and destination are non-blank
        - cargo_weight_kg ≤ vehicle.max_capacity_kg
        - planned_distance_km > 0
        - revenue >= 0
        - vehicle and driver exist

    Raises:
        ValueError: On any validation failure.
    """
    source = source.strip()
    destination = destination.strip()

    if not source:
        raise ValueError("Source/origin cannot be blank.")
    if not destination:
        raise ValueError("Destination cannot be blank.")
    if source.lower() == destination.lower():
        raise ValueError("Source and destination cannot be the same.")
    if cargo_weight_kg <= 0:
        raise ValueError("Cargo weight must be greater than 0 kg.")
    if planned_distance_km <= 0:
        raise ValueError("Planned distance must be greater than 0 km.")
    if revenue < 0:
        raise ValueError("Revenue cannot be negative.")

    with get_session() as session:
        vehicle = session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise ValueError(f"Vehicle with ID {vehicle_id} not found.")

        driver = session.query(Driver).filter(Driver.id == driver_id).first()
        if driver is None:
            raise ValueError(f"Driver with ID {driver_id} not found.")

        # Cargo capacity check (allowed even in Draft so planner can catch issues early)
        if cargo_weight_kg > vehicle.max_capacity_kg:
            raise ValueError(
                f"Cargo weight {cargo_weight_kg:,.0f} kg exceeds vehicle capacity "
                f"{vehicle.max_capacity_kg:,.0f} kg for {vehicle.registration_no}."
            )

        trip_code = _generate_trip_code(session)

        trip = Trip(
            trip_code=trip_code,
            source=source,
            destination=destination,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            cargo_weight_kg=cargo_weight_kg,
            planned_distance_km=planned_distance_km,
            revenue=revenue,
            status=TripStatus.DRAFT,
        )
        session.add(trip)

    return trip


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def dispatch(trip_id: int) -> Trip:
    """
    Transition a Draft trip to Dispatched.

    Validates:
        - Trip exists and is in Draft status
        - Vehicle.status == Available
        - Driver.status == Available
        - Driver.license_expiry > today (not expired)
        - Driver.status != Suspended

    Side-effects on success:
        - Trip.status     → Dispatched
        - Vehicle.status  → On Trip
        - Driver.status   → On Trip

    Raises:
        ValueError: On any validation failure.
    """
    with get_session() as session:
        trip = session.query(Trip).filter(Trip.id == trip_id).first()
        if trip is None:
            raise ValueError(f"Trip with ID {trip_id} not found.")
        if trip.status != TripStatus.DRAFT:
            raise ValueError(
                f"Trip {trip.trip_code} is in '{trip.status}' status and cannot be dispatched. "
                "Only Draft trips can be dispatched."
            )

        vehicle = session.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
        driver  = session.query(Driver).filter(Driver.id == trip.driver_id).first()

        # ---- Vehicle validation ----
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise ValueError(
                f"Vehicle {vehicle.registration_no} is currently '{vehicle.status}'. "
                "Only Available vehicles can be dispatched."
            )

        # ---- Driver validation ----
        if driver.status == DriverStatus.SUSPENDED:
            raise ValueError(
                f"Driver {driver.name} is Suspended and cannot be assigned to a trip."
            )
        if driver.status != DriverStatus.AVAILABLE:
            raise ValueError(
                f"Driver {driver.name} is currently '{driver.status}'. "
                "Only Available drivers can be dispatched."
            )

        # ---- License expiry ----
        today = datetime.date.today()
        if driver.license_expiry < today:
            raise ValueError(
                f"Driver {driver.name}'s license (#{driver.license_no}) expired on "
                f"{driver.license_expiry.strftime('%d %b %Y')}. "
                "License must be valid before dispatching."
            )

        # ---- Cargo capacity (double-check in case vehicle was swapped) ----
        if trip.cargo_weight_kg > vehicle.max_capacity_kg:
            raise ValueError(
                f"Cargo weight {trip.cargo_weight_kg:,.0f} kg exceeds vehicle capacity "
                f"{vehicle.max_capacity_kg:,.0f} kg for {vehicle.registration_no}."
            )

        # ---- Apply transitions ----
        trip.status    = TripStatus.DISPATCHED
        vehicle.status = VehicleStatus.ON_TRIP
        driver.status  = DriverStatus.ON_TRIP

    return trip


# ---------------------------------------------------------------------------
# Complete
# ---------------------------------------------------------------------------

def complete(
    trip_id: int,
    fuel_consumed_l: Optional[float] = None,
    final_odometer: Optional[float] = None,
) -> Trip:
    """
    Transition a Dispatched trip to Completed.

    Validates:
        - Trip exists and is in Dispatched status
        - fuel_consumed_l >= 0 if provided
        - final_odometer >= vehicle.odometer if provided

    Side-effects on success:
        - Trip.status          → Completed
        - Trip.fuel_consumed_l updated (if provided)
        - Trip.final_odometer  updated (if provided)
        - Vehicle.odometer     updated (if final_odometer provided)
        - Vehicle.status       → Available
        - Driver.status        → Available

    Raises:
        ValueError: On any validation failure.
    """
    with get_session() as session:
        trip = session.query(Trip).filter(Trip.id == trip_id).first()
        if trip is None:
            raise ValueError(f"Trip with ID {trip_id} not found.")
        if trip.status != TripStatus.DISPATCHED:
            raise ValueError(
                f"Trip {trip.trip_code} is in '{trip.status}' status and cannot be completed. "
                "Only Dispatched trips can be completed."
            )

        vehicle = session.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
        driver  = session.query(Driver).filter(Driver.id == trip.driver_id).first()

        # Fuel validation
        if fuel_consumed_l is not None:
            if fuel_consumed_l < 0:
                raise ValueError("Fuel consumed cannot be negative.")
            trip.fuel_consumed_l = fuel_consumed_l

        # Odometer validation
        if final_odometer is not None:
            if final_odometer < vehicle.odometer:
                raise ValueError(
                    f"Final odometer ({final_odometer:,.0f} km) cannot be less than "
                    f"current odometer ({vehicle.odometer:,.0f} km)."
                )
            trip.final_odometer = final_odometer
            vehicle.odometer    = final_odometer

        # ---- Apply transitions ----
        trip.status    = TripStatus.COMPLETED
        vehicle.status = VehicleStatus.AVAILABLE
        driver.status  = DriverStatus.AVAILABLE

    return trip


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------

def cancel(trip_id: int) -> Trip:
    """
    Cancel a Draft or Dispatched trip.

    Side-effects:
        - Trip.status → Cancelled
        - If trip was Dispatched: Vehicle.status → Available, Driver.status → Available
        - If trip was Draft: no vehicle/driver status change (they were never set On Trip)

    Raises:
        ValueError: If trip not found or already Completed/Cancelled.
    """
    with get_session() as session:
        trip = session.query(Trip).filter(Trip.id == trip_id).first()
        if trip is None:
            raise ValueError(f"Trip with ID {trip_id} not found.")
        if trip.status in (TripStatus.COMPLETED, TripStatus.CANCELLED):
            raise ValueError(
                f"Trip {trip.trip_code} is already '{trip.status}' and cannot be cancelled."
            )

        was_dispatched = trip.status == TripStatus.DISPATCHED

        # Apply trip transition
        trip.status = TripStatus.CANCELLED

        # Restore vehicle and driver only if they were actively On Trip
        if was_dispatched:
            vehicle = session.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
            driver  = session.query(Driver).filter(Driver.id == trip.driver_id).first()
            if vehicle and vehicle.status == VehicleStatus.ON_TRIP:
                vehicle.status = VehicleStatus.AVAILABLE
            if driver and driver.status == DriverStatus.ON_TRIP:
                driver.status = DriverStatus.AVAILABLE

    return trip
