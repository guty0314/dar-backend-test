from fastapi import Depends, FastAPI
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
    # PROBAR ENVIANDO EMAIL
    # ================================

    @app.post("/test-email")
    async def test_email():
        
        test_email = "tu_correo@gmail.com"

        print("📧 ENVIANDO CORREO DE PRUEBA")

        try:
            await send_user_credentials(
                test_email,
                "usuario_prueba",
                "ABC123"
            )
            return {"message": "Correo enviado correctamente"}
        
        except Exception as e:
            print("⚠️ Error enviando correo:", e)
            return {"error": str(e)}

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
    @app.get("/admin/users/", response_model=List[User])
    async def list_all_users(
        current_user: Annotated[User, Depends(admin_required)]
    ):
        return UserRepository.get_all_users()

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