"""
app/services/fuel_service.py — Phase 4
Handles FuelLog and Expense creation, retrieval, and analytics aggregation.
"""
from __future__ import annotations
import datetime
from typing import Optional

from app.database.engine import get_session
from app.models import FuelLog, Expense, Vehicle, Trip
from app.constants import VehicleStatus
from app.schemas.fuel_schema import FuelCreate, ExpenseCreate
from app.logger import get_logger

log = get_logger(__name__)


# ── Fuel Logs ──────────────────────────────────────────────────

def _fuel_to_dict(f: FuelLog, reg: str = "") -> dict:
    return {
        "id":         f.id,
        "vehicle_id": f.vehicle_id,
        "vehicle_reg":reg,
        "trip_id":    f.trip_id,
        "liters":     f.liters,
        "cost":       f.cost,
        "cost_per_l": round(f.cost / f.liters, 2) if f.liters > 0 else 0,
        "date":       f.date,
    }


def add_fuel_log(data: FuelCreate) -> dict:
    with get_session() as s:
        vehicle = s.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle ID {data.vehicle_id} not found.")
        if data.trip_id:
            trip = s.query(Trip).filter(Trip.id == data.trip_id).first()
            if not trip:
                raise ValueError(f"Trip ID {data.trip_id} not found.")
            if trip.vehicle_id != data.vehicle_id:
                raise ValueError("Trip does not belong to the selected vehicle.")

        record = FuelLog(
            vehicle_id = data.vehicle_id,
            trip_id    = data.trip_id,
            liters     = data.liters,
            cost       = data.cost,
            date       = data.date or datetime.date.today(),
        )
        s.add(record)
        s.flush()
        log.info("Fuel logged: vehicle=%s liters=%.1f cost=%.0f",
                 vehicle.registration_no, data.liters, data.cost)
        return _fuel_to_dict(record, vehicle.registration_no)


def get_fuel_logs(vehicle_id: Optional[int] = None) -> list[dict]:
    with get_session() as s:
        q = s.query(FuelLog)
        if vehicle_id:
            q = q.filter(FuelLog.vehicle_id == vehicle_id)
        logs = q.order_by(FuelLog.date.desc()).all()
        v_map = {v.id: v.registration_no for v in s.query(Vehicle).all()}
        return [_fuel_to_dict(f, v_map.get(f.vehicle_id, "")) for f in logs]


# ── Expenses ───────────────────────────────────────────────────

def _exp_to_dict(e: Expense, reg: str = "") -> dict:
    return {
        "id":          e.id,
        "vehicle_id":  e.vehicle_id,
        "vehicle_reg": reg,
        "trip_id":     e.trip_id,
        "category":    e.category,
        "amount":      e.amount,
        "date":        e.date,
    }


def add_expense(data: ExpenseCreate) -> dict:
    with get_session() as s:
        vehicle = s.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle ID {data.vehicle_id} not found.")

        record = Expense(
            vehicle_id = data.vehicle_id,
            trip_id    = data.trip_id,
            category   = data.category,
            amount     = data.amount,
            date       = data.date or datetime.date.today(),
        )
        s.add(record)
        s.flush()
        log.info("Expense logged: vehicle=%s cat=%s amount=%.0f",
                 vehicle.registration_no, data.category, data.amount)
        return _exp_to_dict(record, vehicle.registration_no)


def get_expenses(vehicle_id: Optional[int] = None) -> list[dict]:
    with get_session() as s:
        q = s.query(Expense)
        if vehicle_id:
            q = q.filter(Expense.vehicle_id == vehicle_id)
        exps = q.order_by(Expense.date.desc()).all()
        v_map = {v.id: v.registration_no for v in s.query(Vehicle).all()}
        return [_exp_to_dict(e, v_map.get(e.vehicle_id, "")) for e in exps]


# ── Summary ────────────────────────────────────────────────────

def get_cost_summary() -> dict:
    with get_session() as s:
        fuel_logs = s.query(FuelLog).all()
        expenses  = s.query(Expense).all()
        fuel_cost    = sum(f.cost for f in fuel_logs)
        expense_cost = sum(e.amount for e in expenses)
        fuel_liters  = sum(f.liters for f in fuel_logs)

        by_category: dict[str, float] = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0) + e.amount

        return {
            "fuel_cost":    fuel_cost,
            "expense_cost": expense_cost,
            "total_cost":   fuel_cost + expense_cost,
            "fuel_liters":  fuel_liters,
            "by_category":  by_category,
            "fuel_entries": len(fuel_logs),
            "exp_entries":  len(expenses),
        }


def get_all_vehicles_list() -> list[dict]:
    with get_session() as s:
        return [{"id": v.id, "label": f"{v.registration_no} — {v.model_name}",
                 "reg": v.registration_no}
                for v in s.query(Vehicle).order_by(Vehicle.registration_no).all()]


def get_trips_for_vehicle(vehicle_id: int) -> list[dict]:
    """Return Completed trips for a vehicle (for optional fuel log linkage)."""
    with get_session() as s:
        trips = s.query(Trip).filter(
            Trip.vehicle_id == vehicle_id,
            Trip.status == "Completed"
        ).order_by(Trip.created_at.desc()).all()
        return [{"id": t.id, "label": f"{t.trip_code}: {t.source}→{t.destination}"}
                for t in trips]
