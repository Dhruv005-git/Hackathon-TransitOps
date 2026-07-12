"""
frontend/pages/page_trips.py — Phase 3 + RBAC enforcement

Permissions enforced:
  Fleet Manager  → view only (no create/dispatch — operations are Dispatcher's job)
  Dispatcher     → full workflow (create/dispatch/complete/cancel/edit draft)
  Safety Officer → view only
  Financial Analyst → view only
"""
from __future__ import annotations
import streamlit as st
import pandas as pd
from pydantic import ValidationError

from app.constants import TripStatus
from app.schemas.trip_schema import TripCreate, TripUpdate, TripComplete
from app.services.trip_service import (
    get_all_trips, get_trip_by_id, create_trip, update_trip,
    dispatch_trip, complete_trip, cancel_trip,
    get_trip_summary, get_available_vehicles, get_available_drivers,
)
from frontend.components.auth_guard import can

_KEY_EDIT     = "trip_edit_id"
_KEY_COMPLETE = "trip_complete_id"
_KEY_CANCEL   = "trip_cancel_id"

def _init():
    for k in [_KEY_EDIT, _KEY_COMPLETE, _KEY_CANCEL]:
        if k not in st.session_state:
            st.session_state[k] = None


def _kpis(s: dict):
    cols = st.columns(6)
    items = [
        (s["total"],      "Total Trips",  "#3b82f6"),
        (s["draft"],      "Draft",        "#9ca3af"),
        (s["dispatched"], "Dispatched",   "#f59e0b"),
        (s["completed"],  "Completed",    "#10b981"),
        (s["cancelled"],  "Cancelled",    "#ef4444"),
        (f"Rs.{s['revenue']:,.0f}", "Revenue", "#8b5cf6"),
    ]
    for col, (val, label, color) in zip(cols, items):
        with col:
            st.markdown(
                f'<div style="background:#21252e;border-radius:10px;padding:14px 16px;'
                f'border-left:4px solid {color};margin-bottom:8px;">'
                f'<p style="margin:0;color:#9ca3af;font-size:0.75rem;text-transform:uppercase;'
                f'letter-spacing:.05em;">{label}</p>'
                f'<p style="margin:0;color:{color};font-size:1.5rem;font-weight:700;">{val}</p></div>',
                unsafe_allow_html=True,
            )


