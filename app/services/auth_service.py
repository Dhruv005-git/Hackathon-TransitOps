"""
app/services/auth_service.py

Purpose:
    Authentication business logic — login, session management, logout.

Reason:
    Keeps auth logic separate from the UI layer. The login page calls
    these functions; it never touches the DB or hashing directly.
"""

from typing import Optional

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
