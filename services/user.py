from typing import Annotated
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from services.utils import oauth2_scheme
from repositories.user_repository import UserRepository
from models.user import User

print("🔥 SERVICES.USER CARGADO 🔥")
class NewUserData(BaseModel):
    """
    Información necesaria para crear un nuevo usuario.
    """
    username: str
    full_name: str
    password: str

class UpdateUserData(BaseModel):
    full_name: str | None = None
    email: str | None = None
    number_phone: str | None = None
    role: str | None = None
    disabled: bool | None = None

class UserServices:

    @staticmethod
    def authenticate_user(username: str, password: str):
        user = UserRepository.get_user_by_username(username)
        if not user:
            return False
        if not user.verify_password(password):
            return False
        return user

    @staticmethod
    def update_my_position(latitude: float, longitude: float, user: User):
        user.latitude = latitude
        user.longitude = longitude
        user.last_position_update = datetime.now()
        UserRepository.update_user(user)

        return {
            "msg": "Position updated",
            "latitude": latitude,
            "longitude": longitude
        }

    @staticmethod
    def register_device_token(device_token: str, user: User):
        user.set_device_token(device_token)
        return {"msg": "Device token registered"}

    @staticmethod
    def get_my_position(user: User):
        latitude, longitude = user.get_user_position()
        return {
            "latitude": latitude,
            "longitude": longitude,
            "last_update": user.last_position_update
        }

    @staticmethod
    def create_user(user: NewUserData, current_user: User) -> User:

        # 🔐 Solo admins pueden crear usuarios
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required"
            )

        if not user.username:
            raise HTTPException(status_code=400, detail="Username cannot be empty")

        if not user.password:
            raise HTTPException(status_code=400, detail="Password cannot be empty")

        if not user.full_name:
            raise HTTPException(status_code=400, detail="Full name cannot be empty")

        existing_user = UserRepository.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        from pwdlib import PasswordHash
        password_hash = PasswordHash.recommended()
        hashed_password = password_hash.hash(user.password)

        new_user = User(
            full_name=user.full_name,
            username=user.username,
            hashed_password=hashed_password,
            role="agent",  # 👈 por defecto los nuevos usuarios son agentes
            online=False
        )

        return UserRepository.create_user(new_user)

    @staticmethod
    def logout_user(user: User):
        user.online = False
        UserRepository.update_user(user)
        return {"msg": "User logged out successfully"}


# 🔐 Obtener usuario desde JWT
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    import jwt
    from jwt.exceptions import InvalidTokenError
    from services.utils import SECRET_KEY, ALGORITHM

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    user = UserRepository.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    # Sincronizar rol desde el token
    if role:
        user.role = role

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# 🔐 Dependencia exclusiva para admins
async def admin_required(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user