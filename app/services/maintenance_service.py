"""
app/services/maintenance_service.py — Phase 4

Business Rules:
  - Vehicle must NOT be On Trip to log maintenance (can't repair a driving truck)
  - Opening maintenance: Vehicle → In Shop
  - Closing maintenance: Vehicle → Available
  - Only Active logs can be closed
"""
from __future__ import annotations
import datetime
from typing import Optional

from app.database.engine import get_session
from app.models import MaintenanceLog, Vehicle
from app.constants import VehicleStatus, MaintenanceStatus
from app.schemas.maintenance_schema import MaintenanceCreate, MaintenanceClose
from app.logger import get_logger

log = get_logger(__name__)


def _to_dict(m: MaintenanceLog, reg: str = "") -> dict:
    return {
        "id":           m.id,
        "vehicle_id":   m.vehicle_id,
        "vehicle_reg":  reg,
        "service_type": m.service_type,
        "cost":         m.cost,
        "date":         m.date,
        "status":       m.status,
    }


def get_all_logs(status_filter: Optional[str] = None,
                 vehicle_id:    Optional[int]  = None) -> list[dict]:
    with get_session() as s:
        q = s.query(MaintenanceLog)
        if status_filter and status_filter != "All":
            q = q.filter(MaintenanceLog.status == status_filter)
        if vehicle_id:
            q = q.filter(MaintenanceLog.vehicle_id == vehicle_id)
        logs = q.order_by(MaintenanceLog.date.desc()).all()
        v_map = {v.id: v.registration_no for v in s.query(Vehicle).all()}
        return [_to_dict(m, v_map.get(m.vehicle_id, "")) for m in logs]


def log_maintenance(data: MaintenanceCreate) -> dict:
    """
    Create a maintenance record and set vehicle to In Shop.
    Raises ValueError if vehicle is On Trip or already In Shop.
    """
    with get_session() as s:
        vehicle = s.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
        if not vehicle:
            raise ValueError(f"Vehicle ID {data.vehicle_id} not found.")
        if vehicle.status == VehicleStatus.ON_TRIP:
            raise ValueError(
                f"Vehicle '{vehicle.registration_no}' is currently On Trip. "
                "Complete the trip before logging maintenance."
            )
        if vehicle.status == VehicleStatus.IN_SHOP:
            raise ValueError(
                f"Vehicle '{vehicle.registration_no}' is already In Shop. "
                "Close the current maintenance record first."
            )

        record = MaintenanceLog(
            vehicle_id   = data.vehicle_id,
            service_type = data.service_type,
            cost         = data.cost,
            date         = data.date or datetime.date.today(),
            status       = MaintenanceStatus.ACTIVE,
        )
        vehicle.status = VehicleStatus.IN_SHOP
        s.add(record)
        s.flush()
        log.info("Maintenance logged: vehicle=%s service=%s",
                 vehicle.registration_no, data.service_type)
        return _to_dict(record, vehicle.registration_no)


def close_maintenance(log_id: int, data: MaintenanceClose) -> dict:
    """
    Mark a maintenance record as Completed and set vehicle → Available.
    Raises ValueError if already closed.
    """
    with get_session() as s:
        record  = s.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
        if not record:
            raise ValueError(f"Maintenance record ID {log_id} not found.")
        if record.status != MaintenanceStatus.ACTIVE:
            raise ValueError("Only Active maintenance records can be closed.")

        vehicle = s.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()

        if data.actual_cost is not None:
            record.cost = data.actual_cost
        record.status  = MaintenanceStatus.COMPLETED
        if vehicle:
            vehicle.status = VehicleStatus.AVAILABLE

        s.flush()
        reg = vehicle.registration_no if vehicle else ""
        log.info("Maintenance closed: id=%s vehicle=%s", log_id, reg)
        return _to_dict(record, reg)


def get_maintenance_summary() -> dict:
    with get_session() as s:
        logs = s.query(MaintenanceLog).all()
        return {
            "total":    len(logs),
            "active":   sum(1 for m in logs if m.status == MaintenanceStatus.ACTIVE),
            "completed":sum(1 for m in logs if m.status == MaintenanceStatus.COMPLETED),
            "total_cost":sum(m.cost for m in logs),
        }


def get_all_vehicles_for_select() -> list[dict]:
    """Vehicles that can be sent to maintenance (Available or Retired)."""
    with get_session() as s:
        vs = s.query(Vehicle).filter(
            Vehicle.status.in_([VehicleStatus.AVAILABLE, VehicleStatus.RETIRED])
        ).all()
        return [{"id": v.id, "label": f"{v.registration_no} — {v.model_name} [{v.status}]"}
                for v in vs]
