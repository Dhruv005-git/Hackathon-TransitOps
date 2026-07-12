"""
frontend/pages/page_trips.py

Purpose:
    Trip Dispatcher page — full Phase 3 lifecycle implementation.
    Tab 1: Trip Dispatcher (CRUD: Create Draft, Dispatch, Complete, Cancel).
    Tab 2: Live Dispatch Board (Kanban-style status columns).

Exposes:
    render() — called by app.py router.
"""

import datetime
from typing import Optional

import streamlit as st
import pandas as pd

from app.auth.rbac import can_edit
from app.services.auth_service import get_current_user
from app.services.trip_service import (
    list_trips,
    create_draft,
    dispatch,
    complete,
    cancel,
    list_available_vehicles,
    list_available_drivers,
)
from app.services.vehicle_service import list_vehicles
from app.services.driver_service import list_drivers
from app.constants import (
    TripStatus,
    VehicleStatus,
    DriverStatus,
    TRIP_STATUS_COLORS,
    VEHICLE_STATUS_COLORS,
    DRIVER_STATUS_COLORS,
)
from app.database.engine import get_session
from app.models import Trip, Vehicle, Driver


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def _color_status(val: str) -> str:
    color = TRIP_STATUS_COLORS.get(val, "#9ca3af")
    return f"color: {color}; font-weight: 600;"


def _status_badge(status: str, colors: dict) -> str:
    color = colors.get(status, "#6b7280")
    return (
        f'<span style="background:{color}22; color:{color}; '
        f'padding:2px 10px; border-radius:12px; font-size:0.78rem; '
        f'font-weight:600; border:1px solid {color}66;">{status}</span>'
    )


def _trip_badge(status: str) -> str:
    return _status_badge(status, TRIP_STATUS_COLORS)


# ---------------------------------------------------------------------------
# Shared data loader
# ---------------------------------------------------------------------------

def _load_all_trips() -> tuple[list, dict, dict]:
    """Return (trips, vehicle_map, driver_map) — all detached from session."""
    with get_session() as session:
        trips    = session.query(Trip).order_by(Trip.created_at.desc()).all()
        vehicles = {v.id: v for v in session.query(Vehicle).all()}
        drivers  = {d.id: d for d in session.query(Driver).all()}
    return trips, vehicles, drivers


# ---------------------------------------------------------------------------
# Tab 1 helpers — forms
# ---------------------------------------------------------------------------

def _metrics_row(trips: list) -> None:
    total      = len(trips)
    draft      = sum(1 for t in trips if t.status == TripStatus.DRAFT)
    dispatched = sum(1 for t in trips if t.status == TripStatus.DISPATCHED)
    completed  = sum(1 for t in trips if t.status == TripStatus.COMPLETED)
    cancelled  = sum(1 for t in trips if t.status == TripStatus.CANCELLED)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Trips",  total)
    m2.metric("📝 Draft",      draft)
    m3.metric("🚀 Dispatched", dispatched)
    m4.metric("✅ Completed",  completed)
    m5.metric("❌ Cancelled",  cancelled)


