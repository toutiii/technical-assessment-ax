from http import HTTPStatus

from fastapi.testclient import TestClient


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
