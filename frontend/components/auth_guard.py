"""
frontend/components/auth_guard.py

Purpose:
    Authentication and granular authorization guard for all pages.

Provides:
    require_auth()   — blocks unauthenticated users
    require_role()   — coarse module-level access gate
    can(action)      — granular per-button/form permission check
"""

import streamlit as st

from app.services.auth_service import is_authenticated, get_current_user
from app.auth.rbac import has_access, role_can


def require_auth() -> dict:
    """
    Ensure the user is logged in. If not, stop the page.
    Returns the current user dict if authenticated.
    """
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.stop()
    user = get_current_user()
    if user is None:
        st.warning("Session expired. Please log in again.")
        st.stop()
    return user


def require_role(module: str, min_level: str = "view") -> str:
    """
    Check if the current user's role has access to a module.

    Args:
        module:    e.g. "Fleet", "Trips"
        min_level: minimum required access ("view" or "edit")

    Returns:
        The actual access level ("view" or "edit")
    """
    user  = require_auth()
    level = has_access(user["role_name"], module)

    if level == "none":
        st.error(f"You don't have access to the {module} module.")
        st.stop()

    if min_level == "edit" and level != "edit":
        st.warning(f"You have view-only access to {module}.")

    return level


def can(action: str) -> bool:
    """
    Granular action permission check for the current session user.

    Usage in pages:
        from frontend.components.auth_guard import can
        if can("fleet.add"):
            show_add_form()

    Args:
        action: e.g. "fleet.add", "trips.dispatch", "fuel.add"

    Returns:
        True if the current user's role may perform the action.
        Always returns False if no user is in session.
    """
    user = get_current_user()
    if user is None:
        return False
    return role_can(user["role_name"], action)
