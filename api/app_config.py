from typing import Annotated
from fastapi import Depends, FastAPI

TUTORIAL_VIDEO_KEY = "tutorial_video_url"


def InitAppConfigRoutes(app: FastAPI):
    from models.user import User
    from services.user import admin_required, get_current_active_user
    from repositories.app_config_repository import AppConfigRepository

    # ================================
    # OBTENER URL DEL VIDEO TUTORIAL
    # ================================
    @app.get("/config/tutorial-video/", tags=["config"])
    async def get_tutorial_video(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        url = AppConfigRepository.get_value(TUTORIAL_VIDEO_KEY)
        return {"url": url}

    # ================================
    # ACTUALIZAR URL DEL VIDEO TUTORIAL (ADMIN)
    # ================================
    @app.put("/admin/config/tutorial-video/", tags=["admin"])
    async def set_tutorial_video(
        url: str,
        current_user: Annotated[User, Depends(admin_required)],
    ):
        AppConfigRepository.set_value(TUTORIAL_VIDEO_KEY, url)
        return {"msg": "URL actualizada correctamente"}
