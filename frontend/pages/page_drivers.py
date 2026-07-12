"""
frontend/pages/page_drivers.py

Purpose:
    Driver Management page — Phase 2 full CRUD implementation.
    Add, Edit, Delete, Search, Filter with license validation.

Exposes:
    render() — called by app.py router.
"""

import datetime
import streamlit as st
import pandas as pd

from app.auth.rbac import can_edit
from app.services.auth_service import get_current_user
from app.services.driver_service import (
    list_drivers,
    create_driver,
    update_driver,
    delete_driver,
)
from app.constants import DriverStatus, LicenseCategory, DRIVER_STATUS_COLORS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _color_status(val: str) -> str:
    color = DRIVER_STATUS_COLORS.get(val, "#e6e6e6")
    return f"color: {color}; font-weight: 600;"


def _color_license(val: str) -> str:
    return "color: #10b981; font-weight:600;" if val == "✅ Valid" else "color: #ef4444; font-weight:600;"


def _color_score(val) -> str:
    try:
        score = float(str(val).replace("%", ""))
    except ValueError:
        return ""
    if score >= 80:
        return "color: #10b981; font-weight:600;"
    elif score >= 50:
        return "color: #f59e0b; font-weight:600;"
    return "color: #ef4444; font-weight:600;"


# ---------------------------------------------------------------------------
# Sub-forms
# ---------------------------------------------------------------------------

