"""
frontend/pages/page_analytics.py — Phase 5 + RBAC enforcement

Permissions enforced:
  Fleet Manager    → view all charts + export CSV
  Financial Analyst → view all charts + export CSV
  Dispatcher       → view charts only (no export)
  Safety Officer   → view charts only (no export)
"""
from __future__ import annotations
import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.database.engine import get_session
from app.models import Trip, Vehicle, Driver, FuelLog, Expense, MaintenanceLog
from app.constants import TripStatus
from frontend.components.auth_guard import can

_DARK  = "rgba(0,0,0,0)"
_FONT  = dict(color="#9ca3af", family="Inter, sans-serif")
_LAY   = dict(paper_bgcolor=_DARK, plot_bgcolor=_DARK, font=_FONT,
              margin=dict(l=10, r=10, t=36, b=10))


def _load():
    with get_session() as s:
        trips    = s.query(Trip).all()
        vehicles = s.query(Vehicle).all()
        fuel     = s.query(FuelLog).all()
        expenses = s.query(Expense).all()
        maint    = s.query(MaintenanceLog).all()

    completed  = [t for t in trips if t.status == TripStatus.COMPLETED]
    v_id2reg   = {v.id: v.registration_no for v in vehicles}
    total_v    = len(vehicles)
    on_trip_v  = sum(1 for v in vehicles if v.status == "On Trip")
    utilization= round(on_trip_v / total_v * 100, 1) if total_v else 0

    fuel_l     = sum(f.liters for f in fuel)
    total_dist = sum(t.planned_distance_km for t in completed)
    efficiency = round(total_dist / fuel_l, 2) if fuel_l else 0

    fuel_cost  = sum(f.cost for f in fuel)
    exp_cost   = sum(e.amount for e in expenses)
    maint_cost = sum(m.cost for m in maint)
    revenue    = sum(t.revenue for t in completed)

    # Revenue per vehicle
    rev_v: dict[str, float] = {}
    for t in completed:
        k = v_id2reg.get(t.vehicle_id, str(t.vehicle_id))
        rev_v[k] = rev_v.get(k, 0) + t.revenue

    # Monthly completed trips
    monthly: dict[str, int] = {}
    for t in completed:
        m = t.created_at.strftime("%b %Y")
        monthly[m] = monthly.get(m, 0) + 1

    # Efficiency per vehicle (from trip.fuel_consumed_l)
    dist_v: dict[int, float] = {}
    fuel_v: dict[int, float] = {}
    for t in completed:
        if t.fuel_consumed_l and t.fuel_consumed_l > 0:
            fuel_v[t.vehicle_id] = fuel_v.get(t.vehicle_id, 0) + t.fuel_consumed_l
            dist_v[t.vehicle_id] = dist_v.get(t.vehicle_id, 0) + t.planned_distance_km
    eff_v = {v_id2reg.get(k, str(k)): round(dist_v[k] / fuel_v[k], 2)
             for k in dist_v if fuel_v.get(k, 0) > 0}

    # Expense by category
    cat_totals: dict[str, float] = {}
    for e in expenses:
        cat_totals[e.category] = cat_totals.get(e.category, 0) + e.amount

    # Trips per vehicle
    trips_v: dict[str, int] = {}
    for t in trips:
        k = v_id2reg.get(t.vehicle_id, str(t.vehicle_id))
        trips_v[k] = trips_v.get(k, 0) + 1

    return dict(
        trips=trips, completed=completed, vehicles=vehicles,
        total_revenue=revenue, efficiency=efficiency, utilization=utilization,
        fuel_cost=fuel_cost, exp_cost=exp_cost, maint_cost=maint_cost,
        rev_v=rev_v, monthly=monthly, eff_v=eff_v,
        cat_totals=cat_totals, trips_v=trips_v,
        all_fuel=fuel, all_expenses=expenses, all_maint=maint,
    )


