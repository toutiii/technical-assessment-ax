from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Ticket, TicketStatus
from app.exceptions import RepositoryError
from app.schemas.ticket import TicketCreate, TicketUpdate


def create(db: Session, ticket_in: TicketCreate) -> Ticket:
    """Create a new ticket and persist it."""
    try:
        ticket = Ticket(
            title=ticket_in.title,
            description=ticket_in.description,
            status=ticket_in.status,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    except SQLAlchemyError as e:
        db.rollback()
        raise RepositoryError("Failed to create ticket", cause=e) from e


def get_all(db: Session) -> list[Ticket]:
    """Return all tickets ordered by creation date."""
    try:
        return db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    except SQLAlchemyError as e:
        raise RepositoryError("Failed to list tickets", cause=e) from e


def get_by_id(db: Session, ticket_id: int) -> Ticket | None:
    """Return the ticket with the given id, or None if not found."""
    try:
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()
    except SQLAlchemyError as e:
        raise RepositoryError("Failed to get ticket", cause=e) from e


def update(db: Session, ticket: Ticket, ticket_in: TicketUpdate) -> Ticket:
    """Update ticket fields with the provided data, ignoring None values."""
    try:
        data = ticket_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(ticket, field, value)
        db.commit()
        db.refresh(ticket)
        return ticket
    except SQLAlchemyError as e:
        db.rollback()
        raise RepositoryError("Failed to update ticket", cause=e) from e


def close(db: Session, ticket: Ticket) -> Ticket:
    """Set the ticket status to closed."""
    try:
        ticket.status = TicketStatus.CLOSED
        db.commit()
        db.refresh(ticket)
        return ticket
    except SQLAlchemyError as e:
        db.rollback()
        raise RepositoryError("Failed to close ticket", cause=e) from e
