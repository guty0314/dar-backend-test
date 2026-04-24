# Para hashear contraseñas (NUNCA guardar contraseñas en texto plano)
from pwdlib import PasswordHash
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from decimal import Decimal
from datetime import datetime

password_hash = PasswordHash.recommended()


class User(SQLModel, table=True):
    """
    Clase que aloja la informacion del usuario, que son los policias registrados en el sistema.
    """
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}  # 🔥 IMPORTANTE

    id_user: int | None = Field(default=None, primary_key=True)

    username: str = Field(index=True)
    full_name: str | None = None

    disabled: bool | None = Field(default=False)

    hashed_password: str

    number_phone: str | None = None
    email: str | None = Field(default=None, index=True)

    latitude: Decimal = Field(sa_column=Column(Numeric(10, 7)), default=0.0)
    longitude: Decimal = Field(sa_column=Column(Numeric(10, 7)), default=0.0)

    device_token: str | None = None

    is_admin: bool = Field(default=0)
    role: str = Field(default="agent", index=True)

    last_login: datetime | None = Field(default=None)
    last_position_update: datetime | None = Field(default=None)

    cuil: str = Field(index=True)

    # -----------------------------
    # MÉTODOS
    # -----------------------------

    def get_user_position(self):
        return (self.latitude, self.longitude)

    def verify_password(self, plain_password):
        return password_hash.verify(plain_password, self.hashed_password)

    def set_lat_lon(self, lat: float, lon: float):
        from sqlmodel import Session
        from db.session import engine
        from datetime import datetime, timezone

        with Session(engine) as session:
            self.latitude = lat
            self.longitude = lon
            self.last_position_update = datetime.now(timezone.utc)  # 🔥 CLAVE

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

    def is_session_active(self) -> bool:
        if self.last_login is None:
            return False
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        last = self.last_login
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return (now - last) < timedelta(hours=8)
    # -----------------------------
    # ESTADO DEL USUARIO
    # -----------------------------

    @property
    def status(self) -> str:
        from datetime import datetime, timezone, timedelta

        if not self.last_position_update:
            return "offline"

        now = datetime.now(timezone.utc)
        last = self.last_position_update

        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)

        delta = now - last

        if delta < timedelta(minutes=2):
            return "online"
        elif delta < timedelta(minutes=10):
            return "recent"
        else:
            return "offline"

    @property
    def online(self) -> bool:
        return self.status == "online"