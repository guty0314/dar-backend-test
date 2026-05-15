"""
api/chat.py
"""

import jwt
import os
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from jwt.exceptions import InvalidTokenError

# Carpeta base donde se guardan las imágenes
IMAGES_BASE_DIR = "media/chat"


def get_image_save_path(id_emergency: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    relative_dir = os.path.join(
        IMAGES_BASE_DIR,
        str(now.year),
        f"{now.month:02d}",
        f"{now.day:02d}",
        f"emergencia_{id_emergency}",
    )
    os.makedirs(relative_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    return relative_dir, filename


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
        return ChatMessageRepository.get_by_emergency(id_emergency)

    # ──────────────────────────────────────────
    # REST — subir imagen
    # ──────────────────────────────────────────

    @app.post(
        "/chat/{id_emergency}/upload-image/",
        tags=["chat"],
        summary="Subir imagen al chat de una emergencia",
    )
    async def upload_chat_image(
        id_emergency: int,
        token: str = Form(...),
        file: UploadFile = File(...),
    ):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            current_user = UserRepository.get_user_by_username(username)
            if not current_user:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Usuario no encontrado")
        except InvalidTokenError:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Token inválido")

        content_type = file.content_type or ""
        if not content_type.startswith("image/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Solo se permiten imágenes")

        save_dir, filename = get_image_save_path(id_emergency)
        file_path = os.path.join(save_dir, filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        image_url = "/" + file_path.replace("\\", "/")

        msg = ChatMessageRepository.create(
            ChatMessageCreate(
                id_emergency=id_emergency,
                id_user=current_user.id_user,
                sender_name=current_user.full_name or current_user.username,
                sender_role=current_user.role if hasattr(current_user, "role") else "usuario",
                message="📷 Imagen",
                image_url=image_url,
            )
        )

        await chat_manager.broadcast(
            {
                "id_message": msg.id_message,
                "id_emergency": msg.id_emergency,
                "id_user": msg.id_user,
                "sender_name": msg.sender_name,
                "sender_role": msg.sender_role,
                "message": msg.message,
                "image_url": msg.image_url,
                "timestamp": msg.timestamp.isoformat(),
            },
            id_emergency,
        )

        return {
            "ok": True,
            "image_url": image_url,
            "id_message": msg.id_message,
        }

    # ──────────────────────────────────────────
    # WebSocket — chat en tiempo real
    # ──────────────────────────────────────────

    @app.websocket("/chat/ws/{id_emergency}/")
    async def chat_websocket(websocket: WebSocket, id_emergency: int):
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

        chat_manager.rooms.setdefault(id_emergency, []).append(websocket)
        print(f"✅ Chat WS: {current_user.username} se unió a sala {id_emergency}")

        try:
            while True:
                data = await websocket.receive_json()
                message_text = data.get("message", "").strip()

                if not message_text:
                    await websocket.send_json({"error": "Mensaje vacío"})
                    continue

                msg = ChatMessageRepository.create(
                    ChatMessageCreate(
                        id_emergency=id_emergency,
                        id_user=current_user.id_user,
                        sender_name=current_user.full_name or current_user.username,
                        sender_role=current_user.role if hasattr(current_user, "role") else "usuario",
                        message=message_text,
                        image_url=None,
                    )
                )

                await chat_manager.broadcast(
                    {
                        "id_message": msg.id_message,
                        "id_emergency": msg.id_emergency,
                        "id_user": msg.id_user,
                        "sender_name": msg.sender_name,
                        "sender_role": msg.sender_role,
                        "message": msg.message,
                        "image_url": msg.image_url,
                        "timestamp": msg.timestamp.isoformat(),
                    },
                    id_emergency,
                )

        except WebSocketDisconnect:
            chat_manager.disconnect(websocket, id_emergency)
            print(f"🔌 Chat WS: {current_user.username} salió de sala {id_emergency}")