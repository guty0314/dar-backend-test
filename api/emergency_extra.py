from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated

def InitEmergencyExtraRoutes(app: FastAPI):

    from models.user import User
    from services.user import get_current_active_user

    # -----------------------------
    # TOMAR EMERGENCIA (OPERADOR)
    # -----------------------------
    @app.post("/emergencies/{emergency_id}/claim/", tags=["emergencias"])
    def claim_emergency(
        emergency_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        from repositories.emergency_repository import EmergencyRepository
        ok, reason = EmergencyRepository.claim_emergency(emergency_id, current_user.id_user)
        if not ok:
            if reason == "already_claimed":
                raise HTTPException(status_code=409, detail="La emergencia ya fue tomada por otro operador")
            raise HTTPException(status_code=404, detail="Emergencia no encontrada")
        return {"ok": True}

    # -----------------------------
    # LIBERAR EMERGENCIA (OPERADOR)
    # -----------------------------
    @app.post("/emergencies/{emergency_id}/release/", tags=["emergencias"])
    def release_emergency(
        emergency_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ):
        from repositories.emergency_repository import EmergencyRepository
        EmergencyRepository.release_emergency(emergency_id, current_user.id_user)
        return {"ok": True}

    # -----------------------------
    # TIPOS DE EMERGENCIA (ACCIDENTES DE TRANSITO, VIOLENCIA DE GENERO, ROBOS, HURTOS)
    # -----------------------------
    @app.get("/emergency/types", tags=["emergencias"])
    def get_emergency_types():
        from repositories.emergency_repository import EmergencyRepository

        types = EmergencyRepository.get_all_types()

        result = []
        for t in types:
            category = EmergencyRepository.get_category_by_id(t.id_category)

            result.append({
                "id_type": t.id_type,
                "name": t.name,
                "priority": t.priority,
                "category": category.name if category else None,
                "color": category.color if category else None,
            })

        return result


    # -----------------------------
    # RESPONDIENTES (QUIEN ACEPTO / QUIEN LLEGO REALMENTE)
    # -----------------------------
    @app.get("/emergencies/{emergency_id}/responses", tags=["emergencias"])
    def get_emergency_responses(emergency_id: int):
        from repositories.emergency_repository import EmergencyRepository
        from repositories.user_repository import UserRepository

        responses = EmergencyRepository.get_responses_by_emergency(emergency_id)

        result = []

        for r in responses:
            user = UserRepository.get_user_by_id(r.id_user)

            result.append({
                "username": user.username if user else None,
                "full_name": user.full_name if user else None,
                "accepted": r.accepted,
                "arrived": r.arrived,
                "status": r.status
            })

        return result


    # -----------------------------
    # DETALLE DE EMERGENCIA
    # -----------------------------
    @app.get("/emergencies/{emergency_id}", tags=["emergencias"])
    def get_emergency_detail(emergency_id: int):
        from repositories.emergency_repository import EmergencyRepository

        emergency = EmergencyRepository.get_emergency_by_id(emergency_id)

        if not emergency:
            return {"error": "No encontrada"}

        responses = EmergencyRepository.get_responses_by_emergency(emergency_id)

        accepted_count = len([r for r in responses if r.accepted])
        arrived_count = len([r for r in responses if r.arrived])
        type_obj = EmergencyRepository.get_type_by_id(emergency.id_type)
        category = EmergencyRepository.get_category_by_id(type_obj.id_category) if type_obj else None

        return {
            "id_emergency": emergency.id_emergency,
            "latitude": float(emergency.latitude),
            "longitude": float(emergency.longitude),

            "id_type": emergency.id_type,
            "type_name": type_obj.name if type_obj else None,

            "category": category.name if category else None,
            "color": category.color if category else None,

            "active": emergency.active,
            "date_created": str(emergency.date_created),

            "accepted_count": accepted_count,
            "arrived_count": arrived_count,
        }