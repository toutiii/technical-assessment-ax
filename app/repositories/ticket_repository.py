from sqlalchemy.orm import Session

from app.db.models import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate


def create(db: Session, ticket_in: TicketCreate) -> Ticket:
    """Create a new ticket and persist it."""
    ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        status=ticket_in.status,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_all(db: Session) -> list[Ticket]:
    """Return all tickets ordered by creation date."""
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()


def get_by_id(db: Session, ticket_id: int) -> Ticket | None:
    """Return the ticket with the given id, or None if not found."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update(db: Session, ticket: Ticket, ticket_in: TicketUpdate) -> Ticket:
    """Update ticket fields with the provided data, ignoring None values."""
    data = ticket_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def close(db: Session, ticket: Ticket) -> Ticket:
    """Set the ticket status to closed."""
    ticket.status = TicketStatus.CLOSED
    db.commit()
    db.refresh(ticket)
    return ticket
