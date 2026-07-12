"""
frontend/pages/page_fleet.py — Phase 2 + RBAC enforcement

Permissions enforced:
  Fleet Manager  → full CRUD + status change
  Dispatcher     → view only
  Safety Officer → view only
  Financial Analyst → view only
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from pydantic import ValidationError

from app.constants import VehicleStatus, VehicleType
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate
from app.services.vehicle_service import (
    get_all_vehicles, get_vehicle_by_id, create_vehicle,
    update_vehicle, delete_vehicle, get_fleet_summary,
)
from frontend.components.auth_guard import can

_KEY_EDIT = "fleet_edit_id"
_KEY_DEL  = "fleet_confirm_delete_id"

def _init():
    for k in [_KEY_EDIT, _KEY_DEL]:
        if k not in st.session_state:
            st.session_state[k] = None


def _show_kpis(summary: dict):
    cols = st.columns(5)
    items = [
        (summary["total"],     "Total Vehicles", "#3b82f6"),
        (summary["available"], "Available",       "#10b981"),
        (summary["on_trip"],   "On Trip",         "#f59e0b"),
        (summary["in_shop"],   "In Maintenance",  "#ef4444"),
        (summary["retired"],   "Retired",         "#6b7280"),
    ]
    for col, (val, label, color) in zip(cols, items):
        with col:
            st.markdown(
                f'<div style="background:#21252e;border-radius:10px;padding:14px 16px;'
                f'border-left:4px solid {color};margin-bottom:8px;">'
                f'<p style="margin:0;color:#9ca3af;font-size:0.75rem;text-transform:uppercase;'
                f'letter-spacing:.05em;">{label}</p>'
                f'<p style="margin:0;color:{color};font-size:1.6rem;font-weight:700;">{val}</p></div>',
                unsafe_allow_html=True,
            )


def _add_vehicle_form():
    st.markdown("#### ➕ Add New Vehicle")
    with st.form("add_vehicle_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            reg_no   = st.text_input("Registration No *", placeholder="e.g. MH-12-AB-1234")
            v_type   = st.selectbox("Vehicle Type *", [t.value for t in VehicleType])
            capacity = st.number_input("Max Capacity (kg) *", min_value=1.0,
                                       max_value=50000.0, value=1000.0, step=50.0)
        with c2:
            model    = st.text_input("Model Name *", placeholder="e.g. Tata Ace 2023")
            cost     = st.number_input("Acquisition Cost (₹) *", min_value=1.0,
                                       value=500000.0, step=10000.0, format="%.0f")
            odometer = st.number_input("Current Odometer (km)", min_value=0.0,
                                       value=0.0, step=100.0)
        submitted = st.form_submit_button("🚛 Add Vehicle", type="primary",
                                          use_container_width=True)
    if submitted:
        try:
            vehicle = create_vehicle(VehicleCreate(
                registration_no=reg_no, model_name=model, type=v_type,
                max_capacity_kg=capacity, acquisition_cost=cost, odometer=odometer,
            ))
            st.success(f"✅ Vehicle **{vehicle['registration_no']}** added!")
            st.rerun()
        except ValidationError as e:
            for err in e.errors(): st.error(f"⚠️ {err['msg']}")
        except ValueError as e:
            st.error(f"⚠️ {e}")


def _edit_vehicle_form(vehicle: dict):
    st.markdown(f"#### ✏️ Editing: **{vehicle['registration_no']}** — {vehicle['model_name']}")
    with st.form("edit_vehicle_form"):
        c1, c2 = st.columns(2)
        with c1:
            model    = st.text_input("Model Name",    value=vehicle["model_name"])
            v_type   = st.selectbox("Vehicle Type",
                                    [t.value for t in VehicleType],
                                    index=[t.value for t in VehicleType].index(vehicle["type"]))
            capacity = st.number_input("Max Capacity (kg)", min_value=1.0, max_value=50000.0,
                                       value=float(vehicle["max_capacity_kg"]), step=50.0)
        with c2:
            status   = st.selectbox("Status",
                                    [s.value for s in VehicleStatus],
                                    index=[s.value for s in VehicleStatus].index(vehicle["status"]))
            cost     = st.number_input("Acquisition Cost (₹)", min_value=1.0,
                                       value=float(vehicle["acquisition_cost"]),
                                       step=10000.0, format="%.0f")
            odometer = st.number_input("Odometer (km)", min_value=0.0,
                                       value=float(vehicle["odometer"]), step=100.0)
        cs, cc = st.columns(2)
        with cs: save   = st.form_submit_button("💾 Save Changes", type="primary",
                                                 use_container_width=True)
        with cc: cancel = st.form_submit_button("✖ Cancel", use_container_width=True)

    if save:
        try:
            update_vehicle(vehicle["id"], VehicleUpdate(
                model_name=model, type=v_type, max_capacity_kg=capacity,
                acquisition_cost=cost, odometer=odometer, status=status,
            ))
            st.success("✅ Vehicle updated!")
            st.session_state[_KEY_EDIT] = None
            st.rerun()
        except (ValidationError, ValueError) as e:
            st.error(str(e))
    if cancel:
        st.session_state[_KEY_EDIT] = None
        st.rerun()


def _vehicle_table(vehicles: list[dict]):
    if not vehicles:
        st.info("No vehicles match your filters.")
        return
    df = pd.DataFrame([{
        "Reg No":        v["registration_no"],
        "Model":         v["model_name"],
        "Type":          v["type"],
        "Capacity (kg)": f"{v['max_capacity_kg']:,.0f}",
        "Odometer (km)": f"{v['odometer']:,.0f}",
        "Acq. Cost (₹)": f"₹{v['acquisition_cost']:,.0f}",
        "Status":        v["status"],
    } for v in vehicles])

    def cs(v):
        c = {"Available":"color:#10b981;font-weight:700;","On Trip":"color:#f59e0b;font-weight:700;",
             "In Shop":"color:#ef4444;font-weight:700;","Retired":"color:#6b7280;font-weight:700;"}
        return c.get(v, "")

    st.dataframe(df.style.map(cs, subset=["Status"]),
                 use_container_width=True, hide_index=True)


def _selection_card(v: dict) -> str:
    status_cls = {
        "Available": "sc-badge-green", "On Trip": "sc-badge-yellow",
        "In Shop": "sc-badge-red",    "Retired": "sc-badge-gray",
    }.get(v["status"], "sc-badge-gray")
    return f"""
    <div class="selection-card">
        <div class="sc-title">🚛 {v['registration_no']}</div>
        <span class="sc-meta"><strong>Model:</strong> {v['model_name']}</span>
        <span class="sc-meta"><strong>Type:</strong> {v['type']}</span>
        <span class="sc-meta"><strong>Capacity:</strong> {v['max_capacity_kg']:,.0f} kg</span>
        <span class="sc-meta"><strong>Odometer:</strong> {v['odometer']:,.0f} km</span>
        <span class="sc-meta"><strong>Cost:</strong> Rs.{v['acquisition_cost']:,.0f}</span>
        <span class="sc-badge {status_cls}">{v['status']}</span>
    </div>
    """


def _actions_panel(vehicles: list[dict]):
    """Only rendered when the user has at least one fleet action permission."""
    if not vehicles:
        return
    can_edit_v   = can("fleet.edit")
    can_delete_v = can("fleet.delete")
    can_status   = can("fleet.status")

    if not any([can_edit_v, can_delete_v, can_status]):
        return

    st.markdown("---")
    st.markdown("#### 🔧 Vehicle Actions")

    options = {f"{v['registration_no']} — {v['model_name']}": v for v in vehicles}
    chosen  = options[st.selectbox("Select vehicle:", list(options.keys()),
                                   key="fleet_select")]

    # Selection card
    st.markdown(_selection_card(chosen), unsafe_allow_html=True)

    # Primary action buttons
    num_btns = sum([can_edit_v, can_delete_v])
    if num_btns:
        bcols = st.columns(max(num_btns, 1))
        idx   = 0
        if can_edit_v:
            with bcols[idx]:
                if st.button("✏️  Edit Vehicle", use_container_width=True,
                             type="primary", key="fleet_edit_btn"):
                    st.session_state[_KEY_EDIT] = chosen["id"]
                    st.session_state[_KEY_DEL]  = None
                    st.rerun()
            idx += 1
        if can_delete_v:
            with bcols[idx]:
                if st.button("🗑️  Delete / Retire", use_container_width=True,
                             key="fleet_del_btn"):
                    st.session_state[_KEY_DEL]  = chosen["id"]
                    st.session_state[_KEY_EDIT] = None
                    st.rerun()

    # Status change — own clean section
    if can_status:
        st.markdown("<hr class='actions-divider'>", unsafe_allow_html=True)
        st.markdown("**🔄 Change Vehicle Status**")
        sc1, sc2 = st.columns([3, 1])
        other = [s.value for s in VehicleStatus if s.value != chosen["status"]]
        with sc1:
            new_s = st.selectbox("New status:", ["(keep current)"] + other,
                                 key="fleet_status_sel", label_visibility="collapsed")
        with sc2:
            if st.button("Apply", use_container_width=True, key="fleet_status_btn"):
                if new_s != "(keep current)":
                    try:
                        update_vehicle(chosen["id"], VehicleUpdate(status=new_s))
                        st.success(f"✅ Status updated → **{new_s}**")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("Select a status to apply.")

    # Delete confirmation
    if st.session_state.get(_KEY_DEL) == chosen["id"]:
        st.warning(f"⚠️ Remove **{chosen['registration_no']}**? "
                   "Vehicles with trip history are Retired, not deleted.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, proceed", use_container_width=True,
                         key="fleet_del_confirm"):
                try:
                    action = delete_vehicle(chosen["id"])
                    st.success("Status → **Retired**" if action == "retired"
                               else f"'{chosen['registration_no']}' deleted.")
                    st.session_state[_KEY_DEL] = None
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        with c2:
            if st.button("❌ Cancel", use_container_width=True, key="fleet_del_cancel"):
                st.session_state[_KEY_DEL] = None
                st.rerun()

    # Edit form
    if st.session_state.get(_KEY_EDIT) and can_edit_v:
        st.markdown("---")
        vehicle = get_vehicle_by_id(st.session_state[_KEY_EDIT])
        if vehicle:
            _edit_vehicle_form(vehicle)
        else:
            st.session_state[_KEY_EDIT] = None



def render():
    _init()
    st.markdown('<div class="page-header"><h1 class="page-title">🚛 Vehicle Registry</h1></div>',
                unsafe_allow_html=True)

    _show_kpis(get_fleet_summary())
    st.markdown("<br>", unsafe_allow_html=True)

    # Build tab list dynamically based on permissions
    tabs = ["📋 All Vehicles"]
    if can("fleet.add"):
        tabs.append("➕ Add Vehicle")

    rendered_tabs = st.tabs(tabs)
    tab_list = rendered_tabs[0]
    tab_add  = rendered_tabs[1] if len(rendered_tabs) > 1 else None

    if tab_add:
        with tab_add:
            _add_vehicle_form()

    with tab_list:
        if not can("fleet.add") and not can("fleet.edit"):
            st.info("🔒 You have **view-only** access to the Vehicle Registry.")

        fc1, fc2 = st.columns(2)
        with fc1:
            type_filter = st.selectbox("Type", ["All"] + [t.value for t in VehicleType],
                                       key="fleet_type_filter")
        with fc2:
            status_filter = st.selectbox("Status", ["All"] + [s.value for s in VehicleStatus],
                                         key="fleet_status_filter")

        vehicles = get_all_vehicles(type_filter=type_filter, status_filter=status_filter)
        st.caption(f"{len(vehicles)} vehicle(s)")
        _vehicle_table(vehicles)
        _actions_panel(vehicles)
