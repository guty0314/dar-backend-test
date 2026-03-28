from sqlmodel import SQLModel, Field


class EmergencyType(SQLModel, table=True):
    __tablename__ = "emergency_type"
    __table_args__ = {"schema": "dar"}

    id_type: int | None = Field(default=None, primary_key=True)

    name: str
    priority: int | None = None

    id_category: int = Field(
        foreign_key="dar.emergency_category.id_category",
        index=True
    )