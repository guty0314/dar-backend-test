from sqlmodel import Session, select

from db.session import engine
from models.app_config import AppConfig


class AppConfigRepository:
    """
    Clase que accede a la base de datos para trabajar la configuración general de la app
    """
    @staticmethod
    def get_value(key: str) -> str | None:
        with Session(engine) as session:
            config = session.exec(
                select(AppConfig).where(AppConfig.key == key)
            ).first()
            return config.value if config else None

    @staticmethod
    def set_value(key: str, value: str) -> AppConfig:
        with Session(engine) as session:
            config = session.exec(
                select(AppConfig).where(AppConfig.key == key)
            ).first()

            if config:
                config.value = value
            else:
                config = AppConfig(key=key, value=value)

            session.add(config)
            session.commit()
            session.refresh(config)
            return config
