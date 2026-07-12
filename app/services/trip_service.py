"""
app/services/trip_service.py — Phase 3

Business Rules enforced:
  - Dispatch: Vehicle must be Available, Driver must be Available,
    license not expired, cargo_weight_kg <= vehicle.max_capacity_kg
  - Dispatch sets Vehicle → On Trip, Driver → On Trip
  - Complete sets Vehicle → Available, Driver → Available
  - Cancel from Dispatched also releases Vehicle + Driver
  - Only Draft trips can be edited or re-dispatched
"""
from __future__ import annotations
import uuid, datetime
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.database.engine import get_session
from app.models import Trip, Vehicle, Driver
from app.constants import TripStatus, VehicleStatus, DriverStatus
from app.schemas.trip_schema import TripCreate, TripUpdate, TripComplete
from app.logger import get_logger

log = get_logger(__name__)


def _trip_code() -> str:
    return f"TRP-{datetime.date.today().strftime('%d%m%y')}-{str(uuid.uuid4())[:6].upper()}"


def _to_dict(t: Trip, vehicles: dict = None, drivers: dict = None) -> dict:
    return {
        "id":                  t.id,
        "trip_code":           t.trip_code,
        "source":              t.source,
        "destination":         t.destination,
        "vehicle_id":          t.vehicle_id,
        "driver_id":           t.driver_id,
        "cargo_weight_kg":     t.cargo_weight_kg,
        "planned_distance_km": t.planned_distance_km,
        "revenue":             t.revenue,
        "status":              t.status,
        "fuel_consumed_l":     t.fuel_consumed_l,
        "final_odometer":      t.final_odometer,
        "created_at":          t.created_at,
        "vehicle_reg":         (vehicles or {}).get(t.vehicle_id, f"#{t.vehicle_id}"),
        "driver_name":         (drivers or {}).get(t.driver_id, f"#{t.driver_id}"),
    }


def _load_lookups(session):
    v_map = {v.id: v.registration_no for v in session.query(Vehicle).all()}
    d_map = {d.id: d.name           for d in session.query(Driver).all()}
    return v_map, d_map


def get_all_trips(status_filter: Optional[str] = None) -> list[dict]:
    with get_session() as s:
        q = s.query(Trip)
        if status_filter and status_filter != "All":
            q = q.filter(Trip.status == status_filter)
        trips = q.order_by(Trip.created_at.desc()).all()
        v_map, d_map = _load_lookups(s)
        return [_to_dict(t, v_map, d_map) for t in trips]


def get_trip_by_id(trip_id: int) -> Optional[dict]:
    with get_session() as s:
        t = s.query(Trip).filter(Trip.id == trip_id).first()
        if not t:
            return None
        v_map, d_map = _load_lookups(s)
        return _to_dict(t, v_map, d_map)


def _validate_dispatch_rules(session, vehicle: Vehicle, driver: Driver,
                              cargo_weight_kg: float) -> None:
    """Shared validation for create + dispatch. Raises ValueError on rule violation."""
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise ValueError(
            f"Vehicle '{vehicle.registration_no}' is not available "
            f"(current status: {vehicle.status}). Only Available vehicles can be dispatched."
        )
    if driver.status != DriverStatus.AVAILABLE:
        raise ValueError(
            f"Driver '{driver.name}' is not available "
            f"(current status: {driver.status}). Only Available drivers can be dispatched."
        )
    if driver.license_expiry < datetime.date.today():
        raise ValueError(
            f"Driver '{driver.name}' has an expired license "
            f"(expired: {driver.license_expiry}). Renew before dispatching."
        )
    if cargo_weight_kg > vehicle.max_capacity_kg:
        raise ValueError(
            f"Cargo weight {cargo_weight_kg:.0f} kg exceeds vehicle capacity "
            f"{vehicle.max_capacity_kg:.0f} kg for '{vehicle.registration_no}'."
        )


