# TransitOps 🚛
### Smart Transport Operations Platform
*React · Vite · FastAPI · SQLAlchemy · SQLite · Pydantic v2 · Recharts*

> **Hackathon Status:** ✅ All 6 Phases Complete + Full RBAC Enforcement + React/FastAPI Rewrite

---

## Quick Start

The application is split into a **FastAPI backend** and a **React frontend**.

### 1. Start the Backend (FastAPI)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Linux / macOS
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```
*Database is **auto-initialized and seeded** on first run — no manual DB step needed.*

### 2. Start the Frontend (React + Vite)
Open a new terminal window:
```bash
cd react-frontend
npm install
npm run dev
```
The app will be available at `http://localhost:5173`.

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| System Admin | admin@transitops.com | admin123 |
| Fleet Manager | fleet@transitops.com | fleet123 |
| Dispatcher | dispatch@transitops.com | dispatch123 |
| Safety Officer | safety@transitops.com | safety123 |
| Financial Analyst | finance@transitops.com | finance123 |
| Driver | driver@transitops.com | driver123 |

> 💡 On the login page, click any role button to auto-fill credentials.

---

## Reset Database (Development)
```bash
python -c "from app.database.engine import reset_database; reset_database()"
```
Deletes the SQLite file, recreates all tables, and reseeds demo data in one command.

---

## Build Roadmap

| Phase | Status | Scope |
|-------|--------|-------|
| **Phase 1** | ✅ **Complete** | Auth, DB (8 models), Seed, Dashboard, Router, Enums, Logger |
| **Phase 2** | ✅ **Complete** | Vehicle Registry CRUD + Driver Management CRUD + Business Rules |
| **Phase 3** | ✅ **Complete** | Trip Dispatch Engine + Lifecycle (Draft→Dispatched→Completed/Cancelled) |
| **Phase 4** | ✅ **Complete** | Maintenance Workflow (auto In Shop↔Available) + Fuel & Expense Logging |
| **Phase 5** | ✅ **Complete** | Analytics Charts + CSV Export + User Management + Settings |
| **Phase 6** | ✅ **Complete** | **React + FastAPI Rewrite**: Full decoupled architecture with modern UI/UX |
| **RBAC**    | ✅ **Complete** | Two-layer permission system enforced at API and UI level |
| **UI/UX**   | ✅ **Complete** | Glassmorphism, dynamic animations, Recharts, dark/light mode toggle |

---

## Feature Highlights

### 🚛 Fleet & Driver Management
- Full CRUD with validation (registration uniqueness, capacity limits)
- Safety score < 70 → driver auto-suspended
- License expiry tracking with color-coded alerts (expired / expiring ≤ 30d)
- Soft delete: vehicles with trips → Retired; drivers with trips → Off Duty

### 🗺️ Trip Dispatch Engine
- Trip lifecycle: **Draft → Dispatched → Completed / Cancelled**
- Dispatch validation: vehicle must be Available, driver must be Available + valid license
- `cargo_weight_kg <= vehicle.max_capacity_kg` enforced
- Dispatching locks vehicle + driver; completing/cancelling releases them

### 🔧 Maintenance & Fuel
- Log maintenance → vehicle status `Available → In Shop` automatically
- Close maintenance → vehicle status `In Shop → Available` automatically
- Fuel log with per-litre cost calculation; linkable to a specific trip
- Expense categories: Toll, Insurance, Fine, Parking, Loading/Unloading, Driver Allowance, Misc

### 📈 Analytics (Recharts)
- Vehicle Status Distribution (Bar Chart)
- Additional modular KPIs and metrics on the Dashboard

### 🔐 RBAC — Two-Layer Enforcement
**Backend (FastAPI):** `Depends(get_current_user)` and strict service-level checks.  
**Frontend (React):** Role-based rendering using `useAuth()` context for granular component control.

| Module | Fleet Manager | Dispatcher | Safety Officer | Financial Analyst | Driver |
|--------|:---:|:---:|:---:|:---:|:---:|
| Dashboard | 👁 View | 👁 View | 👁 View | 👁 View | 👁 View |
| Fleet | ✏️ Edit | 👁 View | 👁 View | 👁 View | ❌ Hidden |
| Drivers | ✏️ Edit | 👁 View | ✏️ Edit | 👁 View | ❌ Hidden |
| Trips | ✏️ Edit | ✏️ Edit | 👁 View | 👁 View | 👁 View |
| Maintenance | ✏️ Edit | 👁 View | 👁 View | 👁 View | ❌ Hidden |
| Fuel/Expenses | ✏️ Edit | 👁 View | 👁 View | ✏️ Edit | ❌ Hidden |
| Analytics | 👁 View | 👁 View | 👁 View | 👁 View | ❌ Hidden |
| Settings | ✏️ Edit | ❌ Hidden | ❌ Hidden | ❌ Hidden | ❌ Hidden |

---

## Architecture

### Decoupled React + FastAPI Pattern
The application was originally built using Streamlit but has been fully rewritten (Phase 6) into a modern, decoupled architecture:
1. **`api/` (FastAPI):** RESTful endpoints exposing the business logic (`app/services/`).
2. **`react-frontend/` (React + Vite):** A modern SPA using React Router, Context API for state management, Recharts for analytics, and Lucide React for iconography.

### Project Structure

```
TransitOps/
├── api/                          ← FastAPI REST Endpoints
│   ├── main.py                   ← FastAPI entry point + CORS
│   └── routes/                   ← Auth, trips, vehicles, drivers, etc.
│
├── app/                          ← Core Business Logic & DB (Python)
│   ├── models/                   ← SQLAlchemy ORM models (8 models)
│   ├── schemas/                  ← Pydantic v2 validation schemas
│   ├── services/                 ← Pure python business logic services
│   ├── auth/                     ← RBAC definitions and hashing
│   └── database/                 ← DB Engine & seed.py
│
├── react-frontend/               ← Modern React SPA
│   ├── src/
│   │   ├── api/client.js         ← Axios interceptors + base URL
│   │   ├── context/AuthContext.js← Global Auth state + Login/Logout logic
│   │   ├── components/           ← Sidebar, ThemeToggle, TopNav
│   │   ├── pages/                ← Dashboard, Trips, Fleet, Drivers, etc.
│   │   ├── utils/ui.js           ← Custom Toast notifications
│   │   ├── index.css             ← Design System (CSS Variables, Utilities)
│   │   └── App.jsx               ← React Router setup
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt              ← Python dependencies
└── README.md                     ← This file
```