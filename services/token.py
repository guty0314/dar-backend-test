from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from services.user import UserServices


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenServices:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        import jwt
        from services.utils import SECRET_KEY, ALGORITHM

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def login_for_access_token(form_data: OAuth2PasswordRequestForm) -> Token:
        from services.utils import ACCESS_TOKEN_EXPIRE_MINUTES
        from repositories.user_repository import UserRepository

        user = UserServices.authenticate_user(form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print("🔥 LOGIN EJECUTADO 🔥")
        print("Role del usuario:", user.role)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = TokenServices.create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id_user,
                "role": user.role
            },
            expires_delta=access_token_expires
        )

        user.online = True

        # ✅ FIX CLAVE
        user.last_login = datetime.now(timezone.utc)

        UserRepository.update_user(user)

        return Token(access_token=access_token, token_type="bearer")