def _create_form():
    st.markdown("#### 🗺️ Create New Trip")
    avail_v = get_available_vehicles()
    avail_d = get_available_drivers()

    if not avail_v:
        st.warning("⚠️ No Available vehicles. Make a vehicle Available first.")
        return
    if not avail_d:
        st.warning("⚠️ No Available drivers.")
        return

    with st.form("create_trip_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            v_opts  = {v["label"]: v["id"] for v in avail_v}
            v_label = st.selectbox("Vehicle *", list(v_opts.keys()))
            source  = st.text_input("Origin *",      placeholder="e.g. Mumbai Depot")
            dest    = st.text_input("Destination *", placeholder="e.g. Pune Warehouse")
            cargo_w = st.number_input("Cargo Weight (kg)", min_value=0.0,
                                      max_value=50000.0, value=0.0, step=50.0)
        with c2:
            d_opts  = {d["label"]: d["id"] for d in avail_d}
            d_label = st.selectbox("Driver *", list(d_opts.keys()))
            dist    = st.number_input("Planned Distance (km) *", min_value=1.0,
                                      value=100.0, step=10.0)
            revenue = st.number_input("Revenue (Rs.) *", min_value=0.0,
                                      value=5000.0, step=500.0, format="%.0f")
            cargo_desc = st.text_input("Cargo Description",
                                       placeholder="e.g. Electronics")

        col_draft, col_dispatch = st.columns(2)
        with col_draft:
            save_draft = st.form_submit_button("💾 Save as Draft",
                                               use_container_width=True)
        with col_dispatch:
            dispatch_now = st.form_submit_button("🚀 Create & Dispatch",
                                                 type="primary", use_container_width=True)

    action = "draft" if save_draft else ("dispatch" if dispatch_now else None)
    if action:
        chosen_d = next((d for d in avail_d if d["id"] == d_opts.get(d_label)), None)
        if chosen_d and chosen_d.get("license_expired") and action == "dispatch":
            st.error("🔴 Selected driver has an EXPIRED license. Cannot dispatch.")
            return
        try:
            data  = TripCreate(
                vehicle_id=v_opts[v_label], driver_id=d_opts[d_label],
                source=source, destination=dest,
                cargo_weight_kg=cargo_w, cargo_description=cargo_desc,
                planned_distance_km=dist, revenue=revenue,
            )
            trip = create_trip(data)
            if action == "dispatch":
                trip = dispatch_trip(trip["id"])
                st.success(f"🚀 Trip **{trip['trip_code']}** dispatched! "
                           f"{trip['vehicle_reg']} + {trip['driver_name']} en route.")
            else:
                st.success(f"💾 Trip **{trip['trip_code']}** saved as Draft.")
            st.rerun()
        except ValidationError as e:
            for err in e.errors(): st.error(f"⚠️ {err['msg']}")
        except ValueError as e:
            st.error(f"⚠️ {e}")


def _trip_table(trips: list[dict]):
    if not trips:
        st.info("No trips match the selected filter.")
        return
    df = pd.DataFrame([{
        "Trip Code":  t["trip_code"],
        "Route":      f"{t['source']} → {t['destination']}",
        "Vehicle":    t["vehicle_reg"],
        "Driver":     t["driver_name"],
        "Cargo (kg)": f"{t['cargo_weight_kg']:,.0f}",
        "Dist. (km)": f"{t['planned_distance_km']:,.0f}",
        "Revenue":    f"Rs.{t['revenue']:,.0f}",
        "Status":     t["status"],
    } for t in trips])

    def cs(v):
        c = {"Draft":"color:#9ca3af;font-weight:700;","Dispatched":"color:#f59e0b;font-weight:700;",
             "Completed":"color:#10b981;font-weight:700;","Cancelled":"color:#ef4444;font-weight:700;"}
        return c.get(v, "")

    st.dataframe(df.style.map(cs, subset=["Status"]),
                 use_container_width=True, hide_index=True)


def _trip_selection_card(t: dict) -> str:
    status_cls = {
        "Draft":      "sc-badge-blue",
        "Dispatched": "sc-badge-yellow",
        "Completed":  "sc-badge-green",
        "Cancelled":  "sc-badge-red",
    }.get(t["status"], "sc-badge-gray")
    return f"""
    <div class="selection-card">
        <div class="sc-title">🗺️ {t['trip_code']}</div>
        <span class="sc-meta"><strong>Route:</strong> {t['source']} → {t['destination']}</span>
        <span class="sc-meta"><strong>Vehicle:</strong> {t['vehicle_reg']}</span>
        <span class="sc-meta"><strong>Driver:</strong> {t['driver_name']}</span>
        <span class="sc-meta"><strong>Cargo:</strong> {t['cargo_weight_kg']:,.0f} kg</span>
        <span class="sc-meta"><strong>Revenue:</strong> Rs.{t['revenue']:,.0f}</span>
        <span class="sc-badge {status_cls}">{t['status']}</span>
    </div>
    """


def _actions_panel(trips: list[dict]):
    """Only rendered if the user has at least one trip action permission."""
    has_any = any(can(a) for a in [
        "trips.dispatch", "trips.complete", "trips.cancel", "trips.edit_draft"
    ])
    if not has_any or not trips:
        return

    st.markdown("---")
    st.markdown("#### 🔧 Trip Actions")
    options    = {f"{t['trip_code']}  [{t['status']}]  {t['source']}→{t['destination']}": t
                  for t in trips}
    chosen_lbl = st.selectbox("Select trip:", list(options.keys()), key="trip_select")
    t          = options[chosen_lbl]

    # Selection card
    st.markdown(_trip_selection_card(t), unsafe_allow_html=True)

    # Action buttons based on status + permissions
    active_btns = []
    if can("trips.dispatch")   and t["status"] == TripStatus.DRAFT:      active_btns.append("dispatch")
    if can("trips.complete")   and t["status"] == TripStatus.DISPATCHED: active_btns.append("complete")
    if can("trips.cancel")     and t["status"] in (TripStatus.DRAFT, TripStatus.DISPATCHED): active_btns.append("cancel")
    if can("trips.edit_draft") and t["status"] == TripStatus.DRAFT:      active_btns.append("edit")

    if active_btns:
        bcols = st.columns(len(active_btns))
        for col, action in zip(bcols, active_btns):
            with col:
                if action == "dispatch":
                    if st.button("🚀  Dispatch", use_container_width=True, type="primary",
                                 key="trip_dispatch_btn"):
                        try:
                            dispatch_trip(t["id"])
                            st.success("✅ Trip dispatched!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                elif action == "complete":
                    if st.button("✅  Complete", use_container_width=True, type="primary",
                                 key="trip_complete_btn"):
                        st.session_state[_KEY_COMPLETE] = t["id"]
                        st.session_state[_KEY_CANCEL]   = None
                        st.rerun()
                elif action == "cancel":
                    if st.button("❌  Cancel Trip", use_container_width=True,
                                 key="trip_cancel_btn"):
                        st.session_state[_KEY_CANCEL]   = t["id"]
                        st.session_state[_KEY_COMPLETE] = None
                        st.rerun()
                elif action == "edit":
                    if st.button("✏️  Edit Draft", use_container_width=True,
                                 key="trip_edit_btn"):
                        st.session_state[_KEY_EDIT]    = t["id"]
                        st.session_state[_KEY_COMPLETE]= None
                        st.session_state[_KEY_CANCEL]  = None
                        st.rerun()
    elif t["status"] in (TripStatus.COMPLETED, TripStatus.CANCELLED):
        st.info(f"This trip is **{t['status']}** — no further actions available.")

    # Complete form
    if st.session_state.get(_KEY_COMPLETE) == t["id"]:
        st.markdown("---")
        st.markdown(f"**Complete Trip: {t['trip_code']}**")
        with st.form("complete_form"):
            fuel = st.number_input("Fuel Consumed (L) — optional",
                                   min_value=0.0, value=0.0, step=1.0)
            odo  = st.number_input("Final Odometer (km) — optional",
                                   min_value=0.0, value=0.0, step=10.0)
            c1, c2 = st.columns(2)
            with c1: confirm  = st.form_submit_button("✅ Confirm Complete",
                                                       type="primary", use_container_width=True)
            with c2: cancel_f = st.form_submit_button("✖ Cancel", use_container_width=True)

        if confirm:
            try:
                complete_trip(t["id"], TripComplete(
                    fuel_consumed_l=fuel if fuel > 0 else None,
                    final_odometer =odo  if odo  > 0 else None,
                ))
                st.success(f"✅ Trip **{t['trip_code']}** completed!")
                st.session_state[_KEY_COMPLETE] = None
                st.rerun()
            except ValueError as e:
                st.error(str(e))
        if cancel_f:
            st.session_state[_KEY_COMPLETE] = None
            st.rerun()

    # Cancel confirmation
    if st.session_state.get(_KEY_CANCEL) == t["id"]:
        st.warning(f"⚠️ Cancel trip **{t['trip_code']}**? "
                   "If Dispatched, vehicle and driver will be released.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, Cancel", use_container_width=True,
                         key="trip_cancel_confirm"):
                try:
                    cancel_trip(t["id"])
                    st.success("Trip cancelled.")
                    st.session_state[_KEY_CANCEL] = None
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        with c2:
            if st.button("Keep Trip", use_container_width=True, key="trip_cancel_abort"):
                st.session_state[_KEY_CANCEL] = None
                st.rerun()

    # Edit draft
    if st.session_state.get(_KEY_EDIT) == t["id"]:
        st.markdown("---")
        st.markdown(f"**Edit Draft: {t['trip_code']}**")
        with st.form("edit_trip_form"):
            c1, c2 = st.columns(2)
            with c1:
                src  = st.text_input("Origin",      value=t["source"])
                dst  = st.text_input("Destination", value=t["destination"])
                dist = st.number_input("Distance (km)", min_value=1.0,
                                       value=float(t["planned_distance_km"]), step=10.0)
            with c2:
                cw   = st.number_input("Cargo (kg)",    min_value=0.0,
                                       value=float(t["cargo_weight_kg"]), step=50.0)
                rev  = st.number_input("Revenue (Rs.)", min_value=0.0,
                                       value=float(t["revenue"]), step=500.0, format="%.0f")
            c1b, c2b = st.columns(2)
            with c1b: save = st.form_submit_button("💾 Save", type="primary",
                                                    use_container_width=True)
            with c2b: canc = st.form_submit_button("✖ Cancel", use_container_width=True)

        if save:
            try:
                update_trip(t["id"], TripUpdate(
                    source=src, destination=dst,
                    cargo_weight_kg=cw, planned_distance_km=dist, revenue=rev,
                ))
                st.success("Draft updated.")
                st.session_state[_KEY_EDIT] = None
                st.rerun()
            except (ValidationError, ValueError) as e:
                st.error(str(e))
        if canc:
            st.session_state[_KEY_EDIT] = None
            st.rerun()


def render():
    _init()
    st.markdown('<div class="page-header"><h1 class="page-title">🗺️ Trip Dispatcher</h1></div>',
                unsafe_allow_html=True)

    _kpis(get_trip_summary())
    st.markdown("<br>", unsafe_allow_html=True)

    tabs = ["📋 All Trips"]
    if can("trips.create"):
        tabs.append("➕ Create Trip")

    rendered_tabs = st.tabs(tabs)
    tab_list = rendered_tabs[0]
    tab_new  = rendered_tabs[1] if len(rendered_tabs) > 1 else None

    if tab_new:
        with tab_new:
            _create_form()

    with tab_list:
        if not can("trips.create") and not can("trips.dispatch"):
            st.info("🔒 You have **view-only** access to Trips.")

        status_filter = st.selectbox("Filter by Status",
                                     ["All"] + [s.value for s in TripStatus],
                                     key="trip_status_filter")
        trips = get_all_trips(status_filter=status_filter)
        st.caption(f"{len(trips)} trip(s) found")
        _trip_table(trips)
        _actions_panel(trips)
