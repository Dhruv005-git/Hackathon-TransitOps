"""
frontend/router.py

Purpose:
    Page routing logic — maps module names to page render() functions.

Reason:
    Extracted from app.py to keep the entry point lean.
    app.py handles setup, auth, and sidebar. router.py handles dispatch.
    Adding a new page in Phase 2+ only requires adding one line here.

Usage:
    from frontend.router import route_to_page
    route_to_page("Dashboard", user)
"""

import importlib
import streamlit as st

from app.auth.rbac import has_access
from app.logger import get_logger

log = get_logger(__name__)

# Map sidebar module name → Python module path (each exposes render())
PAGE_MAP: dict[str, str] = {
    "Dashboard":       "frontend.pages.page_dashboard",
    "Fleet":           "frontend.pages.page_fleet",
    "Drivers":         "frontend.pages.page_drivers",
    "Trips":           "frontend.pages.page_trips",
    "Maintenance":     "frontend.pages.page_maintenance",
    "Fuel & Expenses": "frontend.pages.page_fuel_expenses",
    "Analytics":       "frontend.pages.page_analytics",
    "Settings":        "frontend.pages.page_settings",
}


def route_to_page(page: str, user: dict) -> None:
    """
    Verify RBAC access and render the requested page.

    Args:
        page: Module name from SIDEBAR_ITEMS (e.g. "Dashboard", "Fleet").
        user: Current user dict from session state.
    """
    # RBAC gate — double-check even though sidebar already filters
    if has_access(user["role_name"], page) == "none":
        st.error(f"You don't have access to the {page} module.")
        log.warning("Unauthorized access attempt: user=%s role=%s page=%s",
                    user["email"], user["role_name"], page)
        return

    module_path = PAGE_MAP.get(page)
    if not module_path:
        st.error(f"Page '{page}' is not registered in the router.")
        log.error("Unknown page requested: %s", page)
        return

    log.debug("Routing to page=%s via module=%s", page, module_path)
    mod = importlib.import_module(module_path)
    mod.render()
