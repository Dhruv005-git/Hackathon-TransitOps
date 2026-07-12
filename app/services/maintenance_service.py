import datetime
from sqlalchemy.orm import joinedload
from app.database.engine import get_session
from app.models.maintenance import MaintenanceLog
from app.models.vehicle import Vehicle

def list_maintenance_logs(status_filter: str = None):
    with get_session() as session:
        query = session.query(MaintenanceLog).options(joinedload(MaintenanceLog.vehicle))
        if status_filter and status_filter != "All":
            query = query.filter(MaintenanceLog.status == status_filter)
        return query.order_by(MaintenanceLog.date.desc()).all()

def create_maintenance_log(vehicle_id: int, service_type: str, cost: float, date: datetime.date):
    with get_session() as session:
        vehicle = session.query(Vehicle).get(vehicle_id)
        if not vehicle:
            raise ValueError("Vehicle not found.")
            
        if vehicle.status == "On Trip":
            raise ValueError("Cannot perform maintenance on a vehicle currently On Trip.")
            
        log = MaintenanceLog(
            vehicle_id=vehicle_id,
            service_type=service_type,
            cost=cost,
            date=date,
            status="Active"
        )
        session.add(log)
        
        # Enforce Business Rule: Automatically change status to In Shop
        vehicle.status = "In Shop"
        
        session.commit()
        session.refresh(log)
        return log

def close_maintenance_log(log_id: int):
    with get_session() as session:
        log = session.query(MaintenanceLog).get(log_id)
        if not log:
            raise ValueError("Maintenance log not found.")
            
        if log.status == "Completed":
            raise ValueError("Log is already completed.")
            
        log.status = "Completed"
        
        # Enforce Business Rule: Restore vehicle to Available (unless it was retired)
        vehicle = session.query(Vehicle).get(log.vehicle_id)
        if vehicle.status == "In Shop":
            vehicle.status = "Available"
            
        session.commit()
        session.refresh(log)
        return log
