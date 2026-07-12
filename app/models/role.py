"""
app/models/role.py

Purpose:
    ORM model for the Roles table.

Reason:
    Stores the 4 system roles (Fleet Manager, Dispatcher, Safety Officer,
    Financial Analyst) and their permission maps. Referenced by Users via FK.
"""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    permissions_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    # Relationship
    users = relationship("User", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"
