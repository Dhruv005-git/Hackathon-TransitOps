"""
frontend/pages/page_settings.py — Phase 5
System info, User Management (view + change role), RBAC Matrix.
Fleet Manager only.
"""
from __future__ import annotations
import streamlit as st
import pandas as pd

from app.config import APP_NAME, DATABASE_URL, DEBUG
from app.auth.rbac import PERMISSIONS, SIDEBAR_ITEMS
from app.constants import UserRole
from app.services.auth_service import get_current_user
from app.database.engine import get_session
from app.models import User, Role


def _check_access() -> bool:
    user = get_current_user()
    if not user or user["role_name"] != UserRole.FLEET_MANAGER:
        st.error("🚫 Settings are accessible to Fleet Manager only.")
        return False
    return True


def _system_info():
    st.markdown("#### ⚙️ System Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Application", APP_NAME)
        st.metric("Debug Mode", "ON" if DEBUG else "OFF")
    with col2:
        st.metric("Database", "SQLite")
        st.metric("Auth", "bcrypt")
    with col3:
        st.metric("Framework", "Streamlit")
        st.metric("ORM", "SQLAlchemy")


def _user_management():
    st.markdown("#### 👥 User Management")

    with get_session() as s:
        users = s.query(User).join(Role).all()
        roles = s.query(Role).all()

        user_data = [
            {
                "id":        u.id,
                "name":      u.name,
                "email":     u.email,
                "role":      u.role.name,
                "role_id":   u.role_id,
                "active":    u.is_active,
            }
            for u in users
        ]
        role_opts = {r.name: r.id for r in roles}

    # Display table
    df = pd.DataFrame([{
        "Name":   u["name"],
        "Email":  u["email"],
        "Role":   u["role"],
        "Active": "Yes" if u["active"] else "No",
    } for u in user_data])

    def color_role(v):
        c = {"Fleet Manager": "color:#f59e0b;font-weight:700;",
             "Dispatcher":    "color:#3b82f6;font-weight:700;",
             "Safety Officer":"color:#10b981;font-weight:700;",
             "Financial Analyst":"color:#8b5cf6;font-weight:700;"}
        return c.get(v, "")

    st.dataframe(df.style.map(color_role, subset=["Role"]),
                 use_container_width=True, hide_index=True)

    # Role change form
    st.markdown("**Change User Role:**")
    with st.form("change_role_form"):
        u_opts  = {f"{u['name']} ({u['email']})": u for u in user_data}
        u_label = st.selectbox("Select User", list(u_opts.keys()))
        chosen  = u_opts[u_label]
        new_role= st.selectbox("New Role", list(role_opts.keys()),
                               index=list(role_opts.keys()).index(chosen["role"]))
        submitted = st.form_submit_button("🔄 Update Role", type="primary",
                                          use_container_width=True)

    if submitted:
        if new_role == chosen["role"]:
            st.info("User already has that role.")
        else:
            with get_session() as s:
                user_obj = s.query(User).filter(User.id == chosen["id"]).first()
                if user_obj:
                    user_obj.role_id = role_opts[new_role]
                    s.flush()
            st.success(f"✅ {chosen['name']}'s role changed to **{new_role}**.")
            st.rerun()


def _rbac_matrix():
    st.markdown("#### 🛡️ Role-Based Access Control Matrix")
    st.caption("Read-only. Roles are defined in app/auth/rbac.py.")

    modules = [item["module"] for item in SIDEBAR_ITEMS]
    roles   = list(PERMISSIONS.keys())

    matrix  = {role: [PERMISSIONS[role].get(mod, "none") for mod in modules] for role in roles}
    df      = pd.DataFrame(matrix, index=modules)

    def color_access(v):
        return {
            "edit": "color:#10b981;font-weight:700;text-transform:uppercase;",
            "view": "color:#3b82f6;font-weight:700;text-transform:uppercase;",
            "none": "color:#6b7280;text-transform:uppercase;",
        }.get(v, "")

    st.dataframe(df.style.map(color_access), use_container_width=True)


def _danger_zone():
    st.markdown("---")
    st.markdown("#### ⚠️ Danger Zone")
    st.warning("The following actions are irreversible in production. Use only during development.")

    with st.expander("🗑️ Reset Database"):
        st.markdown("Deletes the database file, recreates all tables, and reseeds demo data.")
        if st.button("🔴 Reset Database Now", type="primary", key="reset_db_btn"):
            from app.database.engine import reset_database
            reset_database()
            st.success("✅ Database reset and reseeded. Refresh the page.")


def render():
    if not _check_access():
        return

    st.markdown('<div class="page-header"><h1 class="page-title">⚙️ Settings</h1></div>',
                unsafe_allow_html=True)

    tab_sys, tab_users, tab_rbac = st.tabs(["🖥️ System", "👥 Users", "🛡️ RBAC Matrix"])

    with tab_sys:
        _system_info()
        st.markdown("---")
        _danger_zone()

    with tab_users:
        _user_management()

    with tab_rbac:
        _rbac_matrix()
