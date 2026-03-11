from collections.abc import Generator
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_db
from app.exceptions import ServiceError
from app.main import app


def test_create_ticket(client: TestClient) -> None:
    """Create a ticket and verify the response."""
    response = client.post(
        "/tickets/",
        json={"title": "Bug fix", "description": "Fix login issue", "status": "open"},
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["title"] == "Bug fix"
    assert data["description"] == "Fix login issue"
    assert data["status"] == "open"
    assert "id" in data
    assert "created_at" in data


def test_create_ticket_default_status(client: TestClient) -> None:
    """Create a ticket without status, defaults to open."""
    response = client.post(
        "/tickets/",
        json={"title": "Task", "description": "Do something"},
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["status"] == "open"


def test_list_tickets_empty(client: TestClient) -> None:
    """List tickets returns empty list when no tickets exist."""
    response = client.get("/tickets/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_list_tickets(client: TestClient) -> None:
    """List tickets returns all created tickets."""
    client.post("/tickets/", json={"title": "A", "description": "Desc A"})
    client.post("/tickets/", json={"title": "B", "description": "Desc B"})
    response = client.get("/tickets/")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2
    titles = {ticket["title"] for ticket in data}
    assert titles == {"A", "B"}


def test_get_ticket(client: TestClient) -> None:
    """Get a ticket by id."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "Get me", "description": "Test"},
    )
    ticket_id = create_resp.json()["id"]
    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == "Get me"


def test_get_ticket_not_found(client: TestClient) -> None:
    """Get returns 404 for non-existent ticket."""
    response = client.get("/tickets/99999")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket(client: TestClient) -> None:
    """Update a ticket."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "Original", "description": "Original desc"},
    )
    ticket_id = create_resp.json()["id"]
    response = client.put(
        f"/tickets/{ticket_id}",
        json={"title": "Updated", "description": "Updated desc", "status": "stalled"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "Updated desc"
    assert data["status"] == "stalled"


def test_update_ticket_partial(client: TestClient) -> None:
    """Update only provided fields."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "Original", "description": "Original desc"},
    )
    ticket_id = create_resp.json()["id"]
    response = client.put(
        f"/tickets/{ticket_id}",
        json={"title": "New title"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["title"] == "New title"
    assert data["description"] == "Original desc"


def test_update_ticket_not_found(client: TestClient) -> None:
    """Update returns 404 for non-existent ticket."""
    response = client.put(
        "/tickets/99999",
        json={"title": "X", "description": "Y", "status": "open"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_close_ticket(client: TestClient) -> None:
    """Close a ticket."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "To close", "description": "Test"},
    )
    ticket_id = create_resp.json()["id"]
    response = client.patch(f"/tickets/{ticket_id}/close")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "closed"


def test_close_ticket_not_found(client: TestClient) -> None:
    """Close returns 404 for non-existent ticket."""
    response = client.patch("/tickets/99999/close")
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_create_ticket_validation_empty_title(client: TestClient) -> None:
    """Create rejects empty title."""
    response = client.post(
        "/tickets/",
        json={"title": "", "description": "Valid desc"},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_ticket_validation_empty_description(client: TestClient) -> None:
    """Create rejects empty description."""
    response = client.post(
        "/tickets/",
        json={"title": "Valid title", "description": ""},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_ticket_validation_invalid_status(client: TestClient) -> None:
    """Create rejects invalid status."""
    response = client.post(
        "/tickets/",
        json={"title": "Valid", "description": "Valid desc", "status": "invalid"},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_ticket_validation_invalid_status(client: TestClient) -> None:
    """Update rejects invalid status."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "Original", "description": "Original desc"},
    )
    ticket_id = create_resp.json()["id"]
    response = client.put(
        f"/tickets/{ticket_id}",
        json={"title": "Original", "description": "Original desc", "status": "pending"},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_ticket_extra_fields_rejected(client: TestClient) -> None:
    """Create rejects request with extra fields."""
    response = client.post(
        "/tickets/",
        json={
            "title": "Valid",
            "description": "Valid desc",
            "status": "open",
            "extra_field": "not allowed",
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_ticket_service_error_returns_500(client: TestClient) -> None:
    """Create returns 500 with generic message when service raises ServiceError."""
    with patch("app.api.routes.tickets.ticket_service.create_ticket") as mock_create:
        mock_create.side_effect = ServiceError("Could not create ticket")
        response = client.post(
            "/tickets/",
            json={"title": "Bug", "description": "Fix it", "status": "open"},
        )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Something went wrong. Please try again later."


def test_get_ticket_service_error_returns_500(client: TestClient) -> None:
    """Get returns 500 with generic message when service raises ServiceError."""
    with patch("app.api.routes.tickets.ticket_service.get_ticket") as mock_get:
        mock_get.side_effect = ServiceError("Could not get ticket")
        response = client.get("/tickets/1")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Something went wrong. Please try again later."


def test_root_returns_ok(client: TestClient) -> None:
    """Root endpoint returns health status."""
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


def test_list_tickets_service_error_returns_500(client: TestClient) -> None:
    """List returns 500 with generic message when service raises ServiceError."""
    with patch("app.api.routes.tickets.ticket_service.get_tickets") as mock_get:
        mock_get.side_effect = ServiceError("Could not list tickets")
        response = client.get("/tickets/")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Something went wrong. Please try again later."


def test_update_ticket_service_error_on_get_returns_500(client: TestClient) -> None:
    """Update returns 500 when get_ticket raises ServiceError."""
    with patch("app.api.routes.tickets.ticket_service.get_ticket") as mock_get:
        mock_get.side_effect = ServiceError("Could not get ticket")
        response = client.put(
            "/tickets/1",
            json={"title": "X", "description": "Y", "status": "open"},
        )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_update_ticket_service_error_on_update_returns_500(client: TestClient) -> None:
    """Update returns 500 when update_ticket raises ServiceError."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "Original", "description": "Original desc"},
    )
    ticket_id = create_resp.json()["id"]
    with patch("app.api.routes.tickets.ticket_service.update_ticket") as mock_update:
        mock_update.side_effect = ServiceError("Could not update ticket")
        response = client.put(
            f"/tickets/{ticket_id}",
            json={"title": "Updated", "description": "Updated desc", "status": "open"},
        )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_close_ticket_service_error_on_get_returns_500(client: TestClient) -> None:
    """Close returns 500 when get_ticket raises ServiceError."""
    with patch("app.api.routes.tickets.ticket_service.get_ticket") as mock_get:
        mock_get.side_effect = ServiceError("Could not get ticket")
        response = client.patch("/tickets/1/close")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_close_ticket_service_error_on_close_returns_500(client: TestClient) -> None:
    """Close returns 500 when close_ticket raises ServiceError."""
    create_resp = client.post(
        "/tickets/",
        json={"title": "To close", "description": "Test"},
    )
    ticket_id = create_resp.json()["id"]
    with patch("app.api.routes.tickets.ticket_service.close_ticket") as mock_close:
        mock_close.side_effect = ServiceError("Could not close ticket")
        response = client.patch(f"/tickets/{ticket_id}/close")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def _bad_get_db_commit_fails() -> Generator[MagicMock, None, None]:
    """Session that raises SQLAlchemyError on commit (triggers repository → service error chain)."""
    session = MagicMock()
    session.commit.side_effect = SQLAlchemyError("database error")
    session.rollback = MagicMock()
    try:
        yield session
    finally:
        pass


def _bad_get_db_query_fails() -> Generator[MagicMock, None, None]:
    """Session that raises SQLAlchemyError on query (triggers repository → service error chain)."""
    session = MagicMock()
    session.query.side_effect = SQLAlchemyError("database error")
    session.rollback = MagicMock()
    try:
        yield session
    finally:
        pass


def test_create_ticket_db_error_returns_500(client: TestClient) -> None:
    """Create returns 500 when repository raises RepositoryError (DB commit fails)."""
    app.dependency_overrides[get_db] = _bad_get_db_commit_fails
    try:
        response = client.post(
            "/tickets/",
            json={"title": "Bug", "description": "Fix it", "status": "open"},
        )
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Something went wrong. Please try again later."
    finally:
        app.dependency_overrides.clear()


def test_list_tickets_db_error_returns_500(client: TestClient) -> None:
    """List returns 500 when repository raises RepositoryError (DB query fails)."""
    app.dependency_overrides[get_db] = _bad_get_db_query_fails
    try:
        response = client.get("/tickets/")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Something went wrong. Please try again later."
    finally:
        app.dependency_overrides.clear()


def test_get_ticket_db_error_returns_500(client: TestClient) -> None:
    """Get returns 500 when repository raises RepositoryError (DB query fails)."""
    app.dependency_overrides[get_db] = _bad_get_db_query_fails
    try:
        response = client.get("/tickets/1")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Something went wrong. Please try again later."
    finally:
        app.dependency_overrides.clear()


def _bad_get_db_commit_fails_after_get() -> Generator[MagicMock, None, None]:
    """Session where get works but commit raises (for update/close flows)."""
    mock_ticket = MagicMock()
    mock_ticket.id = 1
    mock_ticket.title = "X"
    mock_ticket.description = "Y"
    mock_ticket.status = "open"
    mock_ticket.created_at = MagicMock()
    session = MagicMock()
    session.query.return_value.filter.return_value.first.return_value = mock_ticket
    session.query.return_value.order_by.return_value.all.return_value = []
    session.commit.side_effect = SQLAlchemyError("database error")
    session.rollback = MagicMock()
    try:
        yield session
    finally:
        pass


def test_update_ticket_db_error_returns_500(client: TestClient) -> None:
    """Update returns 500 when repository raises RepositoryError (DB commit fails)."""
    app.dependency_overrides[get_db] = _bad_get_db_commit_fails_after_get
    try:
        response = client.put(
            "/tickets/1",
            json={"title": "Updated", "description": "Updated desc", "status": "stalled"},
        )
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Something went wrong. Please try again later."
    finally:
        app.dependency_overrides.clear()


def test_close_ticket_db_error_returns_500(client: TestClient) -> None:
    """Close returns 500 when repository raises RepositoryError (DB commit fails)."""
    app.dependency_overrides[get_db] = _bad_get_db_commit_fails_after_get
    try:
        response = client.patch("/tickets/1/close")
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Something went wrong. Please try again later."
    finally:
        app.dependency_overrides.clear()
