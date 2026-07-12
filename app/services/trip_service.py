import datetime
from sqlalchemy.orm import joinedload
from app.database.engine import get_session
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver

def list_trips(status_filter: str = None):
    with get_session() as session:
        query = session.query(Trip).options(joinedload(Trip.vehicle), joinedload(Trip.driver))
        if status_filter and status_filter != "All":
            query = query.filter(Trip.status == status_filter)
        return query.order_by(Trip.created_at.desc()).all()

def create_trip(trip_code: str, source: str, destination: str, vehicle_id: int, driver_id: int, cargo_weight_kg: float, planned_distance_km: float, revenue: float):
    with get_session() as session:
        vehicle = session.query(Vehicle).get(vehicle_id)
        driver = session.query(Driver).get(driver_id)
        
        if not vehicle or not driver:
            raise ValueError("Invalid vehicle or driver.")
            
        if vehicle.status != "Available" or driver.status != "Available":
            raise ValueError("Vehicle and Driver must be 'Available' to create a trip.")
            
        if cargo_weight_kg > vehicle.max_capacity_kg:
            raise ValueError(f"Cargo weight ({cargo_weight_kg}kg) exceeds vehicle capacity ({vehicle.max_capacity_kg}kg).")
            
        if driver.license_expiry < datetime.date.today():
            raise ValueError("Driver's license is expired.")
            
        trip = Trip(
            trip_code=trip_code,
            source=source,
            destination=destination,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            cargo_weight_kg=cargo_weight_kg,
            planned_distance_km=planned_distance_km,
            revenue=revenue,
            status="Draft"
        )
        session.add(trip)
        session.commit()
        session.refresh(trip)
        return trip

def dispatch_trip(trip_id: int):
    with get_session() as session:
        trip = session.query(Trip).get(trip_id)
        if not trip:
            raise ValueError("Trip not found.")
        if trip.status != "Draft":
            raise ValueError(f"Cannot dispatch trip in {trip.status} status.")
            
        vehicle = session.query(Vehicle).get(trip.vehicle_id)
        driver = session.query(Driver).get(trip.driver_id)
        
        # Enforce Business Rules
        if vehicle.status != "Available" or driver.status != "Available":
            raise ValueError("Vehicle or Driver is no longer Available.")
            
        trip.status = "Dispatched"
        vehicle.status = "On Trip"
        driver.status = "On Trip"
        
        session.commit()
        session.refresh(trip)
        return trip

def complete_trip(trip_id: int, fuel_consumed_l: float, final_odometer: float):
    with get_session() as session:
        trip = session.query(Trip).get(trip_id)
        if not trip:
            raise ValueError("Trip not found.")
        if trip.status != "Dispatched":
            raise ValueError("Only dispatched trips can be completed.")
            
        vehicle = session.query(Vehicle).get(trip.vehicle_id)
        driver = session.query(Driver).get(trip.driver_id)
        
        trip.status = "Completed"
        trip.fuel_consumed_l = fuel_consumed_l
        trip.final_odometer = final_odometer
        
        # Update vehicle odometer and restore availability
        vehicle.odometer = final_odometer
        vehicle.status = "Available"
        driver.status = "Available"
        
        session.commit()
        session.refresh(trip)
        return trip

def cancel_trip(trip_id: int):
    with get_session() as session:
        trip = session.query(Trip).get(trip_id)
        if not trip:
            raise ValueError("Trip not found.")
            
        if trip.status == "Dispatched":
            vehicle = session.query(Vehicle).get(trip.vehicle_id)
            driver = session.query(Driver).get(trip.driver_id)
            vehicle.status = "Available"
            driver.status = "Available"
            
        trip.status = "Cancelled"
        session.commit()
        session.refresh(trip)
        return trip
