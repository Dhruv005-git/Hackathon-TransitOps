from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import auth, vehicles, drivers, trips, maintenance, analytics, fuel_logs, expenses

from contextlib import asynccontextmanager

from app.database.engine import init_db
from app.database.seed import seed_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and seed initial data on startup
    init_db()
    seed_db()
    yield

app = FastAPI(
    title="TransitOps API",
    description="Backend API for the TransitOps React Application",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for React frontend (which typically runs on port 5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(drivers.router, prefix="/api/drivers", tags=["Drivers"])
app.include_router(trips.router, prefix="/api/trips", tags=["Trips"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["Maintenance"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(fuel_logs.router, prefix="/api/fuel-logs", tags=["Fuel Logs"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Expenses"])

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
