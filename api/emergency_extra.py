from fastapi import FastAPI

def InitEmergencyExtraRoutes(app: FastAPI):

    # -----------------------------
    # TIPOS DE EMERGENCIA
    # -----------------------------
    @app.get("/emergency/types")
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
    # RESPONSES (QUIEN ACEPTÓ / LLEGÓ)
    # -----------------------------
    @app.get("/emergencies/{emergency_id}/responses")
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
    @app.get("/emergencies/{emergency_id}")
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