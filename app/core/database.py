"""
MedVision AI – Database Layer
SQLAlchemy engine + session factory + base model.
All DB access goes through get_db() context manager.
"""
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
import streamlit as st

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# ── Engine ────────────────────────────────────────────────────────────────────
def _create_engine():
    return create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )


@st.cache_resource(show_spinner=False)
def get_engine():
    """Cached engine – created once per Streamlit server process."""
    return _create_engine()


SessionLocal = sessionmaker(autocommit=False, autoflush=False)


@contextmanager
def get_db():
    """Context manager – always yields a bound session and closes it after."""
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_connection() -> bool:
    """Returns True if the DB is reachable."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def execute_query(sql: str, params: dict = None) -> list:
    """Run a raw SELECT and return a list of Row objects."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return result.fetchall()


def execute_write(sql: str, params: dict = None) -> int:
    """Run an INSERT / UPDATE / DELETE. Returns rowcount."""
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text(sql), params or {})
        return result.rowcount
