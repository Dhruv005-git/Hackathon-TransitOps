"""
frontend/pages/page_analytics.py

Purpose:
    Reports & Analytics page — full charts in Phase 5.
    Phase 1: top-level KPI preview.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st

from app.database.engine import get_session
from app.models import Trip, Vehicle, FuelLog


def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">📈 Reports & Analytics</h1></div>',
        unsafe_allow_html=True,
    )

    with get_session() as session:
        completed   = session.query(Trip).filter(Trip.status == "Completed").all()
        revenue     = sum(t.revenue for t in completed)
        distance    = sum(t.planned_distance_km for t in completed)
        total_fuel  = sum(f.liters for f in session.query(FuelLog).all())
        efficiency  = round(distance / total_fuel, 2) if total_fuel > 0 else 0
        total_v     = session.query(Vehicle).count()
        on_trip_v   = session.query(Vehicle).filter(Vehicle.status == "On Trip").count()
        utilization = round((on_trip_v / total_v * 100) if total_v > 0 else 0, 1)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Fuel Efficiency (km/L)", efficiency)
    with col2:
        st.metric("Fleet Utilization", f"{utilization}%")
    with col3:
        st.metric("Total Revenue", f"Rs. {revenue:,.0f}")
    with col4:
        st.metric("Completed Trips", len(completed))

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Full Analytics Coming in Phase 5</h3>
            <p>Fuel Efficiency Charts, ROI per Vehicle, Monthly Revenue, Cost Breakdown, CSV Export — Phase 5.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
