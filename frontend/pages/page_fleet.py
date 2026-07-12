"""
frontend/pages/page_fleet.py

Purpose:
    Vehicle Registry page — full CRUD in Phase 2.
    Phase 1: read-only table preview of seeded vehicles.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st
import pandas as pd

from app.database.engine import get_session
from app.models import Vehicle


def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">🚛 Vehicle Registry</h1></div>',
        unsafe_allow_html=True,
    )

    with get_session() as session:
        vehicles = session.query(Vehicle).all()

    if vehicles:
        df = pd.DataFrame([{
            "Registration No":    v.registration_no,
            "Model":              v.model_name,
            "Type":               v.type,
            "Max Capacity (kg)":  v.max_capacity_kg,
            "Odometer (km)":      v.odometer,
            "Acquisition Cost":   f"Rs. {v.acquisition_cost:,.0f}",
            "Status":             v.status,
        } for v in vehicles])

        def color_status(val: str) -> str:
            colors = {"Available": "#10b981", "On Trip": "#f59e0b",
                      "In Shop": "#ef4444", "Retired": "#9ca3af"}
            return f"color: {colors.get(val, '#e6e6e6')}; font-weight: 600;"

        st.dataframe(df.style.map(color_status, subset=["Status"]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No vehicles found.")

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Full CRUD Coming in Phase 2</h3>
            <p>Add Vehicle, Edit Vehicle, Search and Filter forms will be implemented in Phase 2.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
