"""
frontend/pages/page_maintenance.py

Purpose:
    Maintenance tracking page — Phase 4.
    Phase 1: preview of In Shop count.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st

from app.database.engine import get_session
from app.models import Vehicle, MaintenanceLog


def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">🔧 Maintenance</h1></div>',
        unsafe_allow_html=True,
    )

    with get_session() as session:
        in_shop    = session.query(Vehicle).filter(Vehicle.status == "In Shop").count()
        total_logs = session.query(MaintenanceLog).count()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Vehicles Currently In Shop", in_shop)
    with col2:
        st.metric("Total Maintenance Records", total_logs)

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Maintenance Workflow Coming in Phase 4</h3>
            <p>Log Maintenance (auto In Shop), Close Maintenance (auto Available), Service Log, Cost Tracking — Phase 4.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
