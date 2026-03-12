import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Ticket
from app.exceptions import ServiceError
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services import ticket as ticket_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["tickets"])

CLIENT_ERROR_MESSAGE = "Something went wrong. Please try again later."
NOT_FOUND_MESSAGE = "Ticket not found"


def _handle_service_error(e: ServiceError) -> HTTPException:
    """Map ServiceError to HTTPException (500). Log details server-side, return generic message."""
    logger.exception("Service error: %s", e.message)
    return HTTPException(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        detail=CLIENT_ERROR_MESSAGE,
    )


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=HTTPStatus.CREATED,
    summary="Create a ticket",
    description="Create a new ticket with title, description, and optional status.",
    responses={
        HTTPStatus.INTERNAL_SERVER_ERROR: {"description": "Internal server error."},
        HTTPStatus.UNPROCESSABLE_ENTITY: {"description": "Validation error."},
    },
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
) -> Ticket:
    """Create a new ticket."""
    try:
        return ticket_service.create_ticket(db, ticket_data)
    except ServiceError as e:
        raise _handle_service_error(e)


@router.get(
    "/",
    response_model=list[TicketResponse],
    summary="List tickets",
    description="Return all tickets ordered by creation date (newest first).",
    responses={
        HTTPStatus.INTERNAL_SERVER_ERROR: {"description": "Internal server error."},
    },
)
def list_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    """Return all tickets."""
    try:
        return ticket_service.get_tickets(db)
    except ServiceError as e:
        raise _handle_service_error(e)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get a ticket",
    description="Retrieve a ticket by its id.",
    responses={
        HTTPStatus.NOT_FOUND: {"description": "Ticket not found."},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"description": "Internal server error."},
    },
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Ticket:
    """Return a ticket by id."""
    try:
        ticket = ticket_service.get_ticket(db, ticket_id)
    except ServiceError as e:
        raise _handle_service_error(e)
    if ticket is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=NOT_FOUND_MESSAGE,
        )
    return ticket


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update a ticket",
    description=(
        "Update an existing ticket. Fields not provided are left unchanged.\n\n"
        "Note: extra fields are rejected."
    ),
    responses={
        HTTPStatus.NOT_FOUND: {"description": "Ticket not found."},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"description": "Internal server error."},
        HTTPStatus.UNPROCESSABLE_ENTITY: {"description": "Validation error."},
    },
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
) -> Ticket:
    """Update a ticket by id."""
    try:
        ticket = ticket_service.get_ticket(db, ticket_id)
    except ServiceError as e:
        raise _handle_service_error(e)
    if ticket is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=NOT_FOUND_MESSAGE,
        )
    try:
        return ticket_service.update_ticket(db, ticket, ticket_data)
    except ServiceError as e:
        raise _handle_service_error(e)


@router.patch(
    "/{ticket_id}/close",
    response_model=TicketResponse,
    summary="Close a ticket",
    description="Set the ticket status to `closed`.",
    responses={
        HTTPStatus.NOT_FOUND: {"description": "Ticket not found."},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"description": "Internal server error."},
    },
)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Ticket:
    """Close a ticket by id."""
    try:
        ticket = ticket_service.get_ticket(db, ticket_id)
    except ServiceError as e:
        raise _handle_service_error(e)
    if ticket is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=NOT_FOUND_MESSAGE,
        )
    try:
        return ticket_service.close_ticket(db, ticket)
    except ServiceError as e:
        raise _handle_service_error(e)