def create_trip(data: TripCreate) -> dict:
    """Create a trip in Draft status (no vehicle/driver locking yet)."""
    with get_session() as s:
        vehicle = s.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
        driver  = s.query(Driver).filter(Driver.id == data.driver_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle ID {data.vehicle_id} not found.")
        if not driver:
            raise ValueError(f"Driver ID {data.driver_id} not found.")

        # Soft check at create time (hard check at dispatch)
        if data.cargo_weight_kg > vehicle.max_capacity_kg:
            raise ValueError(
                f"Cargo {data.cargo_weight_kg:.0f} kg exceeds vehicle capacity "
                f"{vehicle.max_capacity_kg:.0f} kg."
            )

        trip = Trip(
            trip_code           = _trip_code(),
            source              = data.source,
            destination         = data.destination,
            vehicle_id          = data.vehicle_id,
            driver_id           = data.driver_id,
            cargo_weight_kg     = data.cargo_weight_kg,
            planned_distance_km = data.planned_distance_km,
            revenue             = data.revenue,
            status              = TripStatus.DRAFT,
        )
        s.add(trip)
        s.flush()
        v_map, d_map = _load_lookups(s)
        log.info("Trip created: code=%s route=%s->%s", trip.trip_code, data.source, data.destination)
        return _to_dict(trip, v_map, d_map)


def update_trip(trip_id: int, data: TripUpdate) -> dict:
    """Edit a Draft trip. Raises if trip is not in Draft status."""
    with get_session() as s:
        trip = s.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip ID {trip_id} not found.")
        if trip.status != TripStatus.DRAFT:
            raise ValueError("Only Draft trips can be edited.")

        if data.source              is not None: trip.source              = data.source
        if data.destination         is not None: trip.destination         = data.destination
        if data.cargo_weight_kg     is not None: trip.cargo_weight_kg     = data.cargo_weight_kg
        if data.planned_distance_km is not None: trip.planned_distance_km = data.planned_distance_km
        if data.revenue             is not None: trip.revenue             = data.revenue
        if data.vehicle_id          is not None: trip.vehicle_id          = data.vehicle_id
        if data.driver_id           is not None: trip.driver_id           = data.driver_id

        s.flush()
        v_map, d_map = _load_lookups(s)
        log.info("Trip updated: id=%s code=%s", trip.id, trip.trip_code)
        return _to_dict(trip, v_map, d_map)


def dispatch_trip(trip_id: int) -> dict:
    """
    Dispatch a Draft trip.
    Validates all business rules, then:
      Trip → Dispatched, Vehicle → On Trip, Driver → On Trip
    """
    with get_session() as s:
        trip    = s.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip ID {trip_id} not found.")
        if trip.status != TripStatus.DRAFT:
            raise ValueError(f"Only Draft trips can be dispatched (current: {trip.status}).")

        vehicle = s.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
        driver  = s.query(Driver).filter(Driver.id == trip.driver_id).first()

        _validate_dispatch_rules(s, vehicle, driver, trip.cargo_weight_kg)

        trip.status    = TripStatus.DISPATCHED
        vehicle.status = VehicleStatus.ON_TRIP
        driver.status  = DriverStatus.ON_TRIP

        s.flush()
        v_map, d_map = _load_lookups(s)
        log.info("Trip dispatched: code=%s vehicle=%s driver=%s",
                 trip.trip_code, vehicle.registration_no, driver.name)
        return _to_dict(trip, v_map, d_map)


def complete_trip(trip_id: int, data: TripComplete) -> dict:
    """
    Complete a Dispatched trip.
    Trip → Completed, Vehicle → Available, Driver → Available
    Optionally records fuel_consumed_l and final_odometer.
    """
    with get_session() as s:
        trip   = s.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip ID {trip_id} not found.")
        if trip.status != TripStatus.DISPATCHED:
            raise ValueError(f"Only Dispatched trips can be completed (current: {trip.status}).")

        vehicle = s.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
        driver  = s.query(Driver).filter(Driver.id == trip.driver_id).first()

        trip.status    = TripStatus.COMPLETED
        vehicle.status = VehicleStatus.AVAILABLE
        driver.status  = DriverStatus.AVAILABLE

        if data.fuel_consumed_l is not None:
            trip.fuel_consumed_l = data.fuel_consumed_l
        if data.final_odometer is not None:
            trip.final_odometer  = data.final_odometer
            vehicle.odometer     = data.final_odometer

        s.flush()
        v_map, d_map = _load_lookups(s)
        log.info("Trip completed: code=%s", trip.trip_code)
        return _to_dict(trip, v_map, d_map)


def cancel_trip(trip_id: int) -> dict:
    """
    Cancel a Draft or Dispatched trip.
    If Dispatched: release Vehicle → Available, Driver → Available
    """
    with get_session() as s:
        trip = s.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip ID {trip_id} not found.")
        if trip.status not in (TripStatus.DRAFT, TripStatus.DISPATCHED):
            raise ValueError(f"Cannot cancel a {trip.status} trip.")

        if trip.status == TripStatus.DISPATCHED:
            vehicle = s.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
            driver  = s.query(Driver).filter(Driver.id == trip.driver_id).first()
            if vehicle: vehicle.status = VehicleStatus.AVAILABLE
            if driver:  driver.status  = DriverStatus.AVAILABLE

        trip.status = TripStatus.CANCELLED
        s.flush()
        v_map, d_map = _load_lookups(s)
        log.info("Trip cancelled: code=%s", trip.trip_code)
        return _to_dict(trip, v_map, d_map)


def get_trip_summary() -> dict:
    with get_session() as s:
        trips = s.query(Trip).all()
        completed = [t for t in trips if t.status == TripStatus.COMPLETED]
        return {
            "total":      len(trips),
            "draft":      sum(1 for t in trips if t.status == TripStatus.DRAFT),
            "dispatched": sum(1 for t in trips if t.status == TripStatus.DISPATCHED),
            "completed":  len(completed),
            "cancelled":  sum(1 for t in trips if t.status == TripStatus.CANCELLED),
            "revenue":    sum(t.revenue for t in completed),
        }


def get_available_vehicles() -> list[dict]:
    """Return only Available vehicles for the dispatch form selector."""
    with get_session() as s:
        vs = s.query(Vehicle).filter(Vehicle.status == VehicleStatus.AVAILABLE).all()
        return [{"id": v.id, "label": f"{v.registration_no} — {v.model_name} "
                                      f"({v.max_capacity_kg:.0f} kg)"} for v in vs]


def get_available_drivers() -> list[dict]:
    """Return only Available drivers with valid licenses for the dispatch form."""
    today = datetime.date.today()
    with get_session() as s:
        ds = s.query(Driver).filter(Driver.status == DriverStatus.AVAILABLE).all()
        return [{"id": d.id,
                 "label": f"{d.name} — {d.license_category} "
                           f"{'[EXPIRED]' if d.license_expiry < today else ''}",
                 "license_expired": d.license_expiry < today}
                for d in ds]
