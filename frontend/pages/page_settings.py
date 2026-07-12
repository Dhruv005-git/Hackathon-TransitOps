"""
frontend/pages/page_settings.py

Purpose:
    Settings & RBAC page — editable matrix in Phase 5.
    Phase 1: read-only RBAC matrix for Fleet Manager only.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st
import pandas as pd

from app.auth.rbac import PERMISSIONS, SIDEBAR_ITEMS
from app.services.auth_service import get_current_user


def render() -> None:
    user = get_current_user()

    # Double-check: only Fleet Manager sees this
    if user and user["role_name"] != "Fleet Manager":
        st.error("🚫 Settings are only accessible to Fleet Manager.")
        return

    st.markdown(
        '<div class="page-header"><h1 class="page-title">⚙️ Settings & RBAC</h1></div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Role-Based Access Control Matrix")
    st.caption("Read-only view. Editable RBAC matrix will be available in Phase 5.")

    modules = [item["module"] for item in SIDEBAR_ITEMS]
    roles   = list(PERMISSIONS.keys())

    matrix = {role: [PERMISSIONS[role].get(mod, "none") for mod in modules] for role in roles}
    df = pd.DataFrame(matrix, index=modules)

    def color_access(val: str) -> str:
        colors = {"edit": "#10b981", "view": "#3b82f6", "none": "#6b7280"}
        return f"color: {colors.get(val, '#e6e6e6')}; font-weight: 600; text-transform: uppercase;"

    st.dataframe(df.style.map(color_access), use_container_width=True)

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Editable Settings Coming in Phase 5</h3>
            <p>Depot Info, Editable Role-Permission Matrix, User Management — Phase 5.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
