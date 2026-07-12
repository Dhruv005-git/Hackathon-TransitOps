"""
frontend/pages/page_dashboard.py — Phase 1 (fixed)

Changes from original:
  - Removed non-functional filter row (Type / Status / Region)
  - Recent trips now includes Vehicle + Driver columns
  - Added total revenue and completed trip count to KPIs
  - Donut chart replaces flat bar chart for vehicle status
"""

import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go

from app.database.engine import get_session
from app.models import Vehicle, Driver, Trip
from frontend.components.kpi_card import render_kpi_card


def _get_dashboard_data() -> dict:
    with get_session() as session:
        vehicles = session.query(Vehicle).all()
        drivers  = session.query(Driver).all()
        trips    = session.query(Trip).all()

        v_map = {v.id: v.registration_no for v in vehicles}
        d_map = {d.id: d.name            for d in drivers}

        available_v    = sum(1 for v in vehicles if v.status == "Available")
        in_maint       = sum(1 for v in vehicles if v.status == "In Shop")
        on_trip_v      = sum(1 for v in vehicles if v.status == "On Trip")
        active_trips   = sum(1 for t in trips if t.status == "Dispatched")
        pending_trips  = sum(1 for t in trips if t.status == "Draft")
        drivers_on_duty= sum(1 for d in drivers if d.status == "On Trip")
        completed_trips= sum(1 for t in trips if t.status == "Completed")
        total_revenue  = sum(t.revenue for t in trips if t.status == "Completed")

        dispatachable  = available_v + on_trip_v
        utilization    = round((on_trip_v / dispatachable * 100) if dispatachable > 0 else 0, 1)

        status_counts = {
            "Available": available_v,
            "On Trip":   on_trip_v,
            "In Shop":   in_maint,
            "Retired":   sum(1 for v in vehicles if v.status == "Retired"),
        }

        recent = sorted(trips, key=lambda t: t.created_at, reverse=True)[:8]
        recent_data = [
            {
                "Trip Code":  t.trip_code,
                "Route":      f"{t.source} → {t.destination}",
                "Vehicle":    v_map.get(t.vehicle_id, "-"),
                "Driver":     d_map.get(t.driver_id, "-"),
                "Revenue":    f"Rs.{t.revenue:,.0f}",
                "Status":     t.status,
            }
            for t in recent
        ]

        return {
            "total_vehicles":     len(vehicles),
            "available_vehicles": available_v,
            "in_maintenance":     in_maint,
            "active_trips":       active_trips,
            "pending_trips":      pending_trips,
            "drivers_on_duty":    drivers_on_duty,
            "utilization":        utilization,
            "completed_trips":    completed_trips,
            "total_revenue":      total_revenue,
            "status_counts":      status_counts,
            "recent_trips":       recent_data,
        }


def render() -> None:
    data = _get_dashboard_data()

    # ── Header ─────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="page-header">
            <h1 class="page-title">📊 Operations Dashboard</h1>
            <span style="color:#9ca3af;font-size:0.85rem;">
                {datetime.datetime.now().strftime("%A, %d %B %Y  ·  %H:%M")}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 8 KPI tiles ────────────────────────────────────────────
    kpi_cols = st.columns(8)
    kpi_data = [
        (data["total_vehicles"],             "Total Vehicles",    "#3b82f6"),
        (data["available_vehicles"],         "Available",         "#10b981"),
        (data["in_maintenance"],             "In Maintenance",    "#ef4444"),
        (data["active_trips"],               "Active Trips",      "#f59e0b"),
        (data["pending_trips"],              "Pending Trips",     "#8b5cf6"),
        (data["drivers_on_duty"],            "Drivers On Duty",   "#06b6d4"),
        (f"{data['utilization']}%",          "Fleet Utilization", "#f59e0b"),
        (f"Rs.{data['total_revenue']:,.0f}", "Total Revenue",     "#10b981"),
    ]
    for col, (value, label, color) in zip(kpi_cols, kpi_data):
        with col:
            render_kpi_card(value, label, color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent Trips + Vehicle Status ──────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("#### 🗺️ Recent Trips")
        if data["recent_trips"]:
            df = pd.DataFrame(data["recent_trips"])

            def color_status(val: str) -> str:
                c = {"Dispatched": "#f59e0b", "Completed": "#10b981",
                     "Cancelled":  "#ef4444", "Draft":     "#9ca3af"}
                return f"color:{c.get(val,'#9ca3af')};font-weight:600;"

            st.dataframe(
                df.style.map(color_status, subset=["Status"]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No trips yet. Create your first trip in the Trips page.")

    with right:
        st.markdown("#### 🚛 Fleet Status")
        labels = list(data["status_counts"].keys())
        values = list(data["status_counts"].values())
        colors = ["#10b981", "#f59e0b", "#ef4444", "#6b7280"]

        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#1a1d23", width=3)),
            textinfo="label+value",
            textfont=dict(color="#e6e6e6", size=12),
            insidetextorientation="radial",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=240, showlegend=False,
            annotations=[dict(
                text=f"<b>{data['total_vehicles']}</b><br>vehicles",
                x=0.5, y=0.5, font=dict(size=16, color="#e6e6e6"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # mini stat row below donut
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f'<div style="text-align:center;color:#10b981;font-size:1.1rem;'
                        f'font-weight:700;">{data["available_vehicles"]}</div>'
                        f'<div style="text-align:center;color:#9ca3af;font-size:0.7rem;">Available</div>',
                        unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div style="text-align:center;color:#f59e0b;font-size:1.1rem;'
                        f'font-weight:700;">{data["active_trips"]}</div>'
                        f'<div style="text-align:center;color:#9ca3af;font-size:0.7rem;">On Trip</div>',
                        unsafe_allow_html=True)
        with mc3:
            st.markdown(f'<div style="text-align:center;color:#ef4444;font-size:1.1rem;'
                        f'font-weight:700;">{data["in_maintenance"]}</div>'
                        f'<div style="text-align:center;color:#9ca3af;font-size:0.7rem;">In Shop</div>',
                        unsafe_allow_html=True)
