from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, Index
from enum import Enum


class ResponseStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    arrived = "arrived"


class EmergencyResponse(SQLModel, table=True):
    __tablename__ = "emergency_response"

    __table_args__ = (
        UniqueConstraint("id_emergency", "id_user", name="unique_emergency_user"),
        Index("idx_emergency_user", "id_emergency", "id_user"),
        {"schema": "dar"},
    )

    id_response: int | None = Field(default=None, primary_key=True)

    id_emergency: int = Field(
        foreign_key="dar.emergency.id_emergency",
        index=True
    )

    id_user: int = Field(
        foreign_key="public.user.id_user",
        index=True
    )

    status: ResponseStatus = Field(default=ResponseStatus.pending)

    accepted: bool = Field(default=False)
    arrived: bool = Field(default=False)

    response_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    arrival_time: datetime | None = None