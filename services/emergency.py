from fastapi import BackgroundTasks, WebSocket, WebSocketDisconnect
from services.emergencyring import Ring
from models.emergency import Emergency, EmergencyRequest
from models.user import User
from models.emergency_response import EmergencyResponse
from datetime import datetime, timezone, timedelta


class EmergencyServices:

    # -----------------------------
    # CREAR EMERGENCIA
    # -----------------------------
    @staticmethod
    async def send_emergency(
        emergency_request: EmergencyRequest,
        current_user: User,
        background_tasks: BackgroundTasks,
    ):
        from repositories.emergency_repository import EmergencyRepository
        from services.notifications import send_push_notifications
        from repositories.user_repository import UserRepository

        # id_type en lugar de color
        emergency_record = EmergencyRepository.create_emergency(
            Emergency(
                latitude=emergency_request.latitude,
                longitude=emergency_request.longitude,
                id_type=emergency_request.id_type,
                active=True,
                date_created=datetime.now(timezone.utc),
                id_user=current_user.id_user,
            )
        )

        emergency_ring = emergency_record.generate_emergency_ring()

        try:
            tokens = []
            users_list = UserRepository.get_all_users()

            for u in users_list:
                if u.status == "offline" or not u.device_token:
                    continue
                #Evitar usuarios sin ubicacion
                if u.latitude is None or u.longitude is None:
                    continue
                zone = emergency_ring.contains(u.latitude, u.longitude)
                if zone == 0:
                    continue

                tokens.append(u.device_token)

            if tokens:
                background_tasks.add_task(
                    send_push_notifications,
                    tokens,
                    "Nueva emergencia",
                    f"{current_user.full_name or current_user.username} reportó una emergencia",
                    {
                        "emergency_id": emergency_record.id_emergency,
                        "id_type": emergency_request.id_type,
                    }
                )

                send_result = {"scheduled": len(tokens)}
            else:
                send_result = {"scheduled": 0}

        except Exception as e:
            send_result = {"error": str(e)}
            print("Notification error:", e)

        return {
            "emergency_id": emergency_record.id_emergency,
            "message": "Emergencia registrada correctamente",
            "user": current_user.username,
            "latitude": emergency_request.latitude,
            "longitude": emergency_request.longitude,
            "push_send_result": send_result,
        }

    # -----------------------------
    # CANCELAR EMERGENCIA
    # -----------------------------
    @staticmethod
    async def cancel_emergency(
        emergency_id: int,
        current_user: User,
    ):
        from repositories.emergency_repository import EmergencyRepository

        emergency = EmergencyRepository.get_emergency_by_id(emergency_id)

        if emergency is None:
            return {"message": "Emergencia no encontrada."}

        if not emergency.active:
            return {"message": "La emergencia ya está cancelada."}

        # solo el creador cancela
        if emergency.id_user != current_user.id_user:
            return {"message": "No tienes permiso para cancelar esta emergencia."}

        emergency.disable_emergency()

        return {
            "message": f"Emergencia {emergency_id} cancelada por {current_user.username}."
        }

    # -----------------------------
    # ACEPTAR EMERGENCIA
    # -----------------------------
    @staticmethod
    async def accept_emergency(
        emergency_id: int,
        current_user: User,
    ):
        from sqlmodel import Session, select
        from db.session import engine
        from repositories.emergency_repository import EmergencyRepository

        #Aesegura de quien reporto la emergencia no pueda aceptarla 
        Emergency = EmergencyRepository.get_emergency_by_id(emergency_id)
        if Emergency is None:
            return {"ok": False, "message": "Emergencia no encontrada"}
        if Emergency.id_user == current_user.id_user:
            return{"ok": False, "message": "No podes aceptar tu propia emergencia"}
        
        with Session(engine) as session:
            response = session.exec(
                select(EmergencyResponse).where(
                    EmergencyResponse.id_emergency == emergency_id,
                    EmergencyResponse.id_user == current_user.id_user
                )
            ).first()

            # evitar doble aceptación
            if response and response.accepted:
                return {
                    "ok": False,
                    "message": "Ya aceptaste esta emergencia"
                }

            if response:
                response.accepted = True
                response.status = "accepted"
            else:
                response = EmergencyResponse(
                    id_emergency=emergency_id,
                    id_user=current_user.id_user,
                    accepted=True,
                    arrived=False,
                    status="accepted"
                )
                session.add(response)

            session.commit()

        return {
            "ok": True,
            "message": f"{current_user.username} aceptó la emergencia {emergency_id}.",
        }

    # -----------------------------
    # MARCAR LLEGADA
    # -----------------------------
    @staticmethod
    async def arrive_emergency(emergency_id: int, current_user: User):
        from sqlmodel import Session, select
        from db.session import engine
        from repositories.emergency_repository import EmergencyRepository

        emergency = EmergencyRepository.get_emergency_by_id(emergency_id)

        if not emergency:
            return {"ok": False, "message": "Emergencia no encontrada"}

        if not emergency.active:
            return {"ok": False, "message": "La emergencia ya no está activa"}

        if current_user.latitude is None or current_user.longitude is None:
            return {"ok": False, "message": "No se pudo obtener tu ubicación"}

        ring = emergency.generate_emergency_ring()

        distance = ring.calculate_distance(
            float(current_user.latitude),
            float(current_user.longitude)
        )

        MAX_DISTANCE_METERS = 50

        if distance > MAX_DISTANCE_METERS:
            return {
                "ok": False,
                "message": f"Estás demasiado lejos ({int(distance)}m).",
                "distance_meters": int(distance)
            }

        with Session(engine) as session:
            response = session.exec(
                select(EmergencyResponse).where(
                    EmergencyResponse.id_emergency == emergency_id,
                    EmergencyResponse.id_user == current_user.id_user
                )
            ).first()

            if not response:
                return {"ok": False, "message": "Primero debés aceptar"}

            if not response.accepted:
                return {"ok": False, "message": "Debés aceptar primero"}

            if response.arrived:
                return {"ok": False, "message": "Ya marcaste llegada"}

            response.arrived = True
            response.status = "arrived"
            response.arrival_time = datetime.now(timezone.utc)

            session.commit()

        return {
            "ok": True,
            "message": f"Llegada confirmada a {int(distance)}m",
            "distance_meters": int(distance)
        }
    # -----------------------------
    # USUARIOS CERCANOS
    # -----------------------------
    @staticmethod
    async def get_nearby_users(current_user: User):
        from repositories.user_repository import UserRepository

        if current_user.latitude is None or current_user.longitude is None:
            return {"ok": False, "message": "No se pudo obtener tu ubicación"}

        ring = Ring(
            latitude=float(current_user.latitude),
            longitude=float(current_user.longitude),
            inner_radius_m=500,
            outer_radius_m=1000
        )

        users_list = UserRepository.get_all_users()
        result = []

        for u in users_list:
            if u.status == "offline":
                continue

            if u.id_user == current_user.id_user:
                continue

            if u.latitude is None or u.longitude is None:
                continue

            distance = ring.calculate_distance(
                float(u.latitude),
                float(u.longitude)
            )

            zone = ring.contains(
                float(u.latitude),
                float(u.longitude)
            )

            if zone == 0:
                continue

            result.append({
                "id_user": u.id_user,
                "username": u.username,
                "full_name": u.full_name,
                "latitude": float(u.latitude),
                "longitude": float(u.longitude),
                "zone": zone,
                "distance_meters": int(distance)
            })

        result.sort(key=lambda x: x["distance_meters"])

        return {
            "ok": True,
            "count": len(result),
            "nearby_users": result
        }
    # -----------------------------
    # WEBSOCKET CONTROL EMERGENCIA
    # -----------------------------
    @staticmethod
    async def check_emergency(
        websocket: WebSocket,
    ):
        import asyncio
        import jwt
        from jwt.exceptions import InvalidTokenError
        from services.utils import SECRET_KEY, ALGORITHM
        from repositories.emergency_repository import EmergencyRepository
        from repositories.user_repository import UserRepository

        await websocket.accept()
        data = await websocket.receive_json()
        token = data.get("token", "")
        emergency_id = data.get("emergency_id", 0)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")

            current_user = UserRepository.get_user_by_username(username)

            if not current_user:
                await websocket.close(code=1008, reason="User not found")
                return

        except InvalidTokenError:
            await websocket.close(code=1008, reason="Invalid token")
            return

        try:
            while True:
                emergency = EmergencyRepository.get_emergency_by_id(emergency_id)

                if not emergency:
                    await websocket.close(code=3000, reason="Emergency not found")
                    return

                if not emergency.active:
                    await websocket.close(code=3001, reason="Emergency cancelled")
                    return

                users_data = emergency.get_emergency_users_data()

                await websocket.send_json({
                    "users_data": users_data,
                    "status": 1
                })

                await asyncio.sleep(10)

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user: {current_user.username}")

    # -----------------------------
    # WEBSOCKET ALERTA GENERAL
    # -----------------------------
    @staticmethod
    async def notice_if_im_on_alert(
        websocket: WebSocket
    ):
        import asyncio
        import jwt
        from jwt.exceptions import InvalidTokenError
        from services.utils import SECRET_KEY, ALGORITHM
        from repositories.emergency_repository import EmergencyRepository
        from repositories.user_repository import UserRepository

        await websocket.accept()
        token = await websocket.receive_text()

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")

            current_user = UserRepository.get_user_by_username(username)

            if not current_user:
                await websocket.close(code=1008, reason="User not found")
                return

        except InvalidTokenError:
            await websocket.close(code=1008, reason="Invalid token")
            return

        try:
            while True:
                current_user = UserRepository.get_user_by_username(username)

                emergency = EmergencyRepository.get_first_active_emergency()

                data = {}

                if emergency:
                    now = datetime.now(timezone.utc)
                    emergency_time = emergency.date_created

                    if emergency_time.tzinfo is None:
                        emergency_time = emergency_time.replace(tzinfo=timezone.utc)

                    if now - emergency_time > timedelta(minutes=10):
                        emergency.disable_emergency()
                        await websocket.send_json({})
                        await asyncio.sleep(3)
                        continue

                    zone = emergency.generate_emergency_ring().contains(
                        current_user.latitude,
                        current_user.longitude
                    )

                    if zone in [1, 2]:
                        data = {
                            "my_zone": zone,
                            "emergency_id": emergency.id_emergency,
                            "id_type": emergency.id_type,
                            "users_in_ring": emergency.get_emergency_users_data()
                        }

                await websocket.send_json(data)

                try:
                    msg = await asyncio.wait_for(
                        websocket.receive_text(), timeout=3.0
                    )
                    if msg == "ping":
                        await websocket.send_text("pong")
                except asyncio.TimeoutError:
                    pass

        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user: {current_user.username}")