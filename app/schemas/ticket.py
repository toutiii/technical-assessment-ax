from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import TicketStatus


class TicketBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    status: TicketStatus = TicketStatus.OPEN


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    status: TicketStatus | None = None


class TicketResponse(TicketBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    created_at: datetime
