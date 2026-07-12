"""
frontend/pages/page_maintenance.py — Phase 4 + RBAC enforcement

Permissions enforced:
  Fleet Manager  → log maintenance + close maintenance
  Everyone else  → view only (records table)
"""
from __future__ import annotations
import datetime
import streamlit as st
import pandas as pd
from pydantic import ValidationError

from app.schemas.maintenance_schema import MaintenanceCreate, MaintenanceClose, SERVICE_TYPES
from app.services.maintenance_service import (
    get_all_logs, log_maintenance, close_maintenance,
    get_maintenance_summary, get_all_vehicles_for_select,
)
from frontend.components.auth_guard import can


def _kpis(s: dict):
    cols = st.columns(4)
    items = [
        (s["total"],      "Total Records",  "#3b82f6"),
        (s["active"],     "In Shop Now",    "#ef4444"),
        (s["completed"],  "Completed",      "#10b981"),
        (f"Rs.{s['total_cost']:,.0f}", "Total Spend", "#f59e0b"),
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


def _log_form():
    st.markdown("#### 🔧 Log New Maintenance")
    vehicles = get_all_vehicles_for_select()
    if not vehicles:
        st.warning("No available vehicles to maintain.")
        return
    with st.form("log_maint_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            v_opts   = {v["label"]: v["id"] for v in vehicles}
            v_label  = st.selectbox("Vehicle *", list(v_opts.keys()))
            svc_type = st.selectbox("Service Type *", SERVICE_TYPES)
        with c2:
            cost = st.number_input("Estimated Cost (Rs.) *", min_value=0.0,
                                   value=2000.0, step=500.0, format="%.0f")
            date = st.date_input("Date *", value=datetime.date.today())
        submitted = st.form_submit_button("🔧 Log & Send to Shop", type="primary",
                                          use_container_width=True)
    if submitted:
        try:
            record = log_maintenance(MaintenanceCreate(
                vehicle_id=v_opts[v_label], service_type=svc_type,
                cost=cost, date=date,
            ))
            st.success(f"✅ Maintenance logged for **{record['vehicle_reg']}**. "
                       "Vehicle → In Shop.")
            st.rerun()
        except (ValidationError, ValueError) as e:
            st.error(str(e))


def _logs_table(logs: list[dict]):
    if not logs:
        st.info("No maintenance records found.")
        return
    df = pd.DataFrame([{
        "Vehicle":      m["vehicle_reg"],
        "Service Type": m["service_type"],
        "Cost (Rs.)":   f"Rs.{m['cost']:,.0f}",
        "Date":         m["date"].strftime("%d %b %Y"),
        "Status":       m["status"],
    } for m in logs])

    def cs(v):
        return ("color:#ef4444;font-weight:700;" if v == "Active"
                else "color:#10b981;font-weight:700;")

    st.dataframe(df.style.map(cs, subset=["Status"]),
                 use_container_width=True, hide_index=True)


def _close_panel(active_logs: list[dict]):
    if not active_logs:
        st.info("No active maintenance records to close.")
        return
    st.markdown("---")
    st.markdown("#### ✅ Close Maintenance Record")
    options    = {f"#{m['id']} — {m['vehicle_reg']} — {m['service_type']}": m
                  for m in active_logs}
    chosen_lbl = st.selectbox("Select Active Record:", list(options.keys()),
                               key="maint_close_select")
    chosen = options[chosen_lbl]
    with st.form("close_maint_form"):
        actual = st.number_input("Actual Cost (Rs.) — leave at estimated to keep",
                                  min_value=0.0, value=float(chosen["cost"]),
                                  step=500.0, format="%.0f")
        c1, c2 = st.columns(2)
        with c1: confirm = st.form_submit_button("✅ Close & Release Vehicle",
                                                   type="primary", use_container_width=True)
        with c2: cancel  = st.form_submit_button("✖ Cancel", use_container_width=True)
    if confirm:
        try:
            close_maintenance(chosen["id"],
                              MaintenanceClose(actual_cost=actual if actual > 0 else None))
            st.success(f"✅ Closed. **{chosen['vehicle_reg']}** → Available.")
            st.rerun()
        except ValueError as e:
            st.error(str(e))
    if cancel:
        st.rerun()


def render():
    st.markdown('<div class="page-header"><h1 class="page-title">🔧 Maintenance</h1></div>',
                unsafe_allow_html=True)

    _kpis(get_maintenance_summary())
    st.markdown("<br>", unsafe_allow_html=True)

    # Build tabs based on permissions
    tabs = ["📋 All Records"]
    if can("maintenance.log"):
        tabs.append("➕ Log Maintenance")

    rendered_tabs = st.tabs(tabs)
    tab_list = rendered_tabs[0]
    tab_log  = rendered_tabs[1] if len(rendered_tabs) > 1 else None

    if tab_log:
        with tab_log:
            _log_form()

    with tab_list:
        if not can("maintenance.log"):
            st.info("🔒 You have **view-only** access to Maintenance records.")

        status_f = st.selectbox("Filter", ["All", "Active", "Completed"],
                                key="maint_status_filter")
        logs = get_all_logs(status_filter=status_f)
        st.caption(f"{len(logs)} record(s)")
        _logs_table(logs)

        # Close panel — only Fleet Manager
        if can("maintenance.close"):
            active_logs = get_all_logs(status_filter="Active")
            if active_logs:
                _close_panel(active_logs)
