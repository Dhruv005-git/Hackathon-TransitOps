# TransitOps 🚛
### Smart Transport Operations Platform
*Python · Streamlit · SQLAlchemy · SQLite · Pydantic v2 · bcrypt · Plotly*

> **Hackathon Status:** ✅ All 5 Phases Complete + Full RBAC Enforcement + UI/UX Upgrades

---

## Quick Start

### 1. Create & Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```
Database is **auto-initialized and seeded** on first run — no manual DB step needed.

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Fleet Manager | fleet@transitops.com | fleet123 |
| Dispatcher | dispatch@transitops.com | dispatch123 |
| Safety Officer | safety@transitops.com | safety123 |
| Financial Analyst | finance@transitops.com | finance123 |

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
| **Phase 1** | ✅ **Complete** | Auth, DB (8 models), Seed, Dashboard, Dark Theme, Router, Enums, Logger |
| **Phase 2** | ✅ **Complete** | Vehicle Registry CRUD + Driver Management CRUD + Business Rules |
| **Phase 3** | ✅ **Complete** | Trip Dispatch Engine + Lifecycle (Draft→Dispatched→Completed/Cancelled) |
| **Phase 4** | ✅ **Complete** | Maintenance Workflow (auto In Shop↔Available) + Fuel & Expense Logging |
| **Phase 5** | ✅ **Complete** | 5 Plotly Analytics Charts + CSV Export + User Management + Settings |
| **RBAC**    | ✅ **Complete** | Two-layer permission system: coarse (sidebar) + granular (per-button) |
| **UI/UX**   | ✅ **Complete** | Selection cards, CSS polish, dashboard donut chart, live recent trips |

---

## Feature Highlights

### 🚛 Fleet & Driver Management (Phase 2)
- Full CRUD with validation (registration uniqueness, capacity limits)
- Safety score < 70 → driver auto-suspended
- License expiry tracking with colour-coded alerts (expired / expiring ≤ 30d)
- Soft delete: vehicles with trips → Retired; drivers with trips → Off Duty

### 🗺️ Trip Dispatch Engine (Phase 3)
- Trip lifecycle: **Draft → Dispatched → Completed / Cancelled**
- Dispatch validation: vehicle must be Available, driver must be Available + valid license
- cargo_weight_kg ≤ vehicle.max_capacity_kg enforced
- Trip code auto-generated: `TRP-DDMMYY-XXXXXX`
- Dispatching locks vehicle + driver; completing/cancelling releases them

### 🔧 Maintenance & Fuel (Phase 4)
- Log maintenance → vehicle status `Available → In Shop` automatically
- Close maintenance → vehicle status `In Shop → Available` automatically
- Fuel log with per-litre cost calculation; linkable to a specific trip
- Expense categories: Toll, Insurance, Fine, Parking, Loading/Unloading, Driver Allowance, Misc

### 📈 Analytics (Phase 5)
- Revenue by Vehicle (bar), Completed Trips by Month (bar)
- Fuel Efficiency per Vehicle (colour-coded bar: green ≥ 10 km/L)
- Cost Breakdown donut (Fuel vs Expenses vs Maintenance)
- Total Trips per Vehicle (bar)
- CSV export for Trips, Fuel Logs, Expenses (Fleet Manager + Financial Analyst only)

### 🔐 RBAC — Two-Layer Enforcement
**Layer 1 (Coarse):** `PERMISSIONS` dict in `rbac.py` → controls sidebar visibility  
**Layer 2 (Granular):** `ROLE_ACTIONS` dict in `rbac.py` → controls individual buttons/forms/tabs

```python
# Example usage in any page
from frontend.components.auth_guard import can

if can("fleet.add"):
    show_add_vehicle_tab()

if can("trips.dispatch") and trip["status"] == "Draft":
    show_dispatch_button()
```

| Module | Fleet Manager | Dispatcher | Safety Officer | Financial Analyst |
|--------|:---:|:---:|:---:|:---:|
| Dashboard | 👁 View | 👁 View | 👁 View | 👁 View |
| Fleet | ✏️ Full CRUD | 👁 View | 👁 View | 👁 View |
| Drivers | ✏️ Full CRUD | 👁 View | ✏️ Add/Edit/Status | 👁 View |
| Trips | ✏️ Full workflow | ✏️ Full workflow | 👁 View | 👁 View |
| Maintenance | ✏️ Full CRUD | 👁 View | 👁 View | 👁 View |
| Fuel & Expenses | ✏️ Full CRUD | 👁 View | 👁 View | ✏️ Add/View |
| Analytics | 👁 + CSV Export | 👁 Charts only | 👁 Charts only | 👁 + CSV Export |
| Settings | ✏️ Full | ❌ Hidden | ❌ Hidden | ❌ Hidden |

