"""
app/auth/rbac.py

Purpose:
    Role-Based Access Control permission matrix.

Two levels of RBAC:
  1. PERMISSIONS (coarse) — "none" / "view" / "edit"
     Controls sidebar visibility and module-level access.

  2. ROLE_ACTIONS (granular) — per-action booleans
     Controls which buttons/forms are shown inside each page.
     Implements the exact permission spec from the SDD.
"""

from typing import Literal

AccessLevel = Literal["none", "view", "edit"]

# ── Coarse matrix: sidebar visibility ─────────────────────────
PERMISSIONS: dict[str, dict[str, AccessLevel]] = {
    "Admin": {
        "Dashboard": "edit",
        "Fleet": "edit",
        "Drivers": "edit",
        "Trips": "edit",
        "Maintenance": "edit",
        "Fuel & Expenses": "edit",
        "Analytics": "edit",
        "Settings": "edit",
    },
    "Fleet Manager": {
        "Dashboard":       "view",
        "Fleet":           "edit",
        "Drivers":         "edit",
        "Trips":           "view",
        "Maintenance":     "edit",
        "Fuel & Expenses": "edit",
        "Analytics":       "view",
        "Settings":        "edit",
    },
    "Dispatcher": {
        "Dashboard":       "view",
        "Fleet":           "view",
        "Drivers":         "view",
        "Trips":           "edit",
        "Maintenance":     "view",
        "Fuel & Expenses": "view",
        "Analytics":       "view",
        "Settings":        "none",
    },
    "Safety Officer": {
        "Dashboard":       "view",
        "Fleet":           "view",
        "Drivers":         "edit",
        "Trips":           "view",
        "Maintenance":     "view",
        "Fuel & Expenses": "view",
        "Analytics":       "view",
        "Settings":        "none",
    },
    "Financial Analyst": {
        "Dashboard":       "view",
        "Fleet":           "view",
        "Drivers":         "view",
        "Trips":           "view",
        "Maintenance":     "view",
        "Fuel & Expenses": "edit",
        "Analytics":       "view",
        "Settings":        "none",
    },
    "Driver": {
        "Dashboard": "view",
        "Fleet": "none",
        "Drivers": "none",
        "Trips": "view",
        "Maintenance": "none",
        "Fuel & Expenses": "none",
        "Analytics": "none",
        "Settings": "none",
    },
}

# ── Granular action matrix ─────────────────────────────────────
# Each key maps to a specific button / form section in a page.
# Format: "module.action"
ROLE_ACTIONS: dict[str, dict[str, bool]] = {
    "Fleet Manager": {
        # Fleet
        "fleet.add":    True, "fleet.edit":   True,
        "fleet.delete": True, "fleet.status": True,
        # Drivers
        "drivers.add":    True, "drivers.edit":   True,
        "drivers.delete": True, "drivers.status": True,
        # Trips
        "trips.create":     True, "trips.dispatch":   True,
        "trips.complete":   True, "trips.cancel":     True,
        "trips.edit_draft": True,
        # Maintenance
        "maintenance.log": True, "maintenance.close": True,
        # Fuel & Expenses
        "fuel.add": True, "expenses.add": True,
        # Analytics
        "analytics.export": True,
        # Settings
        "settings.manage": True,
    },
    "Dispatcher": {
        # Fleet — view only
        "fleet.add":    False, "fleet.edit":   False,
        "fleet.delete": False, "fleet.status": False,
        # Drivers — view only
        "drivers.add":    False, "drivers.edit":   False,
        "drivers.delete": False, "drivers.status": False,
        # Trips — full workflow
        "trips.create":     True, "trips.dispatch":   True,
        "trips.complete":   True, "trips.cancel":     True,
        "trips.edit_draft": True,
        # Maintenance — view only
        "maintenance.log": False, "maintenance.close": False,
        # Fuel & Expenses — view only
        "fuel.add": False, "expenses.add": False,
        # Analytics
        "analytics.export": False,
        # Settings
        "settings.manage": False,
    },
    "Safety Officer": {
        # Fleet — view only
        "fleet.add":    False, "fleet.edit":   False,
        "fleet.delete": False, "fleet.status": False,
        # Drivers — add + edit + status (no delete)
        "drivers.add":    True,  "drivers.edit":   True,
        "drivers.delete": False, "drivers.status": True,
        # Trips — view only
        "trips.create":     False, "trips.dispatch":   False,
        "trips.complete":   False, "trips.cancel":     False,
        "trips.edit_draft": False,
        # Maintenance — view only
        "maintenance.log": False, "maintenance.close": False,
        # Fuel & Expenses — view only
        "fuel.add": False, "expenses.add": False,
        # Analytics
        "analytics.export": False,
        # Settings
        "settings.manage": False,
    },
    "Financial Analyst": {
        # Fleet — view only
        "fleet.add":    False, "fleet.edit":   False,
        "fleet.delete": False, "fleet.status": False,
        # Drivers — view only
        "drivers.add":    False, "drivers.edit":   False,
        "drivers.delete": False, "drivers.status": False,
        # Trips — view only
        "trips.create":     False, "trips.dispatch":   False,
        "trips.complete":   False, "trips.cancel":     False,
        "trips.edit_draft": False,
        # Maintenance — view only
        "maintenance.log": False, "maintenance.close": False,
        # Fuel & Expenses — add + view
        "fuel.add": True, "expenses.add": True,
        # Analytics
        "analytics.export": True,
        # Settings
        "settings.manage": False,
    },
}

# ── Sidebar items ──────────────────────────────────────────────
SIDEBAR_ITEMS: list[dict[str, str]] = [
    {"label": "Dashboard",       "icon": "📊", "module": "Dashboard"},
    {"label": "Fleet",           "icon": "🚛", "module": "Fleet"},
    {"label": "Drivers",         "icon": "👤", "module": "Drivers"},
    {"label": "Trips",           "icon": "🗺️", "module": "Trips"},
    {"label": "Maintenance",     "icon": "🔧", "module": "Maintenance"},
    {"label": "Fuel & Expenses", "icon": "⛽", "module": "Fuel & Expenses"},
    {"label": "Analytics",       "icon": "📈", "module": "Analytics"},
    {"label": "Settings",        "icon": "⚙️", "module": "Settings"},
]


# ── Helpers ────────────────────────────────────────────────────
def has_access(role_name: str, module: str) -> AccessLevel:
    """Coarse check — returns none/view/edit for sidebar gating."""
    return PERMISSIONS.get(role_name, {}).get(module, "none")


def get_accessible_modules(role_name: str) -> list[dict[str, str]]:
    """Return sidebar items the role can see (access != 'none')."""
    return [
        item for item in SIDEBAR_ITEMS
        if has_access(role_name, item["module"]) != "none"
    ]


def can_edit(role_name: str, module: str) -> bool:
    """Coarse check — True if role has edit access to the module."""
    return has_access(role_name, module) == "edit"


def role_can(role_name: str, action: str) -> bool:
    """
    Granular action check.

    Args:
        role_name: e.g. "Dispatcher"
        action:    e.g. "trips.dispatch"

    Returns:
        True if the role is allowed to perform that action.
    """
    return ROLE_ACTIONS.get(role_name, {}).get(action, False)
