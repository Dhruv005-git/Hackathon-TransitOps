"""
frontend/pages/page_trips.py

Purpose:
    Trip Dispatcher page — full lifecycle in Phase 3.
    Phase 1: read-only trips table.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st
import pandas as pd

from app.database.engine import get_session
from app.models import Trip, Vehicle, Driver


def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">🗺️ Trip Dispatcher</h1></div>',
        unsafe_allow_html=True,
    )

    with get_session() as session:
        trips    = session.query(Trip).order_by(Trip.created_at.desc()).all()
        vehicles = {v.id: v.registration_no for v in session.query(Vehicle).all()}
        drivers  = {d.id: d.name for d in session.query(Driver).all()}

    if trips:
        df = pd.DataFrame([{
            "Trip Code":     t.trip_code,
            "From -> To":    f"{t.source} -> {t.destination}",
            "Vehicle":       vehicles.get(t.vehicle_id, "-"),
            "Driver":        drivers.get(t.driver_id, "-"),
            "Cargo (kg)":    t.cargo_weight_kg,
            "Distance (km)": t.planned_distance_km,
            "Revenue":       f"Rs. {t.revenue:,.0f}",
            "Status":        t.status,
        } for t in trips])

        def color_status(val: str) -> str:
            colors = {"Draft": "#3b82f6", "Dispatched": "#f59e0b",
                      "Completed": "#10b981", "Cancelled": "#ef4444"}
            return f"color: {colors.get(val, '#e6e6e6')}; font-weight: 600;"

        st.dataframe(df.style.map(color_status, subset=["Status"]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No trips found.")

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Trip Dispatch Engine Coming in Phase 3</h3>
            <p>Create Trip, Dispatch with Validation, Complete, Cancel, Live Board — Phase 3.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
