import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def create_tables() -> None:
    """Create all database tables (idempotent)."""
    from app.db import models  # noqa: F401

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    tables = inspect(engine).get_table_names()
    logger.info(f"Database tables created: {tables}")
