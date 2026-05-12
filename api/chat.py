"""
api/chat.py

Endpoints REST y WebSocket para el chat por emergencia.
Se registra en main.py igual que los demás: InitChatRoutes(app)

Patrón de autenticación WS igual al resto del proyecto:
  - El cliente conecta al WS
  - Envía como primer mensaje JSON: { "token": "<jwt>", "id_emergency": 7 }
  - Si el token es válido, entra a la sala; si no, se cierra la conexión
"""

import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from jwt.exceptions import InvalidTokenError


def InitChatRoutes(app: FastAPI):
    from typing import List
    from models.chat_message import ChatMessageCreate, ChatMessageRead
    from repositories.chat_message_repository import ChatMessageRepository
    from services.chat_ws import chat_manager
    from services.utils import SECRET_KEY, ALGORITHM
    from repositories.user_repository import UserRepository

    # ──────────────────────────────────────────
    # REST — historial de mensajes
    # ──────────────────────────────────────────

    @app.get(
        "/chat/{id_emergency}/messages/",
        response_model=List[ChatMessageRead],
        tags=["chat"],
    )
    async def get_chat_history(id_emergency: int):
        """
        Devuelve todos los mensajes de una emergencia, ordenados por timestamp ASC.
        No requiere autenticación para simplificar la carga inicial desde Flutter/React,
        pero podés agregar Depends(get_current_active_user) si querés protegerlo.
        """
        return ChatMessageRepository.get_by_emergency(id_emergency)

    # ──────────────────────────────────────────
    # WebSocket — chat en tiempo real
    # ──────────────────────────────────────────

    @app.websocket("/chat/ws/{id_emergency}/")
    async def chat_websocket(websocket: WebSocket, id_emergency: int):
        """
        Protocolo:
        1. Cliente conecta.
        2. Cliente envía primer mensaje JSON con el token:
              { "token": "<jwt>" }
        3. Si el token es válido, se une a la sala de la emergencia.
        4. Para enviar un mensaje, el cliente manda:
              { "message": "Texto del mensaje" }
        5. El servidor persiste y hace broadcast a todos en la sala:
              {
                "id_message": 42,
                "id_emergency": 7,
                "id_user": 5,
                "sender_name": "Juan Pérez",
                "sender_role": "personal_campo",
                "message": "Llegué al lugar",
                "timestamp": "2025-05-11T14:32:00+00:00"
              }
        """

        # 1. Aceptar y esperar autenticación
        await websocket.accept()

        try:
            auth_data = await websocket.receive_json()
            token = auth_data.get("token", "")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            current_user = UserRepository.get_user_by_username(username)

            if not current_user:
                await websocket.close(code=1008, reason="User not found")
                return

        except InvalidTokenError:
            await websocket.close(code=1008, reason="Invalid token")
            return
        except Exception:
            await websocket.close(code=1011, reason="Auth error")
            return

        # 2. Unirse a la sala (ya está aceptado, usamos add directo en lugar de connect)
        chat_manager.rooms.setdefault(id_emergency, []).append(websocket)

        print(f"✅ Chat WS: {current_user.username} se unió a sala {id_emergency}")

        try:
            while True:
                data = await websocket.receive_json()
                message_text = data.get("message", "").strip()

                if not message_text:
                    await websocket.send_json({"error": "Mensaje vacío"})
                    continue

                # Persistir
                msg = ChatMessageRepository.create(
                    ChatMessageCreate(
                        id_emergency=id_emergency,
                        id_user=current_user.id_user,
                        sender_name=current_user.full_name or current_user.username,
                        sender_role=current_user.role if hasattr(current_user, "role") else "usuario",
                        message=message_text,
                    )
                )

                # Broadcast a la sala
                await chat_manager.broadcast(
                    {
                        "id_message": msg.id_message,
                        "id_emergency": msg.id_emergency,
                        "id_user": msg.id_user,
                        "sender_name": msg.sender_name,
                        "sender_role": msg.sender_role,
                        "message": msg.message,
                        "timestamp": msg.timestamp.isoformat(),
                    },
                    id_emergency,
                )

        except WebSocketDisconnect:
            chat_manager.disconnect(websocket, id_emergency)
            print(f"🔌 Chat WS: {current_user.username} salió de sala {id_emergency}")