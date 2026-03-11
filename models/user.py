# Para hashear contraseñas (NUNCA guardar contraseñas en texto plano)
from pwdlib import PasswordHash
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from decimal import Decimal
from datetime import datetime

password_hash = PasswordHash.recommended()

# Clase User para manejar los usuarios.
# Note que todo lo que hereda de BaseModel es como un JSON
# que tiene de datos los miembros que se ven en dicha clase.
class User(SQLModel, table=True):
    """
    Clase que aloja la informacion del usuario, que son los policias registrados en el sistema.
    """
    __tablename__ = "user"

    id_user: int | None = Field(default=None, primary_key=True)
    username: str
    full_name: str | None = None
    disabled: bool | None = Field(default=False)
    hashed_password: str
    number_phone: str | None = None
    email: str | None = None
    latitude: Decimal = Field(sa_column=Column(Numeric(10, 7)), default=0.0)
    longitude: Decimal = Field(sa_column=Column(Numeric(10, 7)), default=0.0)
    device_token: str | None = None
    is_admin: bool = Field(default=0)
    role: str = Field(default="agent",index=True)
    online: bool = Field(default=0)
    last_login: datetime | None = Field(default=None)
    last_position_update: datetime | None = Field(default=None)
    cuil: str
    
    def get_user_position(self):
        """
        Obtiene la posicion (latitud, longitud) del usuario.
        """
        return (self.latitude, self.longitude)

    # Funcion que verifica los hashes de contraseñas
    def verify_password(self, plain_password):
        """
        Verifica si la contrasseña (texto plano) pertenece a esta cuenta.

        Argumentos:
            plain_password: La contraseña ingresada.

        Devuelve:
            True si coiciden, False en caso contrario.
        """
        return password_hash.verify(plain_password, self.hashed_password)
    
    def set_lat_lon(self, lat: float, lon: float):
        from sqlmodel import Session
        from db.session import engine

        with Session(engine) as session:
            self.latitude = lat
            self.longitude = lon
            user = session.merge(self)
            session.add(user)
            session.commit()

    def set_device_token(self, device_token: str):
        from sqlmodel import Session
        from db.session import engine

        with Session(engine) as session:
            self.device_token = device_token
            user = session.merge(self)
            session.add(user)
            session.commit()