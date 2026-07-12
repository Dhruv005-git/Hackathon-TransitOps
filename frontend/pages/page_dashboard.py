"""
frontend/pages/page_dashboard.py

Purpose:
    Dashboard page — KPI tiles, recent trips table, vehicle status chart.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go

from app.database.engine import get_session
from app.models import Vehicle, Driver, Trip
from frontend.components.kpi_card import render_kpi_card


def _get_dashboard_data() -> dict:
    """Fetch all KPI data and recent trips from DB."""
    with get_session() as session:
        vehicles = session.query(Vehicle).all()
        drivers  = session.query(Driver).all()
        trips    = session.query(Trip).all()

        available_vehicles = sum(1 for v in vehicles if v.status == "Available")
        in_maintenance     = sum(1 for v in vehicles if v.status == "In Shop")
        on_trip_vehicles   = sum(1 for v in vehicles if v.status == "On Trip")
        active_trips       = sum(1 for t in trips if t.status == "Dispatched")
        pending_trips      = sum(1 for t in trips if t.status == "Draft")
        drivers_on_duty    = sum(1 for d in drivers if d.status == "On Trip")

        dispatachable = available_vehicles + on_trip_vehicles
        utilization = round((on_trip_vehicles / dispatachable * 100) if dispatachable > 0 else 0, 1)

        status_counts = {
            "Available": available_vehicles,
            "On Trip":   on_trip_vehicles,
            "In Shop":   in_maintenance,
            "Retired":   sum(1 for v in vehicles if v.status == "Retired"),
        }

        recent = sorted(trips, key=lambda t: t.created_at, reverse=True)[:5]
        recent_data = [
            {
                "Trip Code":    t.trip_code,
                "From":         t.source,
                "To":           t.destination,
                "Distance (km)": t.planned_distance_km,
                "Status":       t.status,
            }
            for t in recent
        ]

        return {
            "total_vehicles":    len(vehicles),
            "available_vehicles": available_vehicles,
            "in_maintenance":    in_maintenance,
            "active_trips":      active_trips,
            "pending_trips":     pending_trips,
            "drivers_on_duty":   drivers_on_duty,
            "utilization":       utilization,
            "status_counts":     status_counts,
            "recent_trips":      recent_data,
        }


def render() -> None:
    """Render the Dashboard page."""
    data = _get_dashboard_data()

    # Header
    st.markdown(
        f"""
        <div class="page-header">
            <h1 class="page-title">📊 Dashboard</h1>
            <span style="color: #9ca3af; font-size: 0.85rem;">
                {datetime.datetime.now().strftime("%A, %d %B %Y · %H:%M")}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filters
    fc1, fc2, fc3, _ = st.columns([2, 2, 2, 4])
    with fc1:
        st.selectbox("Vehicle Type", ["All", "Van", "Truck", "Mini"], key="dash_type")
    with fc2:
        st.selectbox("Status", ["All", "Available", "On Trip", "In Shop", "Retired"], key="dash_status")
    with fc3:
        st.selectbox("Region", ["All", "North", "South", "East", "West"], key="dash_region")

    st.markdown("<br>", unsafe_allow_html=True)

    # 7 KPI tiles
    kpi_cols = st.columns(7)
    kpi_data = [
        (data["total_vehicles"],       "Total Vehicles",     "#3b82f6"),
        (data["available_vehicles"],   "Available",          "#10b981"),
        (data["in_maintenance"],       "In Maintenance",     "#ef4444"),
        (data["active_trips"],         "Active Trips",       "#f59e0b"),
        (data["pending_trips"],        "Pending Trips",      "#8b5cf6"),
        (data["drivers_on_duty"],      "Drivers On Duty",    "#06b6d4"),
        (f"{data['utilization']}%",    "Fleet Utilization",  "#f59e0b"),
    ]
    for col, (value, label, color) in zip(kpi_cols, kpi_data):
        with col:
            render_kpi_card(value, label, color)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent Trips + Vehicle Status Chart
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("#### 🗺️ Recent Trips")
        if data["recent_trips"]:
            df = pd.DataFrame(data["recent_trips"])

            def color_status(val: str) -> str:
                colors = {
                    "Dispatched": "#f59e0b", "Completed": "#10b981",
                    "Cancelled": "#ef4444", "Draft": "#3b82f6",
                }
                return f"color: {colors.get(val, '#9ca3af')}; font-weight: 600;"

            st.dataframe(
                df.style.map(color_status, subset=["Status"]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No trips yet.")

    with right:
        st.markdown("#### 🚛 Vehicle Status")
        labels = list(data["status_counts"].keys())
        values = list(data["status_counts"].values())
        colors = ["#10b981", "#f59e0b", "#ef4444", "#6b7280"]

        fig = go.Figure(go.Bar(
            x=values, y=labels, orientation="h",
            marker_color=colors,
            text=values, textposition="auto",
            textfont=dict(color="#e6e6e6", size=13),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af"),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False),
            margin=dict(l=10, r=10, t=10, b=10),
            height=220, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
