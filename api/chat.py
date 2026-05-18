"""
api/chat.py
"""

import jwt
import os
import uuid
import boto3
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from jwt.exceptions import InvalidTokenError

# ── Configuración S3 ──────────────────────────────────────
S3_BUCKET = os.getenv("S3_BUCKET", "amzn-s3-dar-files-test")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def get_s3_key(id_emergency: int, filename: str) -> str:
    """
    Estructura: chat/2025/05/14/emergencia_7/uuid.jpg
    """
    now = datetime.now(timezone.utc)
    return (
        f"chat/{now.year}/{now.month:02d}/{now.day:02d}"
        f"/emergencia_{id_emergency}/{filename}"
    )


def get_s3_url(key: str) -> str:
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"


# ─────────────────────────────────────────────────────────


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
    # REST — subir imagen a S3
    # ──────────────────────────────────────────

    @app.post(
        "/chat/{id_emergency}/upload-image/",
        tags=["chat"],
        summary="Subir imagen al chat (S3)",
    )
    async def upload_chat_image(
        id_emergency: int,
        token: str = Form(...),
        file: UploadFile = File(...),
    ):
        # Validar token
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

        # Validar tipo de archivo
        content_type = file.content_type or ""
        if content_type and not content_type.startswith("image/") and content_type != "application/octet-stream":
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Solo se permiten imágenes")

        # Leer contenido
        content = await file.read()

        # Generar key S3
        filename = f"{uuid.uuid4().hex}.jpg"
        s3_key = get_s3_key(id_emergency, filename)

        # Subir a S3
        try:
            s3 = get_s3_client()
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=content,
                ContentType="image/jpeg",
            )
        except Exception as e:
            from fastapi import HTTPException
            print(f"❌ Error subiendo a S3: {e}")
            raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

        # URL pública
        image_url = get_s3_url(s3_key)

        # Guardar mensaje
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

        # Broadcast
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