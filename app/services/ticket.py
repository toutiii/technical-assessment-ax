from sqlalchemy.orm import Session

from app.db.models import Ticket
from app.repositories import ticket_repository
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    """Create a new ticket."""
    return ticket_repository.create(db, ticket_in)


def get_tickets(db: Session) -> list[Ticket]:
    """Return all tickets."""
    return ticket_repository.get_all(db)


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Return the ticket with the given id, or None if not found."""
    return ticket_repository.get_by_id(db, ticket_id)


def update_ticket(db: Session, ticket: Ticket, ticket_in: TicketUpdate) -> Ticket:
    """Update a ticket with the provided data."""
    return ticket_repository.update(db, ticket, ticket_in)


def close_ticket(db: Session, ticket: Ticket) -> Ticket:
    """Close a ticket."""
    return ticket_repository.close(db, ticket)
