from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated, List
from services.user import UpdateUserData
from services.email_service import send_user_credentials

def InitUserRoutes(app: FastAPI):
    from models.user import User
    from services.user import (
        get_current_active_user,
        admin_required,
        UserServices,
        NewUserData
    )
    from repositories.user_repository import UserRepository
    from services.password_reset import generate_reset_token, consume_reset_token
    from services.email_service import send_password_reset_token
    from pwdlib import PasswordHash

    # ================================
    # ACTUALIZAR POSICIÓN
    # ================================
    @app.put("/users/me/position/")
    async def update_my_position(
        latitude: float,
        longitude: float,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return UserServices.update_my_position(latitude, longitude, current_user)

    # ================================
    # REGISTRAR TOKEN DISPOSITIVO
    # ================================
    @app.put("/users/me/device_token/")
    async def register_device_token(
        device_token: str,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return UserServices.register_device_token(device_token, current_user)

    # ================================
    # OBTENER MI POSICIÓN
    # ================================
    @app.get("/users/me/position/")
    async def get_my_position(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        return UserServices.get_my_position(current_user)

    # ================================
    # CREAR USUARIO (ADMIN)
    # ================================
    @app.post("/users/", response_model=User)
    async def create_user(
        user: NewUserData,
        current_user: Annotated[User, Depends(admin_required)]
    ):
        return await UserServices.create_user(user, current_user)

    # ================================
    # LISTAR TODOS LOS USUARIOS (ADMIN)
    # ================================
    @app.get("/admin/users/")
    async def list_all_users(
        current_user: Annotated[User, Depends(admin_required)]
    ):
        users = UserRepository.get_all_users()

        return [
            {
                "id_user": u.id_user,
                "username": u.username,
                "full_name": u.full_name,
                "email": u.email,
                "number_phone": u.number_phone,
                "latitude": float(u.latitude) if u.latitude else None,
                "longitude": float(u.longitude) if u.longitude else None,
                "last_login": u.last_login,
                "last_position_update": u.last_position_update,
                "status": u.status,
                "role": u.role,
                "disabled": u.disabled,
                "cuil": u.cuil,
            }
            for u in users
        ]

    # ================================
    # CAMBIAR ROL (ADMIN)
    # ================================
    @app.put("/admin/users/{username}/role/")
    async def change_user_role(
        username: str,
        role: str,
        current_user: Annotated[User, Depends(admin_required)]
    ):
        return UserRepository.update_user_role(username, role)

    # ================================
    # DESACTIVAR USUARIO (ADMIN)
    # ================================
    @app.put("/admin/users/{username}/disable/")
    async def disable_user(
        username: str,
        current_user: Annotated[User, Depends(admin_required)]
    ):
        return UserRepository.disable_user(username)

    # ================================
    # ACTIVAR USUARIO (ADMIN)
    # ================================
    @app.put("/admin/users/{username}/enable/")
    async def enable_user(
        username: str,
        current_user: Annotated[User, Depends(admin_required)]
    ):
        return UserRepository.enable_user(username)

    # ================================
    # MODIFICAR USUARIO (ADMIN)
    # ================================
    @app.put("/admin/users/{username}/")
    async def update_user(
        username: str,
        data: UpdateUserData,
        current_user: Annotated[User, Depends(admin_required)]
    ):
        return UserRepository.update_user_data(username, data)

    # ================================
    # LOGOUT
    # ================================
    @app.get("/users/logout/")
    async def logout_user(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ):
        return UserServices.logout_user(current_user)

    # ================================
    # SOLICITAR RESET DE CONTRASEÑA
    # ================================
    @app.post("/users/password-reset/request/")
    async def request_password_reset(username: str):
        user = UserRepository.get_user_by_username(username)
        if not user or not user.email:
            return {"msg": "Si el usuario existe y tiene email, recibirá instrucciones."}
        token = generate_reset_token(user.username)
        try:
            await send_password_reset_token(user.email, user.username, token)
        except Exception as e:
            print("Error enviando email de reset:", e)
        return {"msg": "Si el usuario existe y tiene email, recibirá instrucciones."}

    # ================================
    # CONFIRMAR RESET DE CONTRASEÑA
    # ================================
    @app.post("/users/password-reset/confirm/")
    async def confirm_password_reset(token: str, new_password: str):
        username = consume_reset_token(token)
        if not username:
            raise HTTPException(status_code=400, detail="Token inválido o expirado")
        user = UserRepository.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if not new_password or len(new_password) < 8:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 8 caracteres")
        password_hash = PasswordHash.recommended()
        user.hashed_password = password_hash.hash(new_password)
        UserRepository.update_user(user)
        return {"msg": "Contraseña actualizada correctamente"}
    
    # ================================
    # VER MI USUARIO
    # ================================
    @app.get("/users/me")
    async def get_me(current_user: User = Depends(get_current_active_user)):
        return {
            "id": current_user.id_user,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "number_phone": current_user.number_phone,
            "cuil": current_user.cuil,
            "role": current_user.role,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        }
    # ================================
    # MIS EMERGENCIAS ENVIADAS
    # ================================
    @app.get("/users/me/emergencies-sent")
    async def get_my_emergencies_sent(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        from repositories.emergency_repository import EmergencyRepository

        emergencies = EmergencyRepository.get_emergencies_by_user(current_user.id_user)
        types = {t.id_type: t for t in EmergencyRepository.get_all_types()}
        categories = {c.id_category: c for c in EmergencyRepository.get_all_categories()}

        return [
            {
                "id": e.id_emergency,
                "latitude": float(e.latitude),
                "longitude": float(e.longitude),
                "date_created": e.date_created.isoformat(),
                "type_id": e.id_type,
                "type_name": types[e.id_type].name if e.id_type in types else None,
                "color": categories[types[e.id_type].id_category].color
                    if e.id_type in types and types[e.id_type].id_category in categories else None,
                "status": "activa" if e.active else "cerrada",
            }
            for e in emergencies
        ]

    # ================================
    # MIS EMERGENCIAS RESPONDIDAS
    # ================================
    @app.get("/users/me/emergencies-responded")
    async def get_my_emergencies_responded(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        from repositories.emergency_repository import EmergencyRepository

        results = EmergencyRepository.get_responses_with_emergency(current_user.id_user)
        types = {t.id_type: t for t in EmergencyRepository.get_all_types()}
        categories = {c.id_category: c for c in EmergencyRepository.get_all_categories()}

        return [
            {
                "id": e.id_emergency,
                "latitude": float(e.latitude),
                "longitude": float(e.longitude),
                "date_created": e.date_created.isoformat(),
                "type_id": e.id_type,
                "type_name": types[e.id_type].name if e.id_type in types else None,
                "color": categories[types[e.id_type].id_category].color
                    if e.id_type in types and types[e.id_type].id_category in categories else None,
                "status": r.status.value,
                "accepted_at": r.response_date.isoformat() if r.response_date else None,
                "arrived_at": r.arrival_time.isoformat() if r.arrival_time else None,
            }
            for e, r in results
        ]