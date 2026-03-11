from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services import ticket as ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=HTTPStatus.CREATED)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
) -> Ticket:
    """Create a new ticket."""
    created_ticket = ticket_service.create_ticket(db, ticket_in)
    return created_ticket


@router.get("/", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)) -> list[Ticket]:
    """Return all tickets."""
    tickets = ticket_service.get_tickets(db)
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Ticket:
    """Return a ticket by id."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
) -> Ticket:
    """Update a ticket by id."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")
    ticket = ticket_service.update_ticket(db, ticket, ticket_data)
    return ticket


@router.patch("/{ticket_id}/close", response_model=TicketResponse)
def close_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> Ticket:
    """Close a ticket by id."""
    ticket = ticket_service.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")
    ticket = ticket_service.close_ticket(db, ticket)
    return ticket
