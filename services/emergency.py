from fastapi import BackgroundTasks, WebSocket, WebSocketDisconnect
#Define el tipo de emergencia por el color que tendran los botones

from services.emergencyring import Ring
from models.emergency import Emergency, EmergencyRequest
from models.user import User
class EmergencyServices:
    """
    Clase para alojar los servicios que se usan relacionados a las emergencias.
    """
    @staticmethod
    async def send_emergency(
        emergency_request: EmergencyRequest,
        current_user: User,
        background_tasks: BackgroundTasks,
    ):
        """
        Funcion que procesa una nueva emergencia.
        """
        from datetime import datetime

        from repositories.emergency_repository import EmergencyRepository
        from services.notifications import send_push_notifications

        # Guardar la emergencia en la DB
        emergency_record = EmergencyRepository.create_emergency(
            Emergency(
            latitude=emergency_request.latitude,
            longitude=emergency_request.longitude,
            type_emergency=emergency_request.emergency_color,
            active=True,
            date_created=datetime.now(),
            id_first_responder=current_user.id_user
            )
        )

        # Crear el anillo de seguridad alrededor de la emergencia
        emergency_ring = emergency_record.generate_emergency_ring()

        """--- NOTIFICACIONES 
            Después de crear la emergencia, recorre fake_users_db y recopila tokens de usuarios cuya posición cae dentro del anillo (zona 1 o 2).
            Construye payload con: ring_zone (1 o 2), reporter_username, reporter_full_name,
            reporter_latitude, reporter_longitude, emergency_id, emergency_color
            Llama a send_push_notifications(tokens, title, body, data) para enviarlas
            La respuesta del endpoint incluye resumen notified y push_send_result con conteos ok/fail
        ---"""
       
        # Notificar a usuarios cuyos device_token esten definidos y que se encuentren en los anillos
        try:
            from repositories.user_repository import UserRepository

            tokens = []
            notified = []
            users_list = UserRepository.get_all_users()

            for u in users_list:
                # No avisar si el usuario no esta online
                if u.online is False:
                    continue
                token = u.device_token
                if not token:
                    continue
                # Determinar si el usuario está en alguno de los anillos
                user_lat = u.latitude
                user_lon = u.longitude
                zone = emergency_ring.contains(user_lat, user_lon)
                if zone == 0:
                    continue
                # Preparar payload y título
                title = f"Emergencia: {emergency_request.emergency_color.value}"
                body = (
                    f"{current_user.full_name or current_user.username} reportó una emergencia. "
                    f"Estás en zona {'CRÍTICA (Primer Anillo )' if zone==1 else 'DE ALERTA (Segundo Anillo)'}"
                )
                data = {
                    "emergency_id": emergency_record.id_emergency,
                    "ring_zone": str(zone),
                    "reporter_username": current_user.username,
                    "reporter_full_name": current_user.full_name or "",
                    "reporter_latitude": str(emergency_request.latitude),
                    "reporter_longitude": str(emergency_request.longitude),
                    "emergency_color": emergency_request.emergency_color.value,
                }
                tokens.append(token)
                notified.append({"username": u.username, "zone": zone})

            # Enviar notificaciones (FCM o log) EN SEGUNDO PLANO
            if tokens:
                # Programar envío asíncrono para no bloquear el endpoint
                background_tasks.add_task(send_push_notifications, tokens, title, body, data)
                send_result = {"scheduled": len(tokens)}
            else:
                send_result = {"scheduled": 0}
        except Exception as e:
            # Para que un fallo en notificaciones no rompa la API
            send_result = {"ok": 0, "fail": 0,  "error": str(e)}
            print("Notification error:", e)

        return {
            "emergency_id": emergency_record.id_emergency,
            "message": f"Emergencia registrada con color: {emergency_request.emergency_color.value}",
            "user": current_user.username,
            "latitude": emergency_request.latitude,
            "longitude": emergency_request.longitude,
            # Descomentar la siguiente linea y comentar la segunda cuando haya conexion a Firebase
            #"notified": notified if 'notified' in locals() else [],
            "notified": emergency_record.get_emergency_users_data(),
            "push_send_result": send_result,
        }
    
    @staticmethod
    async def cancel_emergency(
        emergency_id: int,
        current_user: User,
    ):
        """
        Cancela una emergencia activa.
        """
        from repositories.emergency_repository import EmergencyRepository

        emergency = EmergencyRepository.get_emergency_by_id(emergency_id)

        if emergency is None:
            return {"message": "Emergencia no encontrada."}
        elif not emergency.active:
            return {"message": "La emergencia ya está cancelada."}
        elif emergency.id_first_responder != current_user.id_user:
            return {"message": "No tienes permiso para cancelar esta emergencia."}
        emergency.disable_emergency()
        return {"message": f"Emergencia {emergency_id} cancelada por {current_user.username}."}
    
    @staticmethod
    async def check_emergency(
        websocket: WebSocket,
    ):
        """
        WebSocket para que el cliente consulte si hay emergencias activas.
        """
        import asyncio
        import jwt
        from jwt.exceptions import InvalidTokenError
        from services.utils import SECRET_KEY, ALGORITHM
        
        from repositories.emergency_repository import EmergencyRepository
        from repositories.user_repository import UserRepository

        await websocket.accept()
        
        # Recibir el json
        data = await websocket.receive_json()
        
        # Recibir el token como primer mensaje
        token = data.get("token", "")
        # Recibir el ID de la emergencia a chequear
        emergency_id = data.get("emergency_id", 0)
        
        # Verificar el token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                await websocket.close(code=1008, reason="Invalid token")
                return
            
            current_user = UserRepository.get_user_by_username(username)

            if current_user is None:
                await websocket.close(code=1008, reason="User not found")
                return
                
        except InvalidTokenError:
            await websocket.close(code=1008, reason="Invalid token")
            return
        except Exception as e:
            print(f"WebSocket authentication error: {e}")
            await websocket.close(code=1008, reason="Authentication error")
            return

        try:
            while True:
                try:
                    found = False
                    emergency_list = EmergencyRepository.get_all_emergencies()
                    for emergency in emergency_list:

                        if emergency.id_emergency == emergency_id:
                            if emergency.id_first_responder != current_user.id_user:
                                await websocket.close(code=1008, reason="No permission for this emergency")
                                return
                            
                            if emergency.active:
                                users_data = emergency.get_emergency_users_data()
                                await websocket.send_json({
                                    "users_data": users_data,
                                    "status": 1
                                })
                                await asyncio.sleep(10)  # Esperar antes de la siguiente verificación
                                found = True
                                break   # Salir del for para reiniciar el while
                            else:
                                await websocket.send_json({
                                    "users_data": {},
                                    "status": 0,
                                })
                                await websocket.close(3001, reason="Emergency cancelled")
                                return  # Finalizar el WebSocket ya que la emergencia fue cancelada
                    if not found:
                        await websocket.close(code=3000, reason="Emergency not found")
                        return  # Finalizar el bucle significa que la emergencia no fue encontrada
                
                except WebSocketDisconnect:
                    print(f"WebSocket disconnected for user: {current_user.username}")
                    break  # Salir del bucle si el cliente se desconectó

        except Exception as e:
            await websocket.close(code=1008, reason=f"Server error: {e}")
            return

    @staticmethod
    async def notice_if_im_on_alert(
        websocket: WebSocket
    ):
        """
        Notifica si el usuario actual está en una zona de emergencia activa.
        """
        import asyncio
        # Aquí se debería verificar contra la base de datos de emergencias activas.
        import jwt
        from jwt.exceptions import InvalidTokenError
        from services.utils import SECRET_KEY, ALGORITHM
        from repositories.emergency_repository import EmergencyRepository
        from repositories.user_repository import UserRepository
        from services.user import UserServices

        await websocket.accept()
        
        # Recibir el token como primer mensaje
        token = await websocket.receive_text()
        
        # Verificar el token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                await websocket.close(code=1008, reason="Invalid token")
                return
            
            current_user = UserRepository.get_user_by_username(username)

            if current_user is None:
                await websocket.close(code=1008, reason="User not found")
                return
            
            # Verificar si el usuario está activo
            if current_user.disabled:
                await websocket.close(code=1008, reason="Inactive user")
                return
                
        except InvalidTokenError:
            await websocket.close(code=1008, reason="Invalid token")
            return
        except Exception as e:
            print(f"WebSocket authentication error: {e}")
            await websocket.close(code=1008, reason="Authentication error")
            return

        try:
            while True:
                # HACK: Obtiene la ubicacion del usuario actual pero esto debe ser optimizado
                current_user = UserRepository.get_user_by_username(username)

                try:
                    current_user_lat = current_user.latitude
                    current_user_lon = current_user.longitude

                    # JSON a enviar
                    data = {}
                    
                    # Solo obtiene una de las emergencias activas (la primera que encuentre)
                    emergency = EmergencyRepository.get_first_active_emergency()

                    if emergency is not None:
                        users_data = emergency.get_emergency_users_data()
                        
                        user_ring_result = emergency.generate_emergency_ring().contains(current_user_lat, current_user_lon)
                        if user_ring_result in [1, 2]:
                            data = {
                                "my_zone": user_ring_result, 
                                "emergency_id": emergency.id_emergency,
                                "emergency_color": emergency.type_emergency.value,
                                "users_in_ring": users_data
                            }

                    
                    await websocket.send_json(data)
                    await asyncio.sleep(3)  # Esperar antes de la siguiente verificación

                except WebSocketDisconnect:
                    print(f"WebSocket disconnected for user: {current_user.username}")
                    break  # Salir del bucle si el cliente se desconectó

        except Exception as e:
            await websocket.close(code=1008, reason=f"Server error: {e}")
            return
    
