"""
app/models/base.py

Purpose:
    Declarative base for all SQLAlchemy models.

Reason:
    All models inherit from this single Base so init_db() can
    create every table with one call to Base.metadata.create_all().
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
