from fastapi import Depends, FastAPI, BackgroundTasks, WebSocket

def InitEmergencyRoutes(app: FastAPI):
    from typing import Annotated

    from models.user import User
    from models.emergency import EmergencyRequest
    from services.emergency import EmergencyServices
    from services.user import get_current_active_user

    # Recibe la emergencia
    # Requiere que exista un usuario activo
    @app.post("/emergencies/")
    async def send_emergency(
        emergency_request: EmergencyRequest,
        current_user: Annotated[User, Depends(get_current_active_user)],
        background_tasks: BackgroundTasks,
    ):
        result = await EmergencyServices.send_emergency(emergency_request, current_user, background_tasks)
        return result
    
    @app.post("/emergencies/{emergency_id}/cancel/")
    async def cancel_emergency(
        emergency_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        result = await EmergencyServices.cancel_emergency(emergency_id, current_user)
        return result
    
    @app.websocket("/emergencies/check_my_emergency/")
    async def check_emergency(
        websocket: WebSocket,
    ):
        await EmergencyServices.check_emergency(websocket)
    
    @app.websocket("/emergencies/im_on_alert/")
    async def notice_if_im_on_alert(
        websocket: WebSocket
    ):
       await EmergencyServices.notice_if_im_on_alert(websocket)