"""Module containing db session dependencies."""

from __future__ import annotations

from ..db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()
