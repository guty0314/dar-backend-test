from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_log"
    __table_args__ = {"schema": "public"}

    id_log: int | None = Field(default=None, primary_key=True)

    id_user: int = Field(foreign_key="public.user.id_user", index=True)
    username: str
    full_name: str | None = None

    action: str  # login, logout, emergency_sent, emergency_accepted, emergency_arrived
    detail: str | None = None  # info extra, ej: "Emergencia #42 - ROBO"

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    ip_address: str | None = None