from sqlalchemy.orm import Session

from app.db.models import Ticket
from app.exceptions import RepositoryError, ServiceError
from app.repositories import ticket_repository
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    """Create a new ticket."""
    try:
        return ticket_repository.create(db, ticket_in)
    except RepositoryError as e:
        raise ServiceError("Could not create ticket", cause=e) from e


def get_tickets(db: Session) -> list[Ticket]:
    """Return all tickets."""
    try:
        return ticket_repository.get_all(db)
    except RepositoryError as e:
        raise ServiceError("Could not list tickets", cause=e) from e


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Return the ticket with the given id, or None if not found."""
    try:
        return ticket_repository.get_by_id(db, ticket_id)
    except RepositoryError as e:
        raise ServiceError("Could not get ticket", cause=e) from e


def update_ticket(db: Session, ticket: Ticket, ticket_in: TicketUpdate) -> Ticket:
    """Update a ticket with the provided data."""
    try:
        return ticket_repository.update(db, ticket, ticket_in)
    except RepositoryError as e:
        raise ServiceError("Could not update ticket", cause=e) from e


def close_ticket(db: Session, ticket: Ticket) -> Ticket:
    """Close a ticket."""
    try:
        return ticket_repository.close(db, ticket)
    except RepositoryError as e:
        raise ServiceError("Could not close ticket", cause=e) from e
