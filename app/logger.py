"""
app/logger.py

Purpose:
    Centralized logging setup for the TransitOps application.

Reason:
    Replaces bare print() calls in the database layer with proper Python logging.
    Log level is controlled by DEBUG setting in config.py / .env.
    All module loggers use the same formatter for consistent output.

Usage:
    from app.logger import get_logger
    log = get_logger(__name__)
    log.info("Tables recreated")
    log.warning("Seed data already exists, skipping")
    log.error("Database connection failed")
"""

import logging
import sys

from app.config import DEBUG


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a named logger with consistent formatting.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    level = logging.DEBUG if DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    return logger
