"""
app/auth/rbac.py

Purpose:
    Role-Based Access Control permission matrix.

Reason:
    Hardcoded permission map matching the mockup's Settings screen.
    Kept as a Python dict so it works without any DB query overhead.
    Can be made editable from the Settings UI in Phase 5 if time allows.
"""

from typing import Literal

AccessLevel = Literal["none", "view", "edit"]

# Permission matrix: role_name -> module -> access_level
# Matches the RBAC table from mockup screen 8
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
        "Dashboard": "view",
        "Fleet": "edit",
        "Drivers": "edit",
        "Trips": "view",
        "Maintenance": "edit",
        "Fuel & Expenses": "edit",
        "Analytics": "view",
        "Settings": "edit",
    },
    "Dispatcher": {
        "Dashboard": "view",
        "Fleet": "view",
        "Drivers": "view",
        "Trips": "edit",
        "Maintenance": "view",
        "Fuel & Expenses": "view",
        "Analytics": "view",
        "Settings": "none",
    },
    "Safety Officer": {
        "Dashboard": "view",
        "Fleet": "view",
        "Drivers": "edit",
        "Trips": "view",
        "Maintenance": "view",
        "Fuel & Expenses": "view",
        "Analytics": "view",
        "Settings": "none",
    },
    "Financial Analyst": {
        "Dashboard": "view",
        "Fleet": "view",
        "Drivers": "view",
        "Trips": "view",
        "Maintenance": "view",
        "Fuel & Expenses": "edit",
        "Analytics": "view",
        "Settings": "none",
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

# Sidebar items in display order (matches mockup sidebar)
SIDEBAR_ITEMS: list[dict[str, str]] = [
    {"label": "Dashboard", "icon": "📊", "module": "Dashboard"},
    {"label": "Fleet", "icon": "🚛", "module": "Fleet"},
    {"label": "Drivers", "icon": "👤", "module": "Drivers"},
    {"label": "Trips", "icon": "🗺️", "module": "Trips"},
    {"label": "Maintenance", "icon": "🔧", "module": "Maintenance"},
    {"label": "Fuel & Expenses", "icon": "⛽", "module": "Fuel & Expenses"},
    {"label": "Analytics", "icon": "📈", "module": "Analytics"},
    {"label": "Settings", "icon": "⚙️", "module": "Settings"},
]


def has_access(role_name: str, module: str) -> AccessLevel:
    """Check what access level a role has for a given module."""
    return PERMISSIONS.get(role_name, {}).get(module, "none")


def get_accessible_modules(role_name: str) -> list[dict[str, str]]:
    """Return sidebar items the role can see (access != 'none')."""
    return [
        item for item in SIDEBAR_ITEMS
        if has_access(role_name, item["module"]) != "none"
    ]


def can_edit(role_name: str, module: str) -> bool:
    """Check if a role has edit access to a module."""
    return has_access(role_name, module) == "edit"
