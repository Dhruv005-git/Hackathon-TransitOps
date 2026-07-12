"""
app/database/seed.py

Purpose:
    Seed the database with demo data for all 4 roles, realistic vehicles,
    drivers, and trips matching the mockup's sample data.

Reason:
    The dashboard and all pages need data from the very first run.
    Seed data is carefully crafted to cover all status values so
    validation rules are visibly demonstrable during the demo.
"""

import datetime
import json

from app.logger import get_logger

log = get_logger(__name__)

from app.auth.hashing import hash_password
from app.auth.rbac import PERMISSIONS
from app.database.engine import get_session
from app.models import Role, User, Vehicle, Driver, Trip


def seed_all() -> None:
    """Insert all seed data. Safe to call multiple times (checks for existing data)."""
    with get_session() as session:
        # Skip if data already exists
        if session.query(Role).count() > 0:
            log.debug("Seed data already exists, skipping")
            return

        # --- Roles ---
        roles = {}
        for role_name, perms in PERMISSIONS.items():
            role = Role(name=role_name, permissions_json=json.dumps(perms))
            session.add(role)
            session.flush()
            roles[role_name] = role

        # --- Users ---
        users_data = [
            {"name": "System Admin", "email": "admin@transitops.com", "password": "admin123", "role": "Admin"},
            {"name": "Arjun Mehta", "email": "fleet@transitops.com", "password": "fleet123", "role": "Fleet Manager"},
            {"name": "Priya Sharma", "email": "dispatch@transitops.com", "password": "dispatch123", "role": "Dispatcher"},
            {"name": "Rahul Verma", "email": "safety@transitops.com", "password": "safety123", "role": "Safety Officer"},
            {"name": "Sneha Patel", "email": "finance@transitops.com", "password": "finance123", "role": "Financial Analyst"},
            {"name": "Alex Driver", "email": "driver@transitops.com", "password": "driver123", "role": "Driver"},
        ]

        for u in users_data:
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role_id=roles[u["role"]].id,
                is_active=True,
            )
            session.add(user)

        # --- Vehicles (6 vehicles covering all statuses) ---
        vehicles_data = [
            {"registration_no": "VAN-05", "model_name": "Tata Ace", "type": "Van", "max_capacity_kg": 500.0, "odometer": 24500.0, "acquisition_cost": 450000.0, "status": "Available"},
            {"registration_no": "TRUCK-8", "model_name": "Ashok Leyland", "type": "Truck", "max_capacity_kg": 8000.0, "odometer": 142000.0, "acquisition_cost": 1850000.0, "status": "On Trip"},
            {"registration_no": "MINI-03", "model_name": "Mahindra Bolero", "type": "Mini", "max_capacity_kg": 750.0, "odometer": 67000.0, "acquisition_cost": 680000.0, "status": "Available"},
            {"registration_no": "VAN-12", "model_name": "Maruti Eeco", "type": "Van", "max_capacity_kg": 600.0, "odometer": 35000.0, "acquisition_cost": 520000.0, "status": "In Shop"},
            {"registration_no": "TRUCK-04", "model_name": "Tata 407", "type": "Truck", "max_capacity_kg": 3500.0, "odometer": 98000.0, "acquisition_cost": 1200000.0, "status": "Retired"},
            {"registration_no": "MINI-07", "model_name": "Force Traveller", "type": "Mini", "max_capacity_kg": 1200.0, "odometer": 53000.0, "acquisition_cost": 950000.0, "status": "Available"},
        ]

        vehicles = {}
        for v in vehicles_data:
            vehicle = Vehicle(**v)
            session.add(vehicle)
            session.flush()
            vehicles[v["registration_no"]] = vehicle

        # --- Drivers (5 drivers covering all statuses) ---
        today = datetime.date.today()
        drivers_data = [
            {"name": "Alex", "license_no": "DL-91935", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=365), "contact_no": "9876543210", "safety_score": 96.0, "status": "Available"},
            {"name": "Dev", "license_no": "DL-44022", "license_category": "HMV", "license_expiry": today + datetime.timedelta(days=180), "contact_no": "9876543211", "safety_score": 88.0, "status": "On Trip"},
            {"name": "Sam", "license_no": "DL-87756", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=730), "contact_no": "9876543212", "safety_score": 92.0, "status": "Available"},
            {"name": "Priya", "license_no": "DL-33190", "license_category": "HMV", "license_expiry": today - datetime.timedelta(days=30), "contact_no": "9876543213", "safety_score": 75.0, "status": "Off Duty"},
            {"name": "Rohan", "license_no": "DL-60843", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=90), "contact_no": "9876543214", "safety_score": 64.0, "status": "Suspended"},
        ]

        drivers = {}
        for d in drivers_data:
            driver = Driver(**d)
            session.add(driver)
            session.flush()
            drivers[d["name"]] = driver

        # --- Trips (5 trips covering full lifecycle) ---
        trips_data = [
            {
                "trip_code": "TR001", "source": "Mumbai", "destination": "Pune",
                "vehicle_id": vehicles["VAN-05"].id, "driver_id": drivers["Alex"].id,
                "cargo_weight_kg": 450.0, "planned_distance_km": 150.0, "revenue": 12000.0,
                "status": "Completed", "fuel_consumed_l": 18.0, "final_odometer": 24650.0,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=5),
            },
            {
                "trip_code": "TR002", "source": "Delhi", "destination": "Jaipur",
                "vehicle_id": vehicles["TRUCK-8"].id, "driver_id": drivers["Dev"].id,
                "cargo_weight_kg": 6500.0, "planned_distance_km": 280.0, "revenue": 35000.0,
                "status": "Dispatched", "fuel_consumed_l": None, "final_odometer": None,
                "created_at": datetime.datetime.now() - datetime.timedelta(hours=6),
            },
            {
                "trip_code": "TR003", "source": "Bangalore", "destination": "Chennai",
                "vehicle_id": vehicles["MINI-03"].id, "driver_id": drivers["Sam"].id,
                "cargo_weight_kg": 600.0, "planned_distance_km": 350.0, "revenue": 18000.0,
                "status": "Draft", "fuel_consumed_l": None, "final_odometer": None,
                "created_at": datetime.datetime.now() - datetime.timedelta(hours=2),
            },
            {
                "trip_code": "TR004", "source": "Hyderabad", "destination": "Vizag",
                "vehicle_id": vehicles["VAN-05"].id, "driver_id": drivers["Alex"].id,
                "cargo_weight_kg": 380.0, "planned_distance_km": 620.0, "revenue": 22000.0,
                "status": "Completed", "fuel_consumed_l": 45.0, "final_odometer": 25270.0,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=3),
            },
            {
                "trip_code": "TR005", "source": "Kolkata", "destination": "Patna",
                "vehicle_id": vehicles["MINI-07"].id, "driver_id": drivers["Sam"].id,
                "cargo_weight_kg": 900.0, "planned_distance_km": 530.0, "revenue": 28000.0,
                "status": "Cancelled", "fuel_consumed_l": None, "final_odometer": None,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=1),
            },
        ]

        for t in trips_data:
            trip = Trip(**t)
            session.add(trip)

        # --- Maintenance Logs ---
        from app.models.maintenance import MaintenanceLog
        maintenance_data = [
            {"vehicle_id": vehicles["VAN-12"].id, "service_type": "Engine Tuning", "cost": 15000.0, "date": today, "status": "Active"},
            {"vehicle_id": vehicles["TRUCK-04"].id, "service_type": "Tyre Replacement", "cost": 45000.0, "date": today - datetime.timedelta(days=10), "status": "Completed"},
            {"vehicle_id": vehicles["MINI-03"].id, "service_type": "Oil Change", "cost": 3500.0, "date": today - datetime.timedelta(days=20), "status": "Completed"}
        ]
        
        for m in maintenance_data:
            session.add(MaintenanceLog(**m))

        session.flush() # Flush to ensure Trips and Maintenance Logs get IDs

        # --- Fuel Logs ---
        from app.models.fuel_log import FuelLog
        
        trip1 = session.query(Trip).filter(Trip.trip_code=="TR001").first()
        trip4 = session.query(Trip).filter(Trip.trip_code=="TR004").first()
        
        fuel_data = [
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip1.id, "liters": 18.0, "cost": 1800.0, "date": today - datetime.timedelta(days=5)},
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip4.id, "liters": 45.0, "cost": 4500.0, "date": today - datetime.timedelta(days=3)}
        ]
        
        for f in fuel_data:
            session.add(FuelLog(**f))

        session.flush()

        # --- Expenses ---
        from app.models.expense import Expense
        expense_data = [
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip1.id, "category": "Toll", "amount": 250.0, "date": today - datetime.timedelta(days=5)},
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip4.id, "category": "Toll", "amount": 800.0, "date": today - datetime.timedelta(days=3)},
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip4.id, "category": "Driver Allowance", "amount": 1200.0, "date": today - datetime.timedelta(days=3)},
            {"vehicle_id": vehicles["TRUCK-8"].id, "trip_id": None, "category": "Miscellaneous", "amount": 5000.0, "date": today - datetime.timedelta(days=1)}
        ]
        
        for e in expense_data:
            session.add(Expense(**e))
            
        session.flush()
        
        log.info("Seeded: 6 roles, 6 users, 6 vehicles, 5 drivers, 5 trips, 3 maintenance logs, 2 fuel logs, 4 expenses")
