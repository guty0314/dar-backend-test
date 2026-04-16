from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from decimal import Decimal

from services.emergencyring import Ring


# 🔥 REQUEST ACTUALIZADO
class EmergencyRequest(BaseModel):
    """
    Modelo para crear una emergencia.
    """
    latitude: float
    longitude: float
    id_type: int  # 🔥 ahora viene el tipo


class Emergency(SQLModel, table=True):
    """
    Representa las emergencias en la base de datos.
    """
    __tablename__ = "emergency"
    __table_args__ = {"schema": "dar"}  # 🔥 clave

    id_emergency: int | None = Field(default=None, primary_key=True)
    
    latitude: Decimal = Field(sa_column=Column(Numeric(10, 7)))
    longitude: Decimal = Field(sa_column=Column(Numeric(10, 7)))
    
    # 🔥 FK al tipo de emergencia
    id_type: int = Field(
        foreign_key="dar.emergency_type.id_type",
        index=True
    )

    active: bool = True

    date_created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
    # 🔥 FK al usuario (schema public)
    id_user: int | None = Field(
        default=None,
        foreign_key="public.user.id_user",
        index=True
    )

    # -----------------------------
    # MÉTODOS
    # -----------------------------

    def get_emergency_users_data(self):
        from repositories.user_repository import UserRepository

        users_data = {}
        users_list = UserRepository.get_all_users()

        for u in users_list:
            if u.status == "offline":
                continue

            user_lat = u.latitude
            user_lon = u.longitude

            #El que creó la emergencia siempre es zone -1
            if u.id_user == self.id_user:
                users_data[u.username] = {
                    "latitude": float(user_lat),
                    "longitude": float(user_lon),
                    "last_position_update": (
                        u.last_position_update.isoformat()
                        if u.last_position_update else None
                    ),
                    "zone": -1,
                }
                continue

            zone = self.generate_emergency_ring().contains(user_lat, user_lon)

            if zone == 0:
                continue

            users_data[u.username] = {
                "latitude": float(user_lat),
                "longitude": float(user_lon),
                "last_position_update": (
                    u.last_position_update.isoformat()
                    if u.last_position_update else None
                ),
                "zone": zone,
            }

        return users_data
    
    def generate_emergency_ring(self) -> Ring:
        return Ring(
            latitude=self.latitude,
            longitude=self.longitude
        )
    
    def disable_emergency(self) -> bool:
        from sqlmodel import Session
        from db.session import engine
        
        with Session(engine) as session:
            self.active = False
            emergency = session.merge(self)
            session.add(emergency)
            session.commit()
            return True