def _trips_table(trips: list, vehicles: dict, drivers: dict) -> None:
    """Render the full trips dataframe with coloured status column."""
    if not trips:
        st.info("No trips match your search/filter.")
        return

    rows = []
    for t in trips:
        v = vehicles.get(t.vehicle_id)
        d = drivers.get(t.driver_id)
        rows.append({
            "Trip Code":      t.trip_code,
            "From → To":      f"{t.source} → {t.destination}",
            "Vehicle":        v.registration_no if v else "-",
            "Driver":         d.name if d else "-",
            "Cargo (kg)":     f"{t.cargo_weight_kg:,.0f}",
            "Distance (km)":  f"{t.planned_distance_km:,.0f}",
            "Revenue (₹)":    f"₹{t.revenue:,.0f}",
            "Status":         t.status,
            "Created":        t.created_at.strftime("%d %b %Y %H:%M") if t.created_at else "-",
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df.style.map(_color_status, subset=["Status"]),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# Form: Create Draft Trip
# ---------------------------------------------------------------------------

def _form_create_draft() -> None:
    """Expander form for creating a new Draft trip."""
    with st.expander("➕ Create Draft Trip", expanded=st.session_state.get("trip_create_open", False)):
        # Fetch selectable vehicles and drivers for the form
        available_vehicles = list_available_vehicles()
        all_vehicles       = list_vehicles()
        all_drivers        = list_available_drivers()

        if not all_vehicles:
            st.warning("No vehicles in the system. Add vehicles in the Fleet module first.")
            return

        with st.form("form_create_draft_trip", clear_on_submit=True):
            c1, c2 = st.columns(2)
            source      = c1.text_input("Origin *", placeholder="e.g. Mumbai")
            destination = c2.text_input("Destination *", placeholder="e.g. Pune")

            # Vehicle selector — show all vehicles but flag non-available ones
            vehicle_options = {
                f"{v.registration_no} — {v.model_name} ({v.status}) | Cap: {v.max_capacity_kg:,.0f} kg": v
                for v in all_vehicles
            }
            selected_v_label = c1.selectbox("Vehicle *", list(vehicle_options.keys()), key="create_vehicle_sel")
            selected_v       = vehicle_options[selected_v_label]

            # Driver selector — show available drivers
            if all_drivers:
                driver_options = {
                    f"{d.name} — {d.license_no} ({d.license_category}) | Score: {d.safety_score:.0f}": d
                    for d in all_drivers
                }
            else:
                driver_options = {}

            if driver_options:
                selected_d_label = c2.selectbox("Driver *", list(driver_options.keys()), key="create_driver_sel")
                selected_d       = driver_options[selected_d_label]
            else:
                c2.warning("No available drivers found.")
                selected_d = None

            cargo     = c1.number_input(
                f"Cargo Weight (kg) *  [Vehicle cap: {selected_v.max_capacity_kg:,.0f} kg]",
                min_value=0.1, value=500.0, step=50.0
            )
            distance  = c2.number_input("Planned Distance (km) *", min_value=1.0, value=100.0, step=10.0)
            revenue   = c1.number_input("Expected Revenue (₹) *",  min_value=0.0, value=10000.0, step=500.0)

            submitted = st.form_submit_button("📝 Save as Draft", use_container_width=True, type="primary")
            if submitted:
                if not source.strip() or not destination.strip():
                    st.error("Origin and Destination are required.")
                elif selected_d is None:
                    st.error("A driver must be selected to create a trip.")
                else:
                    try:
                        trip = create_draft(
                            source=source,
                            destination=destination,
                            vehicle_id=selected_v.id,
                            driver_id=selected_d.id,
                            cargo_weight_kg=cargo,
                            planned_distance_km=distance,
                            revenue=revenue,
                        )
                        st.success(f"✅ Draft trip saved! Code: **{trip.trip_code}**")
                        st.session_state["trip_create_open"] = False
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))


# ---------------------------------------------------------------------------
# Form: Dispatch Trip
# ---------------------------------------------------------------------------

def _form_dispatch(trips: list, vehicles: dict, drivers: dict) -> None:
    """Expander form to dispatch a Draft trip."""
    draft_trips = [t for t in trips if t.status == TripStatus.DRAFT]

    with st.expander("🚀 Dispatch Trip", expanded=False):
        if not draft_trips:
            st.info("No Draft trips available to dispatch.")
            return

        options = {
            f"{t.trip_code} | {t.source} → {t.destination} | "
            f"{vehicles.get(t.vehicle_id).registration_no if vehicles.get(t.vehicle_id) else '?'} | "
            f"{drivers.get(t.driver_id).name if drivers.get(t.driver_id) else '?'}": t
            for t in draft_trips
        }

        with st.form("form_dispatch_trip"):
            selected_label = st.selectbox("Select Draft Trip to Dispatch", list(options.keys()))
            selected_trip  = options[selected_label]

            # Show pre-dispatch summary
            v = vehicles.get(selected_trip.vehicle_id)
            d = drivers.get(selected_trip.driver_id)

            col_v, col_d = st.columns(2)
            with col_v:
                st.markdown("**Vehicle at time of dispatch:**")
                if v:
                    v_color = VEHICLE_STATUS_COLORS.get(v.status, "#6b7280")
                    st.markdown(
                        f"🚛 `{v.registration_no}` — {v.model_name}  \n"
                        f"Status: <span style='color:{v_color};font-weight:600'>{v.status}</span>  \n"
                        f"Capacity: {v.max_capacity_kg:,.0f} kg",
                        unsafe_allow_html=True,
                    )
            with col_d:
                st.markdown("**Driver at time of dispatch:**")
                if d:
                    d_color   = DRIVER_STATUS_COLORS.get(d.status, "#6b7280")
                    today     = datetime.date.today()
                    lic_ok    = d.license_expiry >= today
                    lic_color = "#10b981" if lic_ok else "#ef4444"
                    st.markdown(
                        f"👤 {d.name} — `{d.license_no}` ({d.license_category})  \n"
                        f"Status: <span style='color:{d_color};font-weight:600'>{d.status}</span>  \n"
                        f"License: <span style='color:{lic_color};font-weight:600'>"
                        f"{'Valid' if lic_ok else 'EXPIRED'} ({d.license_expiry.strftime('%d %b %Y')})</span>  \n"
                        f"Safety Score: {d.safety_score:.0f}/100",
                        unsafe_allow_html=True,
                    )

            submitted = st.form_submit_button("🚀 Confirm Dispatch", use_container_width=True, type="primary")
            if submitted:
                try:
                    dispatch(selected_trip.id)
                    st.success(
                        f"✅ Trip **{selected_trip.trip_code}** dispatched! "
                        f"Vehicle and driver are now On Trip."
                    )
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Dispatch failed: {e}")


