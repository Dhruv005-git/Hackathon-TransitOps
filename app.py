"""
app.py

Purpose:
    Single entry point and page router for TransitOps.
    Manages login, session, and all page navigation in one place.

Architecture:
    Single app.py approach — no Streamlit multipage routing.
    Each page in frontend/pages/ exposes a render() function.
    Navigation is driven by st.session_state["current_page"] via the sidebar.
    This gives us full RBAC control without fighting Streamlit's routing.

Run with:
    streamlit run app.py
"""

import streamlit as st
from pathlib import Path

# --- Page Config (must be very first Streamlit call) ---
st.set_page_config(
    page_title="TransitOps — Smart Transport Operations",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load CSS ---
css_path = Path(__file__).parent / "frontend" / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# --- Logger ---
from app.logger import get_logger
log = get_logger(__name__)

# --- Initialize Database on First Run ---
from app.database.engine import init_db
from app.database.seed import seed_all

init_db()
seed_all()

# --- Auth Helpers ---
from app.services.auth_service import (
    login,
    set_current_user,
    is_authenticated,
    get_current_user,
    logout,
)
from app.auth.rbac import get_accessible_modules, has_access
from frontend.router import route_to_page


# ============================================================
# LOGIN PAGE
# ============================================================
def show_login() -> None:
    """Render the login page."""
    col_brand, col_form = st.columns([1, 1], gap="large")

    with col_brand:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            '<p class="login-brand">🚛 TransitOps</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="login-subtitle">Smart Transport Operations Platform</p>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Your login, Your roles:**")
        st.markdown(
            """
            - 🏢 **Fleet Manager** → Fleet, Maintenance, Analytics
            - 🗺️ **Dispatcher** → Trips, Dashboard
            - 🛡️ **Safety Officer** → Drivers, Compliance
            - 💰 **Financial Analyst** → Fuel & Expenses, Analytics
            """
        )
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("TransitOps © 2026 · Built for Hackathon")

    with col_form:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Sign in to your account")
        st.markdown("Enter your credentials to continue")
        st.markdown("<br>", unsafe_allow_html=True)

        # --- Quick-fill role buttons (outside form — trigger rerun to pre-fill) ---
        st.markdown(
            "<p style='color:#9ca3af; font-size:0.8rem; margin-bottom:6px;'>"
            "⚡ Quick login — click a role to fill credentials:</p>",
            unsafe_allow_html=True,
        )

        DEMO_ROLES = [
            ("🏢 Fleet Mgr",      "fleet@transitops.com",    "fleet123"),
            ("🗺️ Dispatcher",     "dispatch@transitops.com", "dispatch123"),
            ("🛡️ Safety",         "safety@transitops.com",   "safety123"),
            ("💰 Finance",        "finance@transitops.com",  "finance123"),
        ]

        btn_cols = st.columns(4)
        for col, (label, demo_email, demo_pwd) in zip(btn_cols, DEMO_ROLES):
            with col:
                if st.button(label, use_container_width=True, key=f"quick_{demo_email}"):
                    st.session_state["login_email"]    = demo_email
                    st.session_state["login_password"] = demo_pwd
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "Email",
                placeholder="you@transitops.com",
                key="login_email",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "🔐 Sign In",
                use_container_width=True,
                type="primary",
            )

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                user = login(email.strip(), password)
                if user:
                    set_current_user(user)
                    st.session_state["current_page"] = "Dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please check your email and password.")

        with st.expander("🔑 Demo Credentials"):
            st.markdown(
                """
                | Role | Email | Password |
                |------|-------|----------|
                | Fleet Manager | fleet@transitops.com | fleet123 |
                | Dispatcher | dispatch@transitops.com | dispatch123 |
                | Safety Officer | safety@transitops.com | safety123 |
                | Financial Analyst | finance@transitops.com | finance123 |
                """
            )


# ============================================================
# SIDEBAR ROUTER
# ============================================================
def show_sidebar(user: dict) -> str:
    """
    Render sidebar and return the selected page name.
    Navigation is purely Python — no Streamlit page routing.
    """
    from app.auth.rbac import get_accessible_modules, SIDEBAR_ITEMS

    with st.sidebar:
        # Brand
        st.markdown(
            "<h2 style='color: #f59e0b; margin-bottom: 0;'>🚛 TransitOps</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: #9ca3af; font-size: 0.8rem; margin-top: 0;'>Smart Transport Operations</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        # User info
        st.markdown(
            f"""
            <div class="sidebar-user-info">
                <p class="sidebar-user-name">👤 {user['name']}</p>
                <p class="sidebar-user-role">{user['role_name']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation buttons
        accessible = get_accessible_modules(user["role_name"])
        current = st.session_state.get("current_page", "Dashboard")

        for item in accessible:
            is_active = current == item["module"]
            label = f"{item['icon']}  {item['label']}"
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{item['module']}", use_container_width=True, type=btn_type):
                st.session_state["current_page"] = item["module"]
                st.rerun()

        st.divider()

        # Logout
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()
            st.session_state["current_page"] = "Dashboard"
            st.rerun()

    return st.session_state.get("current_page", "Dashboard")


# ============================================================
# MAIN APP
# ============================================================
if not is_authenticated():
    show_login()
else:
    user = get_current_user()
    log.debug("Active user: %s (%s)", user["email"], user["role_name"])
    current_page = show_sidebar(user)
    route_to_page(current_page, user)
