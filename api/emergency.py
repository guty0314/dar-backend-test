from fastapi import Depends, FastAPI, BackgroundTasks, WebSocket
from repositories.user_repository import UserRepository


def InitEmergencyRoutes(app: FastAPI):
    from typing import Annotated

    from models.user import User
    from models.emergency import EmergencyRequest
    from services.emergency import EmergencyServices
    from services.user import get_current_active_user
    from repositories.emergency_repository import EmergencyRepository


    # -----------------------------
    # CREAR EMERGENCIA
    # -----------------------------
    @app.post("/emergencies/")
    async def send_emergency(
        emergency_request: EmergencyRequest,
        current_user: Annotated[User, Depends(get_current_active_user)],
        background_tasks: BackgroundTasks,
    ):
        return await EmergencyServices.send_emergency(
            emergency_request,
            current_user,
            background_tasks
        )


    # -----------------------------
    # CANCELAR EMERGENCIA
    # -----------------------------
    @app.post("/emergencies/{emergency_id}/cancel/")
    async def cancel_emergency(
        emergency_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return await EmergencyServices.cancel_emergency(
            emergency_id,
            current_user
        )


    # -----------------------------
    # ACEPTAR EMERGENCIA
    # -----------------------------
    @app.post("/emergencies/{emergency_id}/accept/")
    async def accept_emergency(
        emergency_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return await EmergencyServices.accept_emergency(
            emergency_id,
            current_user
        )


    # -----------------------------
    # MARCAR LLEGADA NUEVO
    # -----------------------------
    @app.post("/emergencies/{emergency_id}/arrive/")
    async def arrive_emergency(
        emergency_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return await EmergencyServices.arrive_emergency(
            emergency_id,
            current_user
        )

    # -----------------------------
    # USUARIOS CERCANOS  NUEVO
    # -----------------------------
    @app.get("/users/nearby/")
    async def get_nearby_users(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return await EmergencyServices.get_nearby_users(current_user)

    # -----------------------------
    # LISTAR EMERGENCIAS (ADMIN)
    # -----------------------------
    @app.get("/admin/emergencies/")
    async def list_emergencies(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        emergencies = EmergencyRepository.get_all_emergencies()

        return [
            {
                "id": e.id_emergency,
                "latitude": float(e.latitude),
                "longitude": float(e.longitude),
                "id_type": e.id_type,
                "id_user": e.id_user,
                "active": e.active,
                "date_created": str(e.date_created),
            }
            for e in emergencies
        ]

    # -----------------------------
    # WEBSOCKET PRIMER INTERVINIENTE
    # -----------------------------
    @app.websocket("/emergencies/check_my_emergency/")
    async def check_emergency(
        websocket: WebSocket,
    ):
        await EmergencyServices.check_emergency(websocket)


    # -----------------------------
    # WEBSOCKET ALERTA GENERAL
    # -----------------------------
    @app.websocket("/emergencies/im_on_alert/")
    async def notice_if_im_on_alert(
        websocket: WebSocket
    ):
        await EmergencyServices.notice_if_im_on_alert(websocket)