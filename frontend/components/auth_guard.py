"""
frontend/components/auth_guard.py

Purpose:
    Authentication and authorization guard for all pages.

Reason:
    Every page calls require_auth() at the top. This ensures no
    unauthenticated user can see any content beyond the login page.
    Also provides require_role() for RBAC module-level gating.
"""

import streamlit as st

from app.services.auth_service import is_authenticated, get_current_user
from app.auth.rbac import has_access


def require_auth() -> dict:
    """
    Ensure the user is logged in. If not, stop the page and show a message.

    Returns:
        The current user dict if authenticated.
    """
    if not is_authenticated():
        st.warning("⚠️ Please log in to access this page.")
        st.stop()

    user = get_current_user()
    if user is None:
        st.warning("⚠️ Session expired. Please log in again.")
        st.stop()

    return user


def require_role(module: str, min_level: str = "view") -> str:
    """
    Check if the current user's role has access to a module.

    Args:
        module: The module name (e.g. "Fleet", "Trips")
        min_level: Minimum required access ("view" or "edit")

    Returns:
        The actual access level ("view" or "edit")
    """
    user = require_auth()
    level = has_access(user["role_name"], module)

    if level == "none":
        st.error(f"🚫 You don't have access to the {module} module.")
        st.stop()

    if min_level == "edit" and level != "edit":
        st.warning(f"🔒 You have view-only access to {module}.")

    return level
