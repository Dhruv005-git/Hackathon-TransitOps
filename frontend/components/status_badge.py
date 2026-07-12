"""
frontend/components/status_badge.py

Purpose:
    Reusable status badge component with color coding.

Reason:
    Status badges appear on every data table (vehicles, drivers, trips).
    Centralizing the color logic here ensures consistent styling everywhere.
"""

import streamlit as st


# Status -> CSS class mapping
STATUS_CLASSES = {
    "Available": "status-available",
    "On Trip": "status-on-trip",
    "In Shop": "status-in-shop",
    "Retired": "status-retired",
    "Suspended": "status-suspended",
    "Off Duty": "status-off-duty",
    "Draft": "status-draft",
    "Dispatched": "status-dispatched",
    "Completed": "status-completed",
    "Cancelled": "status-cancelled",
    "Active": "status-on-trip",
}


def render_status_badge(status: str) -> str:
    """
    Return HTML for a colored status badge.

    Args:
        status: The status string (e.g. "Available", "On Trip").

    Returns:
        HTML string for the badge.
    """
    css_class = STATUS_CLASSES.get(status, "status-available")
    return f'<span class="status-badge {css_class}">{status}</span>'


def display_status_badge(status: str) -> None:
    """Render a status badge directly using st.markdown."""
    st.markdown(render_status_badge(status), unsafe_allow_html=True)