def _kpis(d: dict):
    cols = st.columns(5)
    items = [
        (f"Rs.{d['total_revenue']:,.0f}",                          "Total Revenue",     "#10b981"),
        (f"{d['efficiency']:.1f} km/L",                            "Fleet Efficiency",  "#f59e0b"),
        (f"{d['utilization']:.1f}%",                               "Utilization",       "#3b82f6"),
        (f"Rs.{d['fuel_cost']+d['exp_cost']+d['maint_cost']:,.0f}","Total Op. Cost",    "#ef4444"),
        (len(d["completed"]),                                       "Completed Trips",   "#8b5cf6"),
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


def _bar(title, x, y, color, text=None):
    fig = go.Figure(go.Bar(
        x=x, y=y, marker_color=color,
        text=text or y, textposition="outside",
        textfont=dict(color="#e6e6e6"),
    ))
    fig.update_layout(**_LAY, height=300, title=title,
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _pie(title, labels, values, colors):
    if sum(values) == 0:
        st.info("No cost data yet.")
        return
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors, line=dict(color="#21252e", width=2)),
        textinfo="label+percent", textfont=dict(color="#e6e6e6"),
    ))
    fig.update_layout(**_LAY, height=300, title=title,
                      showlegend=True, legend=dict(font=dict(color="#9ca3af")))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _csv_section(d: dict):
    st.markdown("---")
    st.markdown("#### 📥 Export Data")
    col1, col2, col3 = st.columns(3)

    with col1:
        df = pd.DataFrame([{
            "Trip Code": t.trip_code, "Source": t.source,
            "Destination": t.destination, "Cargo (kg)": t.cargo_weight_kg,
            "Distance (km)": t.planned_distance_km,
            "Revenue (Rs.)": t.revenue, "Status": t.status,
            "Date": t.created_at.strftime("%Y-%m-%d"),
        } for t in d["trips"]])
        buf = io.StringIO(); df.to_csv(buf, index=False)
        st.download_button("⬇️ Trips CSV", buf.getvalue(),
                           "trips.csv", "text/csv", use_container_width=True)

    with col2:
        df = pd.DataFrame([{
            "Vehicle": f.vehicle_id, "Date": f.date.strftime("%Y-%m-%d"),
            "Liters": f.liters, "Cost (Rs.)": f.cost,
        } for f in d["all_fuel"]])
        buf = io.StringIO(); df.to_csv(buf, index=False)
        st.download_button("⬇️ Fuel CSV", buf.getvalue(),
                           "fuel_logs.csv", "text/csv", use_container_width=True)

    with col3:
        df = pd.DataFrame([{
            "Vehicle": e.vehicle_id, "Category": e.category,
            "Amount (Rs.)": e.amount, "Date": e.date.strftime("%Y-%m-%d"),
        } for e in d["all_expenses"]])
        buf = io.StringIO(); df.to_csv(buf, index=False)
        st.download_button("⬇️ Expenses CSV", buf.getvalue(),
                           "expenses.csv", "text/csv", use_container_width=True)


def render():
    st.markdown('<div class="page-header"><h1 class="page-title">📈 Reports & Analytics</h1></div>',
                unsafe_allow_html=True)

    d = _load()
    _kpis(d)
    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2, gap="large")
    with c1:
        if d["rev_v"]:
            _bar("Revenue by Vehicle (Rs.)",
                 list(d["rev_v"].keys()), list(d["rev_v"].values()), "#10b981",
                 [f"Rs.{v:,.0f}" for v in d["rev_v"].values()])
        else:
            st.info("No revenue data yet (complete some trips).")
    with c2:
        if d["monthly"]:
            _bar("Completed Trips by Month",
                 list(d["monthly"].keys()), list(d["monthly"].values()), "#3b82f6")
        else:
            st.info("No completed trips yet.")

    # Row 2
    c3, c4 = st.columns(2, gap="large")
    with c3:
        if d["eff_v"]:
            regs  = list(d["eff_v"].keys())
            effs  = list(d["eff_v"].values())
            cols  = ["#10b981" if e >= 10 else "#f59e0b" if e >= 7 else "#ef4444" for e in effs]
            fig   = go.Figure(go.Bar(
                x=regs, y=effs, marker_color=cols,
                text=[f"{e:.1f}" for e in effs], textposition="outside",
                textfont=dict(color="#e6e6e6"),
            ))
            fig.update_layout(**_LAY, height=300, title="Fuel Efficiency (km/L) per Vehicle",
                              xaxis=dict(showgrid=False),
                              yaxis=dict(showgrid=False, showticklabels=False))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Fuel efficiency available once trips are completed with fuel data.")
    with c4:
        _pie("Cost Breakdown",
             ["Fuel", "Expenses", "Maintenance"],
             [d["fuel_cost"], d["exp_cost"], d["maint_cost"]],
             ["#f59e0b", "#ef4444", "#3b82f6"])

    # Row 3
    if d["trips_v"]:
        _bar("Total Trips per Vehicle",
             list(d["trips_v"].keys()), list(d["trips_v"].values()), "#8b5cf6")

    # CSV export — Fleet Manager + Financial Analyst only
    if can("analytics.export"):
        _csv_section(d)
    else:
        st.markdown("---")
        st.info("🔒 CSV export is available to **Fleet Manager** and **Financial Analyst** only.")