def _add_driver_form() -> None:
    """Expander form to add a new driver."""
    with st.expander("➕ Add New Driver", expanded=st.session_state.get("driver_add_open", False)):
        with st.form("form_add_driver", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name         = c1.text_input("Full Name *",       placeholder="Ravi Kumar")
            contact_no   = c2.text_input("Contact No *",      placeholder="+91 98765 43210")
            license_no   = c1.text_input("License No *",      placeholder="MH0120231234567")
            lic_category = c2.selectbox("License Category *", [lc.value for lc in LicenseCategory])
            lic_expiry   = c1.date_input(
                "License Expiry *",
                value=datetime.date.today() + datetime.timedelta(days=365),
                min_value=datetime.date.today(),
            )
            safety_score = c2.slider("Safety Score", 0, 100, 100, step=1)
            status       = c1.selectbox("Status", [s.value for s in DriverStatus])

            submitted = st.form_submit_button("✅ Add Driver", use_container_width=True, type="primary")
            if submitted:
                try:
                    create_driver(
                        name=name,
                        license_no=license_no,
                        license_category=lic_category,
                        license_expiry=lic_expiry,
                        contact_no=contact_no,
                        safety_score=float(safety_score),
                        status=status,
                    )
                    st.success(f"Driver **{name.strip()}** added successfully!")
                    st.session_state["driver_add_open"] = False
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _edit_driver_form(drivers: list) -> None:
    """Expander form to edit an existing driver."""
    if not drivers:
        return

    with st.expander("✏️ Edit Driver", expanded=False):
        options = {f"{d.name} ({d.license_no})": d for d in drivers}
        selected_label = st.selectbox("Select driver to edit", list(options.keys()), key="edit_driver_select")
        d = options[selected_label]

        with st.form("form_edit_driver"):
            c1, c2 = st.columns(2)
            name         = c1.text_input("Full Name *",       value=d.name)
            contact_no   = c2.text_input("Contact No *",      value=d.contact_no)
            license_no   = c1.text_input("License No *",      value=d.license_no)
            all_cats     = [lc.value for lc in LicenseCategory]
            lic_category = c2.selectbox(
                "License Category *", all_cats,
                index=all_cats.index(d.license_category) if d.license_category in all_cats else 0,
            )
            lic_expiry   = c1.date_input("License Expiry *", value=d.license_expiry)
            safety_score = c2.slider("Safety Score", 0, 100, int(d.safety_score), step=1)
            all_statuses = [s.value for s in DriverStatus]
            status       = c1.selectbox(
                "Status", all_statuses,
                index=all_statuses.index(d.status) if d.status in all_statuses else 0,
            )

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            if submitted:
                try:
                    update_driver(
                        d.id,
                        name=name,
                        license_no=license_no,
                        license_category=lic_category,
                        license_expiry=lic_expiry,
                        contact_no=contact_no,
                        safety_score=float(safety_score),
                        status=status,
                    )
                    st.success("Driver updated successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _delete_driver_form(drivers: list) -> None:
    """Expander form to delete a driver."""
    if not drivers:
        return

    with st.expander("🗑️ Delete Driver", expanded=False):
        options = {f"{d.name} ({d.license_no})": d for d in drivers}
        selected_label = st.selectbox("Select driver to delete", list(options.keys()), key="delete_driver_select")
        d = options[selected_label]

        st.warning(
            f"⚠️ You are about to permanently delete driver **{d.name}** (License: {d.license_no}). "
            "This cannot be undone."
        )
        confirm = st.checkbox("I confirm I want to delete this driver", key="confirm_delete_driver")
        if st.button("🗑️ Delete Driver", type="primary", disabled=not confirm, use_container_width=True):
            try:
                delete_driver(d.id)
                st.success(f"Driver **{d.name}** deleted.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">👤 Driver Management</h1></div>',
        unsafe_allow_html=True,
    )

    user     = get_current_user()
    editable = can_edit(user["role_name"], "Drivers") if user else False
    today    = datetime.date.today()

    # ---- Search & Filter bar ----
    col_search, col_filter = st.columns([3, 1])
    search_term    = col_search.text_input("🔍 Search by Name or License No", placeholder="e.g. Ravi or MH01", label_visibility="collapsed")
    status_options = ["All"] + [s.value for s in DriverStatus]
    status_filter  = col_filter.selectbox("Filter by Status", status_options, label_visibility="collapsed")

    # ---- Fetch drivers ----
    drivers = list_drivers(search=search_term, status_filter=status_filter)

    # ---- Summary metrics ----
    total      = len(drivers)
    available  = sum(1 for d in drivers if d.status == DriverStatus.AVAILABLE)
    on_trip    = sum(1 for d in drivers if d.status == DriverStatus.ON_TRIP)
    suspended  = sum(1 for d in drivers if d.status == DriverStatus.SUSPENDED)
    expired    = sum(1 for d in drivers if d.license_expiry < today)
    expiring   = sum(1 for d in drivers if today <= d.license_expiry <= today + datetime.timedelta(days=30))

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Total Drivers", total)
    m2.metric("Available",     available)
    m3.metric("On Trip",       on_trip)
    m4.metric("Suspended",     suspended)
    m5.metric("⚠️ Expiring Soon",  expiring)
    m6.metric("❌ Expired Licenses", expired)

    st.divider()

    # ---- Driver Table ----
    if drivers:
        df = pd.DataFrame([{
            "ID":             d.id,
            "Name":           d.name,
            "License No":     d.license_no,
            "Category":       d.license_category,
            "Expiry":         d.license_expiry.strftime("%d %b %Y"),
            "Contact":        d.contact_no,
            "Safety Score":   f"{d.safety_score:.0f}%",
            "Status":         d.status,
            "License":        "✅ Valid" if d.license_expiry >= today else "❌ Expired",
        } for d in drivers])

        st.dataframe(
            df.drop(columns=["ID"]).style
              .map(_color_status,  subset=["Status"])
              .map(_color_license, subset=["License"])
              .map(_color_score,   subset=["Safety Score"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No drivers match your search/filter. Try adjusting your criteria.")

    # ---- CRUD Forms (edit-access only) ----
    if editable:
        st.divider()
        st.markdown("### Manage Drivers")
        _add_driver_form()
        if drivers:
            _edit_driver_form(drivers)
            _delete_driver_form(drivers)
    else:
        st.info("🔒 You have view-only access to Driver Management.")
