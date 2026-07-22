from sqlmodel import SQLModel, Field


class AppConfig(SQLModel, table=True):
    """
    Configuración general de la app en formato clave/valor (ej: URL del video tutorial),
    editable por un admin sin necesidad de una nueva versión de la app.
    """
    __tablename__ = "app_config"
    __table_args__ = {"schema": "public"}

    id_config: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    value: str | None = None
