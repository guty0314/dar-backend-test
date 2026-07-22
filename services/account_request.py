import logging
import secrets

from fastapi import HTTPException
from pydantic import BaseModel

from models.account_request import AccountRequest
from models.user import User
from repositories.account_request_repository import AccountRequestRepository
from repositories.user_repository import UserRepository
from services.email_service import send_user_credentials, send_account_request_rejected

logger = logging.getLogger(__name__)


class NewAccountRequestData(BaseModel):
    full_name: str
    username: str  # legajo
    cuil: str
    jerarquia: str
    email: str
    destino: str


class ApproveRequestData(BaseModel):
    role: str = "agent"


class RejectRequestData(BaseModel):
    reason: str | None = None


class AccountRequestServices:

    @staticmethod
    def create_request(data: NewAccountRequestData) -> AccountRequest:
        if not data.full_name:
            raise HTTPException(status_code=400, detail="El nombre y apellido es obligatorio")
        if not data.username:
            raise HTTPException(status_code=400, detail="El legajo es obligatorio")
        if not data.cuil:
            raise HTTPException(status_code=400, detail="El CUIL es obligatorio")
        if not data.jerarquia:
            raise HTTPException(status_code=400, detail="La jerarquía es obligatoria")
        if not data.email:
            raise HTTPException(status_code=400, detail="El email es obligatorio")
        if not data.destino:
            raise HTTPException(status_code=400, detail="El destino es obligatorio")

        if UserRepository.get_user_by_username(data.username):
            raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese legajo")

        if AccountRequestRepository.get_pending_by_username(data.username):
            raise HTTPException(status_code=400, detail="Ya hay una solicitud pendiente para ese legajo")

        request = AccountRequest(
            full_name=data.full_name,
            username=data.username,
            cuil=data.cuil,
            jerarquia=data.jerarquia,
            email=data.email,
            destino=data.destino,
        )
        return AccountRequestRepository.create(request)

    @staticmethod
    async def approve_request(id_request: int, role: str, current_user: User) -> AccountRequest:
        request = AccountRequestRepository.get_by_id(id_request)
        if not request:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        if request.status != "pending":
            raise HTTPException(status_code=400, detail="La solicitud ya fue revisada")
        if role not in ["admin", "agent"]:
            raise HTTPException(status_code=400, detail="Rol inválido")
        if UserRepository.get_user_by_username(request.username):
            raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese usuario")

        from pwdlib import PasswordHash
        password_hash = PasswordHash.recommended()
        plain_password = secrets.token_urlsafe(9)
        hashed_password = password_hash.hash(plain_password)

        new_user = User(
            full_name=request.full_name,
            username=request.username,
            email=request.email,
            cuil=request.cuil,
            hashed_password=hashed_password,
            role=role,
            last_position_update=None,
        )
        created_user = UserRepository.create_user(new_user)

        try:
            await send_user_credentials(created_user.email, created_user.username, plain_password)
        except Exception as e:
            logger.error(f"Error enviando credenciales a {created_user.email}: {e}")

        return AccountRequestRepository.mark_approved(id_request, current_user.username)

    @staticmethod
    async def reject_request(id_request: int, reason: str | None, current_user: User) -> AccountRequest:
        request = AccountRequestRepository.get_by_id(id_request)
        if not request:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        if request.status != "pending":
            raise HTTPException(status_code=400, detail="La solicitud ya fue revisada")

        updated = AccountRequestRepository.mark_rejected(id_request, current_user.username, reason)

        try:
            await send_account_request_rejected(request.email, request.full_name, reason)
        except Exception as e:
            logger.error(f"Error enviando email de rechazo a {request.email}: {e}")

        return updated
