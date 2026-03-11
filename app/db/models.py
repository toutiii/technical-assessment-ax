import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    STALLED = "stalled"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        nullable=False,
        default=TicketStatus.OPEN,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