# ---------------------------------------------------------------------------
# Form: Complete Trip
# ---------------------------------------------------------------------------

def _form_complete(trips: list, vehicles: dict) -> None:
    """Expander form to complete a Dispatched trip."""
    dispatched_trips = [t for t in trips if t.status == TripStatus.DISPATCHED]

    with st.expander("✅ Complete Trip", expanded=False):
        if not dispatched_trips:
            st.info("No Dispatched trips to complete.")
            return

        options = {
            f"{t.trip_code} | {t.source} → {t.destination}": t
            for t in dispatched_trips
        }

        with st.form("form_complete_trip"):
            selected_label = st.selectbox("Select Dispatched Trip to Complete", list(options.keys()))
            selected_trip  = options[selected_label]

            v = vehicles.get(selected_trip.vehicle_id)
            current_odo = float(v.odometer) if v else 0.0

            c1, c2 = st.columns(2)
            fuel_consumed = c1.number_input(
                "Fuel Consumed (L)", min_value=0.0, value=0.0, step=1.0,
                help="Leave as 0 to skip fuel recording"
            )
            final_odo = c2.number_input(
                f"Final Odometer (km)  [Current: {current_odo:,.0f} km]",
                min_value=current_odo,
                value=current_odo + selected_trip.planned_distance_km,
                step=1.0,
            )

            submitted = st.form_submit_button("✅ Mark as Completed", use_container_width=True, type="primary")
            if submitted:
                try:
                    complete(
                        trip_id=selected_trip.id,
                        fuel_consumed_l=fuel_consumed if fuel_consumed > 0 else None,
                        final_odometer=final_odo if final_odo > current_odo else None,
                    )
                    st.success(
                        f"✅ Trip **{selected_trip.trip_code}** completed! "
                        f"Vehicle and driver are now Available."
                    )
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Could not complete trip: {e}")


# ---------------------------------------------------------------------------
# Form: Cancel Trip
# ---------------------------------------------------------------------------

def _form_cancel(trips: list) -> None:
    """Expander form to cancel a Draft or Dispatched trip."""
    cancellable = [t for t in trips if t.status in (TripStatus.DRAFT, TripStatus.DISPATCHED)]

    with st.expander("❌ Cancel Trip", expanded=False):
        if not cancellable:
            st.info("No Draft or Dispatched trips available to cancel.")
            return

        options = {
            f"{t.trip_code} | {t.source} → {t.destination} [{t.status}]": t
            for t in cancellable
        }

        selected_label = st.selectbox("Select Trip to Cancel", list(options.keys()), key="cancel_trip_select")
        selected_trip  = options[selected_label]

        if selected_trip.status == TripStatus.DISPATCHED:
            st.warning(
                f"⚠️ Trip **{selected_trip.trip_code}** is currently **Dispatched**. "
                "Cancelling will restore the vehicle and driver to Available."
            )
        else:
            st.info(f"Trip **{selected_trip.trip_code}** is a Draft — cancellation will not affect vehicle/driver status.")

        confirm = st.checkbox("I confirm I want to cancel this trip", key="confirm_cancel_trip")
        if st.button("❌ Cancel Trip", type="primary", disabled=not confirm, use_container_width=True, key="btn_cancel_trip"):
            try:
                cancel(selected_trip.id)
                st.success(f"Trip **{selected_trip.trip_code}** has been cancelled.")
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {e}")


# ---------------------------------------------------------------------------
# Tab 2 — Live Dispatch Board (Kanban)
# ---------------------------------------------------------------------------

