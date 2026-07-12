"""
frontend/components/kpi_card.py

Purpose:
    Reusable KPI tile component for the dashboard.

Reason:
    The dashboard has 7 KPI tiles in a row. This component renders one
    tile with a value, label, and accent color — used via st.columns().
"""

import streamlit as st


def render_kpi_card(value: str | int | float, label: str, color: str = "#f59e0b") -> None:
    """
    Render a single KPI card.

    Args:
        value: The metric number to display.
        label: Description below the number.
        color: Accent color for the value (hex).
    """
    st.markdown(
        f"""
        <div class="kpi-card">
            <p class="kpi-value" style="color: {color};">{value}</p>
            <p class="kpi-label">{label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
