"""
app/database/seed.py

Purpose:
    Seed the database with demo data for all roles, vehicles,
    drivers, and trips to populate Analytics and Dashboard nicely.
"""

import datetime
import json
import random

from app.logger import get_logger

log = get_logger(__name__)

from app.auth.hashing import hash_password
from app.auth.rbac import PERMISSIONS
from app.database.engine import get_session
from app.models import Role, User, Vehicle, Driver, Trip


def seed_all() -> None:
    """Insert all seed data. Safe to call multiple times (checks for existing data)."""
    with get_session() as session:
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

        # --- Vehicles ---
        vehicles_data = [
            {"registration_no": "VAN-05", "model_name": "Tata Ace", "type": "Van", "max_capacity_kg": 500.0, "odometer": 24500.0, "acquisition_cost": 450000.0, "status": "Available"},
            {"registration_no": "TRUCK-8", "model_name": "Ashok Leyland", "type": "Truck", "max_capacity_kg": 8000.0, "odometer": 142000.0, "acquisition_cost": 1850000.0, "status": "On Trip"},
            {"registration_no": "MINI-03", "model_name": "Mahindra Bolero", "type": "Mini", "max_capacity_kg": 750.0, "odometer": 67000.0, "acquisition_cost": 680000.0, "status": "Available"},
            {"registration_no": "VAN-12", "model_name": "Maruti Eeco", "type": "Van", "max_capacity_kg": 600.0, "odometer": 35000.0, "acquisition_cost": 520000.0, "status": "In Shop"},
            {"registration_no": "TRUCK-04", "model_name": "Tata 407", "type": "Truck", "max_capacity_kg": 3500.0, "odometer": 98000.0, "acquisition_cost": 1200000.0, "status": "Retired"},
            {"registration_no": "MINI-07", "model_name": "Force Traveller", "type": "Mini", "max_capacity_kg": 1200.0, "odometer": 53000.0, "acquisition_cost": 950000.0, "status": "Available"},
            {"registration_no": "TRUCK-15", "model_name": "Eicher Pro", "type": "Truck", "max_capacity_kg": 5000.0, "odometer": 88000.0, "acquisition_cost": 1500000.0, "status": "Available"},
            {"registration_no": "VAN-09", "model_name": "Tata Magic", "type": "Van", "max_capacity_kg": 600.0, "odometer": 12000.0, "acquisition_cost": 480000.0, "status": "On Trip"},
            {"registration_no": "MINI-12", "model_name": "Mahindra Supro", "type": "Mini", "max_capacity_kg": 800.0, "odometer": 45000.0, "acquisition_cost": 620000.0, "status": "Available"},
            {"registration_no": "TRUCK-22", "model_name": "Tata Signa", "type": "Truck", "max_capacity_kg": 12000.0, "odometer": 185000.0, "acquisition_cost": 2500000.0, "status": "In Shop"},
        ]

        vehicles = {}
        for v in vehicles_data:
            vehicle = Vehicle(**v)
            session.add(vehicle)
            session.flush()
            vehicles[v["registration_no"]] = vehicle

        # --- Drivers ---
        today = datetime.date.today()
        drivers_data = [
            {"name": "Alex", "license_no": "DL-91935", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=365), "contact_no": "9876543210", "safety_score": 96.0, "status": "Available"},
            {"name": "Dev", "license_no": "DL-44022", "license_category": "HMV", "license_expiry": today + datetime.timedelta(days=180), "contact_no": "9876543211", "safety_score": 88.0, "status": "On Trip"},
            {"name": "Sam", "license_no": "DL-87756", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=730), "contact_no": "9876543212", "safety_score": 92.0, "status": "Available"},
            {"name": "Priya", "license_no": "DL-33190", "license_category": "HMV", "license_expiry": today - datetime.timedelta(days=30), "contact_no": "9876543213", "safety_score": 75.0, "status": "Off Duty"},
            {"name": "Rohan", "license_no": "DL-60843", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=90), "contact_no": "9876543214", "safety_score": 64.0, "status": "Suspended"},
            {"name": "Vikram", "license_no": "DL-11223", "license_category": "HMV", "license_expiry": today + datetime.timedelta(days=400), "contact_no": "9876543215", "safety_score": 98.0, "status": "Available"},
            {"name": "Anjali", "license_no": "DL-44556", "license_category": "LMV", "license_expiry": today + datetime.timedelta(days=200), "contact_no": "9876543216", "safety_score": 85.0, "status": "On Trip"},
            {"name": "Karan", "license_no": "DL-77889", "license_category": "HMV", "license_expiry": today + datetime.timedelta(days=50), "contact_no": "9876543217", "safety_score": 79.0, "status": "Available"},
        ]

        drivers = {}
        for d in drivers_data:
            driver = Driver(**d)
            session.add(driver)
            session.flush()
            drivers[d["name"]] = driver

        # --- Trips ---
        trips_data = [
            {"trip_code": "TR001", "source": "Mumbai", "destination": "Pune", "vehicle_id": vehicles["VAN-05"].id, "driver_id": drivers["Alex"].id, "cargo_weight_kg": 450.0, "planned_distance_km": 150.0, "revenue": 12000.0, "status": "Completed", "fuel_consumed_l": 18.0, "final_odometer": 24650.0, "created_at": datetime.datetime.now() - datetime.timedelta(days=5)},
            {"trip_code": "TR002", "source": "Delhi", "destination": "Jaipur", "vehicle_id": vehicles["TRUCK-8"].id, "driver_id": drivers["Dev"].id, "cargo_weight_kg": 6500.0, "planned_distance_km": 280.0, "revenue": 35000.0, "status": "Dispatched", "fuel_consumed_l": None, "final_odometer": None, "created_at": datetime.datetime.now() - datetime.timedelta(hours=6)},
            {"trip_code": "TR003", "source": "Bangalore", "destination": "Chennai", "vehicle_id": vehicles["MINI-03"].id, "driver_id": drivers["Sam"].id, "cargo_weight_kg": 600.0, "planned_distance_km": 350.0, "revenue": 18000.0, "status": "Draft", "fuel_consumed_l": None, "final_odometer": None, "created_at": datetime.datetime.now() - datetime.timedelta(hours=2)},
            {"trip_code": "TR004", "source": "Hyderabad", "destination": "Vizag", "vehicle_id": vehicles["VAN-05"].id, "driver_id": drivers["Alex"].id, "cargo_weight_kg": 380.0, "planned_distance_km": 620.0, "revenue": 22000.0, "status": "Completed", "fuel_consumed_l": 45.0, "final_odometer": 25270.0, "created_at": datetime.datetime.now() - datetime.timedelta(days=3)},
            {"trip_code": "TR005", "source": "Kolkata", "destination": "Patna", "vehicle_id": vehicles["MINI-07"].id, "driver_id": drivers["Sam"].id, "cargo_weight_kg": 900.0, "planned_distance_km": 530.0, "revenue": 28000.0, "status": "Cancelled", "fuel_consumed_l": None, "final_odometer": None, "created_at": datetime.datetime.now() - datetime.timedelta(days=1)},
            {"trip_code": "TR006", "source": "Ahmedabad", "destination": "Surat", "vehicle_id": vehicles["TRUCK-15"].id, "driver_id": drivers["Vikram"].id, "cargo_weight_kg": 4000.0, "planned_distance_km": 260.0, "revenue": 24000.0, "status": "Completed", "fuel_consumed_l": 30.0, "final_odometer": 88260.0, "created_at": datetime.datetime.now() - datetime.timedelta(days=8)},
            {"trip_code": "TR007", "source": "Indore", "destination": "Bhopal", "vehicle_id": vehicles["VAN-09"].id, "driver_id": drivers["Anjali"].id, "cargo_weight_kg": 500.0, "planned_distance_km": 190.0, "revenue": 14000.0, "status": "Dispatched", "fuel_consumed_l": None, "final_odometer": None, "created_at": datetime.datetime.now() - datetime.timedelta(hours=12)},
            {"trip_code": "TR008", "source": "Lucknow", "destination": "Kanpur", "vehicle_id": vehicles["MINI-12"].id, "driver_id": drivers["Karan"].id, "cargo_weight_kg": 700.0, "planned_distance_km": 90.0, "revenue": 8000.0, "status": "Completed", "fuel_consumed_l": 10.0, "final_odometer": 45090.0, "created_at": datetime.datetime.now() - datetime.timedelta(days=2)},
            {"trip_code": "TR009", "source": "Chandigarh", "destination": "Shimla", "vehicle_id": vehicles["TRUCK-8"].id, "driver_id": drivers["Dev"].id, "cargo_weight_kg": 7500.0, "planned_distance_km": 110.0, "revenue": 16000.0, "status": "Completed", "fuel_consumed_l": 25.0, "final_odometer": 141000.0, "created_at": datetime.datetime.now() - datetime.timedelta(days=14)},
            {"trip_code": "TR010", "source": "Goa", "destination": "Mumbai", "vehicle_id": vehicles["TRUCK-15"].id, "driver_id": drivers["Vikram"].id, "cargo_weight_kg": 3800.0, "planned_distance_km": 590.0, "revenue": 45000.0, "status": "Draft", "fuel_consumed_l": None, "final_odometer": None, "created_at": datetime.datetime.now() - datetime.timedelta(hours=1)},
        ]

        trip_objects = {}
        for t in trips_data:
            trip = Trip(**t)
            session.add(trip)
            session.flush()
            trip_objects[t["trip_code"]] = trip

        # --- Maintenance Logs ---
        from app.models.maintenance import MaintenanceLog
        maintenance_data = [
            {"vehicle_id": vehicles["VAN-12"].id, "service_type": "Engine Tuning", "cost": 15000.0, "date": today, "status": "Active"},
            {"vehicle_id": vehicles["TRUCK-04"].id, "service_type": "Tyre Replacement", "cost": 45000.0, "date": today - datetime.timedelta(days=10), "status": "Completed"},
            {"vehicle_id": vehicles["MINI-03"].id, "service_type": "Oil Change", "cost": 3500.0, "date": today - datetime.timedelta(days=20), "status": "Completed"},
            {"vehicle_id": vehicles["TRUCK-22"].id, "service_type": "Brake Inspection", "cost": 12000.0, "date": today - datetime.timedelta(days=2), "status": "Active"},
            {"vehicle_id": vehicles["MINI-12"].id, "service_type": "Battery Replacement", "cost": 8500.0, "date": today - datetime.timedelta(days=15), "status": "Completed"},
            {"vehicle_id": vehicles["VAN-05"].id, "service_type": "Scheduled Service", "cost": 6000.0, "date": today - datetime.timedelta(days=45), "status": "Completed"},
            {"vehicle_id": vehicles["TRUCK-15"].id, "service_type": "Suspension Fix", "cost": 28000.0, "date": today - datetime.timedelta(days=60), "status": "Completed"}
        ]
        
        for m in maintenance_data:
            session.add(MaintenanceLog(**m))

        session.flush()

        # --- Fuel Logs ---
        from app.models.fuel_log import FuelLog
        fuel_data = [
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip_objects["TR001"].id, "liters": 18.0, "cost": 1800.0, "date": today - datetime.timedelta(days=5)},
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip_objects["TR004"].id, "liters": 45.0, "cost": 4500.0, "date": today - datetime.timedelta(days=3)},
            {"vehicle_id": vehicles["TRUCK-15"].id, "trip_id": trip_objects["TR006"].id, "liters": 30.0, "cost": 3000.0, "date": today - datetime.timedelta(days=8)},
            {"vehicle_id": vehicles["MINI-12"].id, "trip_id": trip_objects["TR008"].id, "liters": 10.0, "cost": 1000.0, "date": today - datetime.timedelta(days=2)},
            {"vehicle_id": vehicles["TRUCK-8"].id, "trip_id": trip_objects["TR009"].id, "liters": 25.0, "cost": 2500.0, "date": today - datetime.timedelta(days=14)},
            {"vehicle_id": vehicles["MINI-03"].id, "trip_id": None, "liters": 35.0, "cost": 3400.0, "date": today - datetime.timedelta(days=10)},
            {"vehicle_id": vehicles["TRUCK-04"].id, "trip_id": None, "liters": 100.0, "cost": 9800.0, "date": today - datetime.timedelta(days=25)},
            {"vehicle_id": vehicles["VAN-12"].id, "trip_id": None, "liters": 20.0, "cost": 1950.0, "date": today - datetime.timedelta(days=1)}
        ]
        
        for f in fuel_data:
            session.add(FuelLog(**f))

        session.flush()

        # --- Expenses ---
        from app.models.expense import Expense
        expense_data = [
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip_objects["TR001"].id, "category": "Toll", "amount": 250.0, "date": today - datetime.timedelta(days=5)},
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip_objects["TR004"].id, "category": "Toll", "amount": 800.0, "date": today - datetime.timedelta(days=3)},
            {"vehicle_id": vehicles["VAN-05"].id, "trip_id": trip_objects["TR004"].id, "category": "Driver Allowance", "amount": 1200.0, "date": today - datetime.timedelta(days=3)},
            {"vehicle_id": vehicles["TRUCK-8"].id, "trip_id": trip_objects["TR002"].id, "category": "Miscellaneous", "amount": 5000.0, "date": today - datetime.timedelta(days=1)},
            {"vehicle_id": vehicles["TRUCK-15"].id, "trip_id": trip_objects["TR006"].id, "category": "Toll", "amount": 1200.0, "date": today - datetime.timedelta(days=8)},
            {"vehicle_id": vehicles["MINI-12"].id, "trip_id": trip_objects["TR008"].id, "category": "Driver Allowance", "amount": 500.0, "date": today - datetime.timedelta(days=2)},
            {"vehicle_id": vehicles["TRUCK-8"].id, "trip_id": trip_objects["TR009"].id, "category": "Toll", "amount": 400.0, "date": today - datetime.timedelta(days=14)},
            {"vehicle_id": vehicles["MINI-03"].id, "trip_id": trip_objects["TR003"].id, "category": "Driver Allowance", "amount": 800.0, "date": today - datetime.timedelta(days=2)},
            {"vehicle_id": vehicles["TRUCK-22"].id, "trip_id": None, "category": "Miscellaneous", "amount": 3500.0, "date": today - datetime.timedelta(days=4)},
            {"vehicle_id": vehicles["MINI-07"].id, "trip_id": None, "category": "Toll", "amount": 300.0, "date": today - datetime.timedelta(days=6)}
        ]
        
        for e in expense_data:
            session.add(Expense(**e))
            
        session.flush()
        
        log.info("Seeded: 6 roles, 6 users, 10 vehicles, 8 drivers, 10 trips, 7 maintenance logs, 8 fuel logs, 10 expenses")
