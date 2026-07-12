"""
frontend/pages/page_fuel_expenses.py — Phase 4 + RBAC enforcement

Permissions enforced:
  Fleet Manager    → log fuel + log expense + view all
  Financial Analyst → log fuel + log expense + view all
  Dispatcher       → view only (no log forms)
  Safety Officer   → view only (no log forms)
"""
from __future__ import annotations
import datetime
import streamlit as st
import pandas as pd
from pydantic import ValidationError

from app.schemas.fuel_schema import FuelCreate, ExpenseCreate, EXPENSE_CATEGORIES
from app.services.fuel_service import (
    add_fuel_log, add_expense, get_fuel_logs, get_expenses,
    get_cost_summary, get_all_vehicles_list, get_trips_for_vehicle,
)
from frontend.components.auth_guard import can


def _kpis(s: dict):
    cols = st.columns(4)
    items = [
        (f"Rs.{s['fuel_cost']:,.0f}",    "Total Fuel Cost",    "#f59e0b"),
        (f"Rs.{s['expense_cost']:,.0f}", "Other Expenses",      "#ef4444"),
        (f"Rs.{s['total_cost']:,.0f}",   "Total Op. Cost",      "#3b82f6"),
        (f"{s['fuel_liters']:,.0f} L",   "Fuel Consumed",       "#10b981"),
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


def _fuel_form(vehicles: list[dict]):
    st.markdown("#### ⛽ Log Fuel Entry")
    with st.form("fuel_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            v_opts  = {v["label"]: v["id"] for v in vehicles}
            v_label = st.selectbox("Vehicle *", list(v_opts.keys()))
            liters  = st.number_input("Liters *", min_value=0.1, value=40.0, step=5.0)
            cost    = st.number_input("Total Cost (Rs.) *", min_value=1.0,
                                      value=3600.0, step=100.0, format="%.0f")
        with c2:
            date   = st.date_input("Date *", value=datetime.date.today())
            trips  = get_trips_for_vehicle(v_opts.get(v_label, 0))
            t_opts = {"(No trip)": None} | {t["label"]: t["id"] for t in trips}
            t_lbl  = st.selectbox("Link to Trip (optional)", list(t_opts.keys()))
        st.caption(f"Rate: Rs.{round(cost / liters, 2) if liters > 0 else 0}/L")
        submitted = st.form_submit_button("⛽ Log Fuel", type="primary",
                                          use_container_width=True)
    if submitted:
        try:
            rec = add_fuel_log(FuelCreate(
                vehicle_id=v_opts[v_label], trip_id=t_opts[t_lbl],
                liters=liters, cost=cost, date=date,
            ))
            st.success(f"✅ Fuel: {rec['liters']:.1f}L @ Rs.{rec['cost_per_l']}/L "
                       f"for {rec['vehicle_reg']}")
            st.rerun()
        except (ValidationError, ValueError) as e:
            st.error(str(e))


def _expense_form(vehicles: list[dict]):
    st.markdown("#### 💸 Log Expense")
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            v_opts  = {v["label"]: v["id"] for v in vehicles}
            v_label = st.selectbox("Vehicle *", list(v_opts.keys()))
            cat     = st.selectbox("Category *", EXPENSE_CATEGORIES)
        with c2:
            amount = st.number_input("Amount (Rs.) *", min_value=1.0,
                                     value=500.0, step=50.0, format="%.0f")
            date   = st.date_input("Date *", value=datetime.date.today())
        submitted = st.form_submit_button("💸 Log Expense", type="primary",
                                          use_container_width=True)
    if submitted:
        try:
            rec = add_expense(ExpenseCreate(
                vehicle_id=v_opts[v_label], category=cat,
                amount=amount, date=date,
            ))
            st.success(f"✅ Expense: Rs.{rec['amount']:,.0f} ({rec['category']}) "
                       f"for {rec['vehicle_reg']}")
            st.rerun()
        except (ValidationError, ValueError) as e:
            st.error(str(e))


def render():
    st.markdown('<div class="page-header">'
                '<h1 class="page-title">⛽ Fuel & Expense Management</h1></div>',
                unsafe_allow_html=True)

    _kpis(get_cost_summary())
    st.markdown("<br>", unsafe_allow_html=True)

    can_fuel = can("fuel.add")
    can_exp  = can("expenses.add")

    vehicles = get_all_vehicles_list()
    if not vehicles:
        st.warning("No vehicles found. Add vehicles first.")
        return

    # Build tab list dynamically
    tabs = []
    if can_fuel:
        tabs.append("⛽ Log Fuel")
    if can_exp:
        tabs.append("💸 Log Expense")
    tabs += ["📋 Fuel Records", "📋 Expense Records"]

    rendered = st.tabs(tabs)
    idx = 0

    if can_fuel:
        with rendered[idx]:
            _fuel_form(vehicles)
        idx += 1

    if can_exp:
        with rendered[idx]:
            _expense_form(vehicles)
        idx += 1

    # Fuel records — always visible
    with rendered[idx]:
        if not can_fuel:
            st.info("🔒 You have **view-only** access. Log Fuel requires Fleet Manager "
                    "or Financial Analyst role.")
        logs = get_fuel_logs()
        if logs:
            df = pd.DataFrame([{
                "Vehicle":      f["vehicle_reg"],
                "Date":         f["date"].strftime("%d %b %Y"),
                "Liters":       f"{f['liters']:.1f} L",
                "Total Cost":   f"Rs.{f['cost']:,.0f}",
                "Rate (Rs./L)": f"{f['cost_per_l']:.2f}",
            } for f in logs])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No fuel records yet.")
    idx += 1

    # Expense records — always visible
    with rendered[idx]:
        if not can_exp:
            st.info("🔒 You have **view-only** access. Log Expense requires Fleet Manager "
                    "or Financial Analyst role.")
        exps = get_expenses()
        if exps:
            df = pd.DataFrame([{
                "Vehicle":  e["vehicle_reg"],
                "Date":     e["date"].strftime("%d %b %Y"),
                "Category": e["category"],
                "Amount":   f"Rs.{e['amount']:,.0f}",
            } for e in exps])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No expense records yet.")
