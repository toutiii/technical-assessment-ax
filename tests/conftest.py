from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.db.database import Base, create_tables, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db() -> Generator[None, None, None]:
    """Reset the database before each test for isolation."""
    Base.metadata.drop_all(bind=engine)
    create_tables()
    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a test client for the API."""
    with TestClient(app) as c:
        yield c
