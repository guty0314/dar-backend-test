from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class EmergencyResponse(SQLModel, table=True):
    __tablename__ = "emergency_response"
    __table_args__ = {"schema": "dar"}

    id_response: int | None = Field(default=None, primary_key=True)

    id_emergency: int = Field(
        foreign_key="dar.emergency.id_emergency",
        index=True
    )

    id_user: int = Field(
        foreign_key="public.user.id_user",
        index=True
    )

    status: str = Field(default="pending")

    accepted: bool = Field(default=False)
    arrived: bool = Field(default=False)

    response_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )