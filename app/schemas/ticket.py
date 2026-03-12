from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import TicketStatus


class TicketBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        ...,
        min_length=1,
        description="Short title of the ticket.",
        examples=["Fix broken CTA button on landing page"],
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed description of the issue/request.",
        examples=["Primary CTA is not clickable on mobile Safari (iOS 17)."],
    )
    status: TicketStatus = Field(
        default=TicketStatus.OPEN,
        description="Current status of the ticket.",
        examples=["open"],
    )


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(
        None,
        min_length=1,
        description="New title of the ticket.",
        examples=["Fix broken CTA button on landing page"],
    )
    description: str | None = Field(
        None,
        min_length=1,
        description="New description of the ticket.",
        examples=["Blocked: waiting for updated Figma specs from design."],
    )
    status: TicketStatus | None = Field(
        None,
        description="New status of the ticket.",
        examples=["stalled"],
    )


class TicketResponse(TicketBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int = Field(description="Ticket identifier.")
    created_at: datetime = Field(description="Ticket creation timestamp (UTC).")
