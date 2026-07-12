from sqlalchemy import func
from app.database.engine import get_session
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import MaintenanceLog
from app.models.fuel_log import FuelLog
from app.models.expense import Expense

def get_dashboard_kpis(vehicle_type: str = None, status: str = None, region: str = None):
    with get_session() as session:
        # Base Queries
        v_query = session.query(Vehicle)
        t_query = session.query(Trip)
        
        if vehicle_type and vehicle_type != 'All':
            v_query = v_query.filter(Vehicle.type == vehicle_type)
        if status and status != 'All':
            v_query = v_query.filter(Vehicle.status == status)
        
        total_vehicles = v_query.count()
        available_vehicles = v_query.filter(Vehicle.status == "Available").count()
        in_shop_vehicles = v_query.filter(Vehicle.status == "In Shop").count()
        active_vehicles = v_query.filter(Vehicle.status == "On Trip").count()
        
        utilization = (active_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
        
        active_trips = t_query.filter(Trip.status == "Dispatched").count()
        pending_trips = t_query.filter(Trip.status == "Draft").count()
        
        drivers_on_duty = session.query(Driver).filter(Driver.status == "On Trip").count()
        
        # Calculate Operational Costs and ROI
        total_revenue = session.query(func.sum(Trip.revenue)).scalar() or 0.0
        total_maintenance_cost = session.query(func.sum(MaintenanceLog.cost)).scalar() or 0.0
        total_fuel_cost = session.query(func.sum(FuelLog.cost)).scalar() or 0.0
        total_other_expenses = session.query(func.sum(Expense.amount)).scalar() or 0.0
        
        total_acq_cost = session.query(func.sum(Vehicle.acquisition_cost)).scalar() or 0.0
        
        operational_cost = total_maintenance_cost + total_fuel_cost + total_other_expenses
        roi = ((total_revenue - operational_cost) / total_acq_cost * 100) if total_acq_cost > 0 else 0
        
        # Fuel efficiency (Total Distance / Total Fuel)
        completed_trips = session.query(Trip).filter(Trip.status == "Completed").all()
        total_distance = sum([t.planned_distance_km for t in completed_trips])
        total_fuel_l = sum([t.fuel_consumed_l for t in completed_trips if t.fuel_consumed_l])
        fuel_efficiency = (total_distance / total_fuel_l) if total_fuel_l > 0 else 0
        
        return {
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "available_vehicles": available_vehicles,
            "in_shop_vehicles": in_shop_vehicles,
            "utilization_percent": round(utilization, 1),
            "active_trips": active_trips,
            "pending_trips": pending_trips,
            "drivers_on_duty": drivers_on_duty,
            "operational_cost": operational_cost,
            "total_revenue": total_revenue,
            "roi_percent": round(roi, 2),
            "fuel_efficiency_km_l": round(fuel_efficiency, 2)
        }
