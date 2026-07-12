"""
frontend/components/sidebar.py

Purpose:
    Persistent sidebar matching the mockup's navigation layout.

Reason:
    Reusable across all pages. Shows user info, role badge, RBAC-filtered
    navigation items, and a logout button. Renders identically on every page.
"""

import streamlit as st

from app.services.auth_service import get_current_user, logout
from app.auth.rbac import get_accessible_modules


def render_sidebar() -> None:
    """Render the sidebar with user info, navigation, and logout."""
    user = get_current_user()
    if user is None:
        return

    with st.sidebar:
        # --- Brand ---
        st.markdown(
            "<h2 style='color: #f59e0b; margin-bottom: 0;'>🚛 TransitOps</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: #9ca3af; font-size: 0.8rem; margin-top: 0;'>Smart Transport Operations</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # --- User Info ---
        st.markdown(
            f"""
            <div class="sidebar-user-info">
                <p class="sidebar-user-name">👤 {user['name']}</p>
                <p class="sidebar-user-role">{user['role_name']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Navigation ---
        modules = get_accessible_modules(user["role_name"])

        # Page file mapping
        page_map = {
            "Dashboard": "pages/1_Dashboard",
            "Fleet": "pages/2_Fleet",
            "Drivers": "pages/3_Drivers",
            "Trips": "pages/4_Trips",
            "Maintenance": "pages/5_Maintenance",
            "Fuel & Expenses": "pages/6_Fuel_Expenses",
            "Analytics": "pages/7_Analytics",
            "Settings": "pages/8_Settings",
        }

        for item in modules:
            page_name = page_map.get(item["module"], "")
            st.page_link(
                f"pages/{page_name}.py",
                label=f"{item['icon']}  {item['label']}",
            )

        st.divider()

        # --- Logout ---
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
