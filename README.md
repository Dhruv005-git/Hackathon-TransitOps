# TransitOps 🚛
### Smart Transport Operations Platform
*Python · Streamlit · SQLAlchemy · SQLite · bcrypt*

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

---

## Reset Database (Development)
```bash
python -c "from app.database.engine import reset_database; reset_database()"
```
Deletes the SQLite file, recreates all tables, and reseeds demo data in one command.

---

## Architecture

### Single Entry Point Pattern
This app uses **one `app.py` entry point** instead of Streamlit's built-in multipage routing.
Each page in `frontend/pages/` exposes a `render()` function. The sidebar drives navigation
via `st.session_state["current_page"]` and `frontend/router.py` dispatches to the correct page.

```
app.py  →  show_sidebar()  →  route_to_page()  →  page_x.render()
```

**Why not Streamlit's native multipage?**
Streamlit requires pages in a root-level `pages/` folder. Our architecture uses
`frontend/pages/` (per SDD) and needs centralized RBAC + auth — incompatible with
Streamlit's routing. The render() pattern gives us full control with no hacks.

### Adding a New Page (Phase 3+)
1. Create `frontend/pages/page_newfeature.py` with a `render()` function
2. Add one line to `PAGE_MAP` in `frontend/router.py`
3. Add the RBAC entry in `app/auth/rbac.py`

---

## Project Structure

```
TransitOps/
├── app.py                        ← Entry point: login + sidebar + calls router
├── .env                          ← DATABASE_URL, SECRET_KEY, APP_NAME, DEBUG
├── .env.example
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
│   │   ├── trip.py, maintenance.py, fuel_log.py, expense.py
│   ├── auth/
│   │   ├── hashing.py            ← bcrypt hash_password / verify_password
│   │   └── rbac.py               ← 4-role × 8-module permission matrix
│   ├── services/
│   │   ├── auth_service.py       ← login(), logout(), get_current_user()
│   │   ├── vehicle_service.py    ← create(), update(), delete(), list() + search/filter
│   │   ├── driver_service.py     ← create(), update(), delete(), list() + license validation
│   │   └── trip_service.py       ← create_draft(), dispatch(), complete(), cancel() + validations
│   ├── database/
│   │   ├── engine.py             ← get_session, init_db, reset_database
│   │   └── seed.py               ← 4 roles, 4 users, 6 vehicles, 5 drivers, 5 trips
│   └── utils/, schemas/          ← Populated in Phase 3+
│
├── frontend/
│   ├── router.py                 ← PAGE_MAP + route_to_page() dispatcher
│   ├── assets/style.css          ← Dark theme CSS
│   ├── components/
│   │   ├── auth_guard.py         ← require_auth(), require_role()
│   │   ├── sidebar.py            ← Legacy (sidebar now in app.py)
│   │   ├── kpi_card.py           ← render_kpi_card(value, label, color)
│   │   └── status_badge.py       ← render_status_badge(status) → HTML
│   └── pages/                    ← Each file: render() function only
│       ├── page_dashboard.py     ← 7 KPIs + recent trips + vehicle chart
│       ├── page_fleet.py         ← Full CRUD: Add/Edit/Delete/Search/Filter vehicles
│       ├── page_drivers.py       ← Full CRUD: Add/Edit/Delete/Search/Filter + license expiry alerts
│       ├── page_trips.py         ← Full trip lifecycle: Draft→Dispatch→Complete/Cancel + Live Board
│       ├── page_maintenance.py   ← In Shop count (workflow in Phase 4)
│       ├── page_fuel_expenses.py ← Cost totals (logging in Phase 4)
│       ├── page_analytics.py     ← Top metrics (full charts in Phase 5)
│       └── page_settings.py      ← RBAC matrix read-only (editable in Phase 5)
│
├── tests/                        ← Unit tests (Phase 3+)
├── docs/
│   └── TransitOps_Phase1_Report.pdf  ← Full Phase 1 technical report
└── data/transitops.db            ← Auto-created on first run
```

---

## Build Roadmap

| Phase | Status | Scope |
|-------|--------|-------|
| **Phase 1** | ✅ **Complete** | Auth, DB (8 models), Seed, Dashboard, Dark Theme, Router, Enums, Logger |
| **Phase 2** | ✅ **Complete** | Vehicle Registry CRUD + Driver Management CRUD + License Validation + RBAC gating |
| **Phase 3** | ✅ **Complete** | Trip Dispatch Engine + Full Lifecycle (Draft→Dispatch→Complete/Cancel) + Live Board + 7 Business Rules |
| Phase 4 | ⏳ Pending | Maintenance Workflow + Fuel & Expense Logging |
| Phase 5 | ⏳ Pending | Analytics Charts + CSV Export + Editable Settings |

---

## Phase 2 — What's New

### Vehicle Registry (`page_fleet.py`)
- **Add Vehicle** — form with registration no, model, type, capacity, odometer, cost, status
- **Edit Vehicle** — inline form pre-filled with existing data
- **Delete Vehicle** — confirmation checkbox required before deletion
- **Search** — case-insensitive match on registration no or model name
- **Filter** — by status: Available / On Trip / In Shop / Retired
- **Summary Metrics** — total, available, on-trip, in-shop counts
- **Unique Reg No Validation** — duplicate registration rejected with friendly error
- **RBAC** — edit forms only visible to Fleet Manager; all other roles get view-only

