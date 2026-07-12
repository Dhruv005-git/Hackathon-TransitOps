"""
frontend/pages/page_fleet.py

Purpose:
    Vehicle Registry page — Phase 2 full CRUD implementation.
    Add, Edit, Delete, Search, Filter with unique registration validation.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st
import pandas as pd

from app.auth.rbac import can_edit
from app.services.auth_service import get_current_user
from app.services.vehicle_service import (
    list_vehicles,
    create_vehicle,
    update_vehicle,
    delete_vehicle,
)
from app.constants import VehicleStatus, VehicleType, VEHICLE_STATUS_COLORS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _color_status(val: str) -> str:
    color = VEHICLE_STATUS_COLORS.get(val, "#e6e6e6")
    return f"color: {color}; font-weight: 600;"


def _status_badge(status: str) -> str:
    color = VEHICLE_STATUS_COLORS.get(status, "#6b7280")
    return (
        f'<span style="background:{color}22; color:{color}; '
        f'padding:2px 10px; border-radius:12px; font-size:0.78rem; '
        f'font-weight:600; border:1px solid {color}66;">{status}</span>'
    )


# ---------------------------------------------------------------------------
# Sub-forms
# ---------------------------------------------------------------------------

def _add_vehicle_form() -> None:
    """Expander form to add a new vehicle."""
    with st.expander("➕ Add New Vehicle", expanded=st.session_state.get("fleet_add_open", False)):
        with st.form("form_add_vehicle", clear_on_submit=True):
            c1, c2 = st.columns(2)
            reg_no       = c1.text_input("Registration No *", placeholder="MH12AB1234")
            model_name   = c2.text_input("Model Name *",       placeholder="Tata Ace")
            v_type       = c1.selectbox("Type *", [t.value for t in VehicleType])
            capacity     = c2.number_input("Max Capacity (kg) *", min_value=0.1, value=1000.0, step=50.0)
            odometer     = c1.number_input("Odometer (km)",       min_value=0.0, value=0.0,    step=100.0)
            acq_cost     = c2.number_input("Acquisition Cost (₹) *", min_value=0.0, value=500000.0, step=10000.0)
            status       = c1.selectbox("Status", [s.value for s in VehicleStatus])

            submitted = st.form_submit_button("✅ Add Vehicle", use_container_width=True, type="primary")
            if submitted:
                try:
                    create_vehicle(
                        registration_no=reg_no,
                        model_name=model_name,
                        vehicle_type=v_type,
                        max_capacity_kg=capacity,
                        odometer=odometer,
                        acquisition_cost=acq_cost,
                        status=status,
                    )
                    st.success(f"Vehicle **{reg_no.strip().upper()}** added successfully!")
                    st.session_state["fleet_add_open"] = False
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _edit_vehicle_form(vehicles: list) -> None:
    """Expander form to edit an existing vehicle."""
    if not vehicles:
        return

    with st.expander("✏️ Edit Vehicle", expanded=False):
        options = {f"{v.registration_no} — {v.model_name}": v for v in vehicles}
        selected_label = st.selectbox("Select vehicle to edit", list(options.keys()), key="edit_vehicle_select")
        v = options[selected_label]

        with st.form("form_edit_vehicle"):
            c1, c2 = st.columns(2)
            reg_no    = c1.text_input("Registration No *", value=v.registration_no)
            model_name = c2.text_input("Model Name *",     value=v.model_name)
            v_type    = c1.selectbox("Type *", [t.value for t in VehicleType],
                                     index=[t.value for t in VehicleType].index(v.type) if v.type in [t.value for t in VehicleType] else 0)
            capacity  = c2.number_input("Max Capacity (kg) *", min_value=0.1, value=float(v.max_capacity_kg), step=50.0)
            odometer  = c1.number_input("Odometer (km)",       min_value=0.0, value=float(v.odometer),        step=100.0)
            acq_cost  = c2.number_input("Acquisition Cost (₹) *", min_value=0.0, value=float(v.acquisition_cost), step=10000.0)
            all_statuses = [s.value for s in VehicleStatus]
            status    = c1.selectbox("Status", all_statuses,
                                     index=all_statuses.index(v.status) if v.status in all_statuses else 0)

            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            if submitted:
                try:
                    update_vehicle(
                        v.id,
                        registration_no=reg_no,
                        model_name=model_name,
                        vehicle_type=v_type,
                        max_capacity_kg=capacity,
                        odometer=odometer,
                        acquisition_cost=acq_cost,
                        status=status,
                    )
                    st.success("Vehicle updated successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _delete_vehicle_form(vehicles: list) -> None:
    """Expander form to delete a vehicle."""
    if not vehicles:
        return

    with st.expander("🗑️ Delete Vehicle", expanded=False):
        options = {f"{v.registration_no} — {v.model_name}": v for v in vehicles}
        selected_label = st.selectbox("Select vehicle to delete", list(options.keys()), key="delete_vehicle_select")
        v = options[selected_label]

        st.warning(
            f"⚠️ You are about to permanently delete **{v.registration_no}** ({v.model_name}). "
            "This cannot be undone."
        )
        confirm = st.checkbox("I confirm I want to delete this vehicle", key="confirm_delete_vehicle")
        if st.button("🗑️ Delete Vehicle", type="primary", disabled=not confirm, use_container_width=True):
            try:
                delete_vehicle(v.id)
                st.success(f"Vehicle **{v.registration_no}** deleted.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">🚛 Vehicle Registry</h1></div>',
        unsafe_allow_html=True,
    )

    user = get_current_user()
    editable = can_edit(user["role_name"], "Fleet") if user else False

    # ---- Search & Filter bar ----
    col_search, col_filter = st.columns([3, 1])
    search_term    = col_search.text_input("🔍 Search by Registration No or Model", placeholder="e.g. MH12 or Tata", label_visibility="collapsed")
    status_options = ["All"] + [s.value for s in VehicleStatus]
    status_filter  = col_filter.selectbox("Filter by Status", status_options, label_visibility="collapsed")

    # ---- Fetch vehicles ----
    vehicles = list_vehicles(search=search_term, status_filter=status_filter)

    # ---- Summary metrics ----
    total       = len(vehicles)
    available   = sum(1 for v in vehicles if v.status == VehicleStatus.AVAILABLE)
    on_trip     = sum(1 for v in vehicles if v.status == VehicleStatus.ON_TRIP)
    in_shop     = sum(1 for v in vehicles if v.status == VehicleStatus.IN_SHOP)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Vehicles", total)
    m2.metric("Available",      available,  delta=None)
    m3.metric("On Trip",        on_trip)
    m4.metric("In Shop",        in_shop)

    st.divider()

    # ---- Vehicle Table ----
    if vehicles:
        df = pd.DataFrame([{
            "ID":                 v.id,
            "Reg No":             v.registration_no,
            "Model":              v.model_name,
            "Type":               v.type,
            "Capacity (kg)":      f"{v.max_capacity_kg:,.0f}",
            "Odometer (km)":      f"{v.odometer:,.0f}",
            "Acq. Cost (₹)":     f"₹{v.acquisition_cost:,.0f}",
            "Status":             v.status,
        } for v in vehicles])

        st.dataframe(
            df.drop(columns=["ID"]).style.map(_color_status, subset=["Status"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No vehicles match your search/filter. Try adjusting your criteria.")

    # ---- CRUD Forms (edit-access only) ----
    if editable:
        st.divider()
        st.markdown("### Manage Vehicles")
        _add_vehicle_form()
        if vehicles:
            _edit_vehicle_form(vehicles)
            _delete_vehicle_form(vehicles)
    else:
        st.info("🔒 You have view-only access to the Vehicle Registry.")
