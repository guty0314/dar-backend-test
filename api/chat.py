"""
api/chat.py
"""

import jwt
import os
import uuid
import boto3
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import StreamingResponse
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
    now = datetime.now(timezone.utc)
    return (
        f"chat/{now.year}/{now.month:02d}/{now.day:02d}"
        f"/emergencia_{id_emergency}/{filename}"
    )


def s3_key_from_url(image_url: str) -> str:
    """Extrae el key de S3 desde la URL completa."""
    # https://bucket.s3.region.amazonaws.com/key
    prefix = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/"
    if image_url.startswith(prefix):
        return image_url[len(prefix):]
    return image_url


def get_proxy_url(base_url: str, image_url: str) -> str:
    """Convierte una URL de S3 en una URL del proxy del backend."""
    key = s3_key_from_url(image_url)
    import urllib.parse
    encoded_key = urllib.parse.quote(key, safe='')
    return f"{base_url}/chat/image/?key={encoded_key}"


# ─────────────────────────────────────────────────────────


def InitChatRoutes(app: FastAPI):
    from typing import Annotated
    from fastapi import Depends, HTTPException, Request
    from models.chat_message import ChatMessageCreate, ChatMessageRead
    from models.user import User
    from repositories.chat_message_repository import ChatMessageRepository
    from services.chat_ws import chat_manager
    from services.user import get_current_active_user
    from services.utils import SECRET_KEY, ALGORITHM
    from repositories.user_repository import UserRepository

    # ──────────────────────────────────────────
    # REST — historial de mensajes
    # ──────────────────────────────────────────

    @app.get(
        "/chat/{id_emergency}/messages/",
        tags=["chat"],
    )
    async def get_chat_history(
        id_emergency: int,
        request: Request,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        from repositories.emergency_repository import EmergencyRepository

        emergency = EmergencyRepository.get_emergency_by_id(id_emergency)
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergencia no encontrada")

        es_admin = current_user.role == "admin"
        es_creador = emergency.id_user == current_user.id_user
        es_respondedor = emergency.claimed_by == current_user.id_user

        if not (es_admin or es_creador or es_respondedor):
            raise HTTPException(status_code=403, detail="Sin acceso a esta emergencia")

        messages = ChatMessageRepository.get_by_emergency(id_emergency)
        base_url = str(request.base_url).rstrip("/")
        result = []
        for m in messages:
            result.append({
                "id_message": m.id_message,
                "id_emergency": m.id_emergency,
                "id_user": m.id_user,
                "sender_name": m.sender_name,
                "sender_role": m.sender_role,
                "message": m.message,
                "image_url": get_proxy_url(base_url, m.image_url) if m.image_url else None,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            })
        return result

    # ──────────────────────────────────────────
    # REST — proxy de imágenes S3
    # ──────────────────────────────────────────

    @app.get(
        "/chat/image/",
        tags=["chat"],
        summary="Proxy de imágenes del chat (S3 privado)",
    )
    async def get_chat_image(key: str):
        """Descarga la imagen de S3 y la sirve al cliente."""
        import urllib.parse
        decoded_key = urllib.parse.unquote(key)
        try:
            s3 = get_s3_client()
            response = s3.get_object(Bucket=S3_BUCKET, Key=decoded_key)
            content_type = response.get("ContentType", "image/jpeg")
            body = response["Body"]
            return StreamingResponse(body, media_type=content_type)
        except Exception as e:
            print(f"❌ Error obteniendo imagen de S3: {e}")
            raise HTTPException(status_code=404, detail="Imagen no encontrada")

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
        request: Request,
        token: str = Form(...),
        file: UploadFile = File(...),
    ):
        # Validar token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            current_user = UserRepository.get_user_by_username(username)
            if not current_user:
                raise HTTPException(status_code=401, detail="Usuario no encontrado")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Validar tipo de archivo
        content_type = file.content_type or ""
        if content_type and not content_type.startswith("image/") and content_type != "application/octet-stream":
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
            print(f"❌ Error subiendo a S3: {e}")
            raise HTTPException(status_code=500, detail=f"Error subiendo imagen: {str(e)}")

        # Guardar URL de S3 en la DB (URL interna, no pública)
        image_url_s3 = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"

        # Generar URL del proxy para el broadcast
        base_url = str(request.base_url).rstrip("/")
        proxy_url = get_proxy_url(base_url, image_url_s3)

        # Guardar mensaje con URL de S3
        msg = ChatMessageRepository.create(
            ChatMessageCreate(
                id_emergency=id_emergency,
                id_user=current_user.id_user,
                sender_name=current_user.full_name or current_user.username,
                sender_role=current_user.role if hasattr(current_user, "role") else "usuario",
                message="📷 Imagen",
                image_url=image_url_s3,
            )
        )

        # Broadcast con URL del proxy
        await chat_manager.broadcast(
            {
                "id_message": msg.id_message,
                "id_emergency": msg.id_emergency,
                "id_user": msg.id_user,
                "sender_name": msg.sender_name,
                "sender_role": msg.sender_role,
                "message": msg.message,
                "image_url": proxy_url,
                "timestamp": msg.timestamp.isoformat(),
            },
            id_emergency,
        )

        return {
            "ok": True,
            "image_url": proxy_url,
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