### Driver Management (`page_drivers.py`)
- **Add Driver** — form with name, license no, category (LMV/HMV), expiry, contact, safety score, status
- **Edit Driver** — inline form pre-filled with existing data
- **Delete Driver** — confirmation checkbox required
- **Search** — case-insensitive match on name or license no
- **Filter** — by status: Available / On Trip / Off Duty / Suspended
- **Summary Metrics** — total, available, on-trip, suspended, expiring soon (≤30 days), expired
- **License Validation** — cannot add a driver with an already-expired license
- **Unique License No Validation** — duplicate license rejected with friendly error
- **RBAC** — edit forms visible to Fleet Manager and Safety Officer; others get view-only

### Services Added
| Service | Functions |
|---------|-----------|
| `vehicle_service.py` | `list_vehicles()`, `create_vehicle()`, `update_vehicle()`, `delete_vehicle()` |
| `driver_service.py` | `list_drivers()`, `create_driver()`, `update_driver()`, `delete_driver()` |

---

## Phase 3 — What's New

### Trip Dispatcher (`page_trips.py`)
Full two-tab page replacing the Phase 2 read-only stub:

**Tab 1 — Trip Dispatcher**
- **Create Draft Trip** — form with origin, destination, vehicle (all shown with capacity), available driver, cargo weight, planned distance, expected revenue; auto-generates trip code in `TR-YYYYMMDD-NNN` format
- **Dispatch Trip** — selectbox of Draft trips with a live pre-dispatch summary card showing vehicle status, driver status, license validity (colour-coded green/red), and safety score; blocked if any rule fails
- **Complete Trip** — selectbox of Dispatched trips; captures fuel consumed (L) and final odometer; pre-fills odometer with `current + planned_distance`
- **Cancel Trip** — selectbox of Draft or Dispatched trips; shows contextual warning when cancelling a Dispatched trip (vehicle+driver will be restored); checkbox confirmation required
- **Search** — case-insensitive match on trip code, origin, or destination
- **Filter** — by status: All / Draft / Dispatched / Completed / Cancelled
- **5-Metric KPI Row** — Total · Draft · Dispatched · Completed · Cancelled counts
- **Colour-coded table** — Status column coloured per trip state
- **RBAC** — all action forms visible to Dispatcher only; all other roles get view-only message

**Tab 2 — Live Dispatch Board**
- **4-column Kanban** — Draft | Dispatched | Completed | Cancelled
- **Trip cards** — trip code (monospace), route, vehicle, driver, cargo + distance, revenue badge (green), creation timestamp
- **Column headers** — colour-coded per status with live count badge
- **Hover animation** — cards lift and glow orange on hover
- **Empty state** — dashed placeholder when a column has no trips
- **Refresh button** — instant live reload

### Dispatch Engine — Business Rules
All rules enforced in the **service layer** (`trip_service.py`), never in the UI:

| Rule | Enforced In |
|------|-------------|
| Vehicle must be `Available` | `dispatch()` |
| Driver must be `Available` | `dispatch()` |
| Driver must **not** be `Suspended` | `dispatch()` |
| Driver license must **not** be expired | `dispatch()` |
| Cargo weight ≤ vehicle max capacity | `create_draft()` + `dispatch()` |
| Only `Draft` trips can be dispatched | `dispatch()` |
| Only `Dispatched` trips can be completed | `complete()` |
| Already `Completed`/`Cancelled` trips cannot be cancelled | `cancel()` |

### Status Transitions
```
                  ┌─────────────────────────────────────────────┐
                  │              Trip Lifecycle                   │
                  └─────────────────────────────────────────────┘

  create_draft()        dispatch()           complete()
  ─────────────→  Draft ─────────→ Dispatched ─────────→ Completed
                    │                  │
              cancel()           cancel()
                    └──────┬───────────┘
                           ↓
                        Cancelled

  On dispatch:  Vehicle → On Trip   │  Driver → On Trip
  On complete:  Vehicle → Available │  Driver → Available
  On cancel
   (if Dispatched): Vehicle → Available │  Driver → Available
   (if Draft):      no side-effects
```

### Service Added
| Service | Functions |
|---------|-----------|
| `trip_service.py` | `list_trips()`, `get_trip()`, `create_draft()`, `dispatch()`, `complete()`, `cancel()`, `list_available_vehicles()`, `list_available_drivers()` |

### CSS Added (`style.css`)
- `.dispatch-card` — dark card with border-radius, hover lift + orange glow
- `.dispatch-col-header` — coloured top-border column header with count badge
- `.dispatch-card-revenue` — green revenue chip
- `.dispatch-empty` — dashed empty-column placeholder

### Git Commit
```
feat: trip lifecycle with dispatch validation and status automation
```
Branch: `nevil-phase3` → merged to `main`

---

## Documentation

Full Phase 1 technical report (architecture decisions, bugs fixed, features):
`docs/TransitOps_Phase1_Report.pdf`