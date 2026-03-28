from sqlmodel import SQLModel, Field


class EmergencyCategory(SQLModel, table=True):
    __tablename__ = "emergency_category"
    __table_args__ = {"schema": "dar"}

    id_category: int | None = Field(default=None, primary_key=True)

    name: str
    color: str
    description: str | None = None