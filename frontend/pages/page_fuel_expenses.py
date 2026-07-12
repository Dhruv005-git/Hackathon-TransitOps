"""
frontend/pages/page_fuel_expenses.py

Purpose:
    Fuel & Expense Management page — Phase 4.
    Phase 1: preview cost totals.

Exposes:
    render() — called by app.py router.
"""

import streamlit as st

from app.database.engine import get_session
from app.models import FuelLog, Expense


def render() -> None:
    st.markdown(
        '<div class="page-header"><h1 class="page-title">⛽ Fuel & Expense Management</h1></div>',
        unsafe_allow_html=True,
    )

    with get_session() as session:
        fuel_total    = sum(f.cost for f in session.query(FuelLog).all())
        expense_total = sum(e.amount for e in session.query(Expense).all())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Fuel Cost", f"Rs. {fuel_total:,.0f}")
    with col2:
        st.metric("Other Expenses", f"Rs. {expense_total:,.0f}")
    with col3:
        st.metric("Total Operational Cost", f"Rs. {fuel_total + expense_total:,.0f}")

    st.markdown(
        """
        <div class="coming-soon">
            <h3>Fuel & Expense Logging Coming in Phase 4</h3>
            <p>Log Fuel, Log Expenses, Per-Vehicle Cost Rollup — Phase 4.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
