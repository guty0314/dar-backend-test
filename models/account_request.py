from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class AccountRequest(SQLModel, table=True):
    """
    Solicitud de cuenta enviada por un usuario sin acceso, pendiente de revisión por un admin.
    """
    __tablename__ = "account_request"
    __table_args__ = {"schema": "public"}

    id_request: int | None = Field(default=None, primary_key=True)

    full_name: str
    username: str  # legajo
    cuil: str
    jerarquia: str
    email: str
    destino: str

    status: str = Field(default="pending", index=True)  # pending | approved | rejected

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    rejection_reason: str | None = None
