import logging
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, status

from services.recaptcha import verify_recaptcha
from services.limiter import limiter

logger = logging.getLogger(__name__)


def InitAccountRequestRoutes(app: FastAPI):
    from models.user import User
    from services.user import admin_required
    from services.account_request import (
        AccountRequestServices,
        NewAccountRequestData,
        ApproveRequestData,
        RejectRequestData,
    )
    from repositories.account_request_repository import AccountRequestRepository

    # ================================
    # SOLICITAR CUENTA (PÚBLICO)
    # ================================
    @app.post("/account-requests/", tags=["account-requests"])
    @limiter.limit("3/minute")
    async def create_account_request(
        request: Request,
        data: NewAccountRequestData,
        captcha_token: str,
    ):
        if not verify_recaptcha(captcha_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Captcha inválido. Por favor, intente nuevamente.",
            )
        created = AccountRequestServices.create_request(data)
        return {"msg": "Solicitud enviada correctamente", "id_request": created.id_request}

    # ================================
    # LISTAR SOLICITUDES (ADMIN)
    # ================================
    @app.get("/admin/account-requests/", tags=["admin"])
    async def list_account_requests(
        current_user: Annotated[User, Depends(admin_required)],
        status: str | None = None,
    ):
        requests = AccountRequestRepository.get_all(status=status)
        return [
            {
                "id_request": r.id_request,
                "full_name": r.full_name,
                "username": r.username,
                "cuil": r.cuil,
                "jerarquia": r.jerarquia,
                "email": r.email,
                "destino": r.destino,
                "status": r.status,
                "created_at": r.created_at,
                "reviewed_at": r.reviewed_at,
                "reviewed_by": r.reviewed_by,
                "rejection_reason": r.rejection_reason,
            }
            for r in requests
        ]

    # ================================
    # APROBAR SOLICITUD (ADMIN)
    # ================================
    @app.post("/admin/account-requests/{id_request}/approve/", tags=["admin"])
    async def approve_account_request(
        id_request: int,
        data: ApproveRequestData,
        current_user: Annotated[User, Depends(admin_required)],
    ):
        return await AccountRequestServices.approve_request(id_request, data.role, current_user)

    # ================================
    # RECHAZAR SOLICITUD (ADMIN)
    # ================================
    @app.post("/admin/account-requests/{id_request}/reject/", tags=["admin"])
    async def reject_account_request(
        id_request: int,
        data: RejectRequestData,
        current_user: Annotated[User, Depends(admin_required)],
    ):
        return await AccountRequestServices.reject_request(id_request, data.reason, current_user)
