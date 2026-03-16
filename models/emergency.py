from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from decimal import Decimal

from services.emergencyring import Ring

class EmergencyColor(str, Enum):
    rojo = "rojo"
    amarillo = "amarillo"
    verde = "verde"

class EmergencyRequest(BaseModel):
        """
        Modelo para armar una solicitud de emergencia.
        """
        latitude: float
        longitude: float
        emergency_color: EmergencyColor

class Emergency(SQLModel, table=True):
    """
    Representa las emergencias. Esto puede ser guardado en la base de datos.
    """
    __tablename__ = "emergency"
    
    id_emergency: int | None = Field(default=None, primary_key=True)
    
    latitude: Decimal = Field(sa_column=Column(Numeric(10, 7)))
    longitude: Decimal = Field(sa_column=Column(Numeric(10, 7)))
    
    type_emergency: EmergencyColor
    active: bool = True
    date_created: datetime = Field(default_factory=datetime.now())
    
    id_user: int | None = Field(default= None, foreign_key="user.id_user" )

    id_first_responder: int | None = Field(default=None, foreign_key="user.id_user")

    def get_emergency_users_data(self):
        from repositories.user_repository import UserRepository

        users_data = {}
        users_list = UserRepository.get_all_users()
        for u in users_list:

            # Ignorar a usuarios desconectados
            if not u.online:
                continue

            user_id = u.id_user
            user_lat = u.latitude
            user_lon = u.longitude

            zone = self.generate_emergency_ring().contains(user_lat, user_lon)
            if user_id == self.id_first_responder:
                zone = -1  # El primer interviniente se marca como -1 para avisar que es el origen
            elif zone == 0:
                continue

            users_data[u.username] = {
                "latitude": float(user_lat),
                "longitude": float(user_lon),
                "last_position_update": u.last_position_update.isoformat() if u.last_position_update else None,
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
            emergency = session.merge(self)  # Fusiona el objeto con la sesión
            session.add(emergency)
            session.commit()