def _render_trip_card(trip: Trip, vehicles: dict, drivers: dict) -> str:
    """Return HTML for a single trip card on the dispatch board."""
    v = vehicles.get(trip.vehicle_id)
    d = drivers.get(trip.driver_id)

    status_color = TRIP_STATUS_COLORS.get(trip.status, "#6b7280")

    vehicle_line = f"🚛 {v.registration_no} — {v.model_name}" if v else "🚛 Unknown Vehicle"
    driver_line  = f"👤 {d.name}" if d else "👤 Unknown Driver"

    return f"""
<div class="dispatch-card">
    <div class="dispatch-card-code">{trip.trip_code}</div>
    <div class="dispatch-card-route">📍 {trip.source} → {trip.destination}</div>
    <div class="dispatch-card-detail">{vehicle_line}</div>
    <div class="dispatch-card-detail">{driver_line}</div>
    <div class="dispatch-card-detail">📦 {trip.cargo_weight_kg:,.0f} kg &nbsp;|&nbsp; 📏 {trip.planned_distance_km:,.0f} km</div>
    <div class="dispatch-card-revenue">₹{trip.revenue:,.0f}</div>
    <div class="dispatch-card-time">{trip.created_at.strftime('%d %b %Y · %H:%M') if trip.created_at else ''}</div>
</div>
"""


def _render_dispatch_board(trips: list, vehicles: dict, drivers: dict) -> None:
    """4-column kanban board showing trips grouped by status."""
    statuses = [
        (TripStatus.DRAFT,      "📝 Draft",      "#3b82f6"),
        (TripStatus.DISPATCHED, "🚀 Dispatched", "#f59e0b"),
        (TripStatus.COMPLETED,  "✅ Completed",  "#10b981"),
        (TripStatus.CANCELLED,  "❌ Cancelled",  "#ef4444"),
    ]

    cols = st.columns(4, gap="small")
    for col, (status, label, color) in zip(cols, statuses):
        status_trips = [t for t in trips if t.status == status]
        with col:
            # Column header
            st.markdown(
                f"""
                <div class="dispatch-col-header" style="border-top: 3px solid {color};">
                    <span style="color:{color}; font-weight:700; font-size:1rem;">{label}</span>
                    <span class="dispatch-col-count" style="background:{color}22; color:{color};">{len(status_trips)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if status_trips:
                cards_html = "".join(_render_trip_card(t, vehicles, drivers) for t in status_trips)
                st.markdown(cards_html, unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="dispatch-empty">No {status.lower()} trips</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Trip Dispatcher page (two tabs)."""
    st.markdown(
        '<div class="page-header"><h1 class="page-title">🗺️ Trip Dispatcher</h1></div>',
        unsafe_allow_html=True,
    )

    user     = get_current_user()
    editable = can_edit(user["role_name"], "Trips") if user else False

    # ---- Load data ----
    trips, vehicles, drivers = _load_all_trips()

    # ---- Tabs ----
    tab1, tab2 = st.tabs(["🗺️ Trip Dispatcher", "📋 Live Dispatch Board"])

    # ================================================================
    # TAB 1 — Trip Dispatcher
    # ================================================================
    with tab1:
        # Search & Filter
        col_search, col_filter, col_refresh = st.columns([3, 1, 1])
        search_term   = col_search.text_input(
            "🔍 Search trips",
            placeholder="Trip code, origin, or destination",
            label_visibility="collapsed",
            key="trip_search",
        )
        status_options = ["All"] + [s.value for s in TripStatus]
        status_filter  = col_filter.selectbox(
            "Filter", status_options, label_visibility="collapsed", key="trip_status_filter"
        )
        with col_refresh:
            if st.button("🔄 Refresh", use_container_width=True, key="btn_refresh_trips"):
                st.rerun()

        # Apply client-side filters to loaded data
        filtered = trips
        if search_term:
            term = search_term.lower()
            filtered = [
                t for t in filtered
                if term in t.trip_code.lower()
                or term in t.source.lower()
                or term in t.destination.lower()
            ]
        if status_filter != "All":
            filtered = [t for t in filtered if t.status == status_filter]

        # Metrics
        _metrics_row(trips)  # metrics always show totals across all trips
        st.divider()

        # Trips table
        st.markdown("#### 📋 All Trips")
        _trips_table(filtered, vehicles, drivers)

        # ---- CRUD actions ----
        if editable:
            st.divider()
            st.markdown("### ⚙️ Trip Actions")
            _form_create_draft()
            _form_dispatch(trips, vehicles, drivers)
            _form_complete(trips, vehicles)
            _form_cancel(trips)
        else:
            st.info("🔒 You have view-only access to the Trip Dispatcher. Contact a Dispatcher to manage trips.")

    # ================================================================
    # TAB 2 — Live Dispatch Board
    # ================================================================
    with tab2:
        hdr_col, refresh_col = st.columns([6, 1])
        with hdr_col:
            st.markdown(
                f"<p style='color:#9ca3af; font-size:0.85rem; margin:0;'>"
                f"Live view • Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}</p>",
                unsafe_allow_html=True,
            )
        with refresh_col:
            if st.button("🔄 Refresh", use_container_width=True, key="btn_refresh_board"):
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        _render_dispatch_board(trips, vehicles, drivers)
