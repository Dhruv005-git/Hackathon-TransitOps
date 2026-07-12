"""
frontend/pages/page_drivers.py

Purpose:
    Driver Management page — full CRUD in Phase 2.
    Phase 1: read-only driver table with license expiry check.

Exposes:
    render() — called by app.py router.
"""

import datetime
import streamlit as st
import pandas as pd

from app.database.engine import get_session
from app.models import Driver


def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">👤 Drivers & Safety Profiles</h1></div>',
        unsafe_allow_html=True,
    )

    today = datetime.date.today()

    with get_session() as session:
        drivers = session.query(Driver).all()

    if drivers:
        df = pd.DataFrame([{
            "Name":           d.name,
            "License No":     d.license_no,
            "Category":       d.license_category,
            "License Expiry": d.license_expiry.strftime("%d %b %Y"),
            "Contact":        d.contact_no,
            "Safety Score":   f"{d.safety_score:.0f}%",
            "Status":         d.status,
            "License":        "Valid" if d.license_expiry >= today else "EXPIRED",
        } for d in drivers])

        def color_status(val: str) -> str:
            colors = {"Available": "#10b981", "On Trip": "#f59e0b",
                      "Off Duty": "#9ca3af", "Suspended": "#ef4444"}
            return f"color: {colors.get(val, '#e6e6e6')}; font-weight: 600;"

        def color_license(val: str) -> str:
            return "color: #10b981; font-weight:600;" if val == "Valid" else "color: #ef4444; font-weight:600;"

        st.dataframe(
            df.style.map(color_status, subset=["Status"]).map(color_license, subset=["License"]),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No drivers found.")

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Full CRUD Coming in Phase 2</h3>
            <p>Add Driver, Edit Driver, License Compliance forms will be implemented in Phase 2.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