---

## Architecture

### Single Entry Point Pattern
```
app.py  →  show_sidebar()  →  route_to_page()  →  page_x.render()
```
One `app.py` entry point; all navigation via `st.session_state["current_page"]`.  
Pages in `frontend/pages/` expose only a `render()` function — zero Streamlit imports in `app/`.

### Adding a New Page
1. Create `frontend/pages/page_newfeature.py` with a `render()` function
2. Add one line to `PAGE_MAP` in `frontend/router.py`
3. Add RBAC entry in `app/auth/rbac.py` (both `PERMISSIONS` and `ROLE_ACTIONS`)

---

## Project Structure

```
TransitOps/
├── app.py                        ← Entry point: login + sidebar + calls router
├── .env                          ← DATABASE_URL, SECRET_KEY, APP_NAME, DEBUG
├── .streamlit/config.toml        ← Dark theme + orange accent
├── requirements.txt
├── README.md
│
├── app/                          ← Backend (zero Streamlit imports)
│   ├── config.py                 ← Reads .env, all settings as typed constants
│   ├── constants.py              ← Status enums: VehicleStatus, DriverStatus…
│   ├── logger.py                 ← get_logger(__name__) factory
│   ├── models/                   ← 8 SQLAlchemy ORM models
│   │   ├── role.py, user.py, vehicle.py, driver.py
│   │   └── trip.py, maintenance.py, fuel_log.py, expense.py
│   ├── auth/
│   │   ├── hashing.py            ← bcrypt hash_password / verify_password
│   │   └── rbac.py               ← PERMISSIONS + ROLE_ACTIONS + role_can() + can_edit()
│   ├── schemas/                  ← Pydantic v2 input/update validation schemas
│   │   ├── vehicle_schema.py, driver_schema.py
│   │   ├── trip_schema.py, maintenance_schema.py, fuel_schema.py
│   ├── services/                 ← Business logic (pure Python, no Streamlit)
│   │   ├── auth_service.py       ← login(), logout(), get_current_user()
│   │   ├── vehicle_service.py    ← CRUD + fleet_summary
│   │   ├── driver_service.py     ← CRUD + driver_summary + license checks
│   │   ├── trip_service.py       ← create, dispatch, complete, cancel + validation
│   │   ├── maintenance_service.py← log, close + auto vehicle status transition
│   │   └── fuel_service.py       ← add_fuel_log, add_expense, cost_summary
│   └── database/
│       ├── engine.py             ← get_session, init_db, reset_database
│       └── seed.py               ← 4 roles, 4 users, 6 vehicles, 5 drivers, 5 trips
│
├── frontend/
│   ├── router.py                 ← PAGE_MAP + route_to_page() dispatcher
│   ├── assets/style.css          ← Dark theme CSS + selection-card + button polish
│   ├── components/
│   │   ├── auth_guard.py         ← require_auth(), require_role(), can(action)
│   │   ├── kpi_card.py           ← render_kpi_card(value, label, color)
│   │   └── sidebar.py            ← Role-filtered navigation sidebar
│   └── pages/                    ← Each file: render() function only
│       ├── page_dashboard.py     ← 8 KPIs + live recent trips + fleet donut chart
│       ├── page_fleet.py         ← Full vehicle CRUD + selection card actions
│       ├── page_drivers.py       ← Full driver CRUD + license alerts + selection card
│       ├── page_trips.py         ← Trip lifecycle + selection card + dispatch engine
│       ├── page_maintenance.py   ← Maintenance log/close + auto status transitions
│       ├── page_fuel_expenses.py ← Fuel log + expense log + records viewer
│       ├── page_analytics.py     ← 5 Plotly charts + CSV export (role-gated)
│       └── page_settings.py      ← User mgmt + RBAC matrix + danger zone
│
├── docs/
│   ├── TransitOps_Phase1_Report.pdf    ← Phase 1 technical report
│   ├── TransitOps_Phases2to5_Report.pdf← Phases 2–5 full report (features, errors, arch)
│   └── generate_report_p2_p5.py        ← ReportLab PDF generator
└── data/transitops.db            ← Auto-created SQLite database
```

---

## Documentation

- **Phase 1 Report** — Auth, DB models, seed, dashboard, router architecture
- **Phases 2–5 Report** — All features, 8 errors + fixes, RBAC matrix, architecture decisions  
  → `docs/TransitOps_Phases2to5_Report.pdf`