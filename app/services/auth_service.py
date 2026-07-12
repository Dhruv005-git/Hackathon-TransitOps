"""
app/services/auth_service.py

Purpose:
    Authentication business logic — login, session management, logout.

Reason:
    Keeps auth logic separate from the UI layer. The login page calls
    these functions; it never touches the DB or hashing directly.
"""

from typing import Optional

import streamlit as st
from sqlalchemy.orm import joinedload

from app.auth.hashing import verify_password
from app.database.engine import get_session
from app.models.user import User


def login(email: str, password: str) -> Optional[dict]:
    """
    Validate credentials and return user info dict on success.

    Returns:
        dict with id, name, email, role_name, role_id — or None if invalid.
    """
    with get_session() as session:
        user = (
            session.query(User)
            .options(joinedload(User.role))
            .filter(User.email == email, User.is_active == True)
            .first()
        )

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role_name": user.role.name,
            "role_id": user.role_id,
        }


def set_current_user(user_data: dict) -> None:
    """Store authenticated user in Streamlit session state."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = user_data


def get_current_user() -> Optional[dict]:
    """Retrieve the currently logged-in user from session state."""
    if st.session_state.get("authenticated"):
        return st.session_state.get("user")
    return None


def logout() -> None:
    """Clear session state to log out the user."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None


def is_authenticated() -> bool:
    """Check if a user is currently logged in."""
    return st.session_state.get("authenticated", False)
