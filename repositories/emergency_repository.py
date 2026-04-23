from sqlmodel import Session, select

from db.session import engine
from models.emergency import Emergency

class EmergencyRepository:

    @staticmethod
    def get_emergency_by_id(id_emergency: int) -> Emergency | None:
        with Session(engine) as session:
            return session.get(Emergency, id_emergency)
        
    @staticmethod
    def get_all_emergencies() -> list[Emergency]:
        with Session(engine) as session:
            return session.exec(select(Emergency)).all()
        
    @staticmethod
    def get_active_emergencies() -> list[Emergency]:
        with Session(engine) as session:
            return session.exec(select(Emergency).where(Emergency.active==True)).all()
        
    @staticmethod
    def get_first_active_emergency() -> Emergency | None:
        with Session(engine) as session:
            return session.exec(select(Emergency).where(Emergency.active==True)).first()
        
    @staticmethod
    def create_emergency(emergency: Emergency) -> Emergency:
        with Session(engine) as session:
            session.add(emergency)
            session.commit()
            session.refresh(emergency)
            return emergency

    @staticmethod
    def set_first_responder(emergency_id: int, user_id: int) -> Emergency | None:
        with Session(engine) as session:
            emergency = session.get(Emergency, emergency_id)
            if emergency is None or not emergency.active:
                return None
            if emergency.id_first_responder is None:
                emergency.id_first_responder = user_id
                session.add(emergency)
                session.commit()
                session.refresh(emergency)
            return emergency
        
    @staticmethod
    def get_all_types():
        from sqlmodel import Session, select
        from db.session import engine
        from models.emergency_type import EmergencyType

        with Session(engine) as session:
            return session.exec(select(EmergencyType)).all()
        
    @staticmethod
    def get_responses_by_emergency(id_emergency: int):
        from sqlmodel import Session, select
        from db.session import engine
        from models.emergency_response import EmergencyResponse

        with Session(engine) as session:
            return session.exec(
                select(EmergencyResponse)
                .where(EmergencyResponse.id_emergency == id_emergency)
            ).all()
        
    @staticmethod
    def get_all_categories():
        from models.emergency_category import EmergencyCategory
        with Session(engine) as session:
            return session.exec(select(EmergencyCategory)).all()
        
    @staticmethod
    def get_type_by_id(id_type: int):
        from models.emergency_type import EmergencyType
        with Session(engine) as session:
            return session.get(EmergencyType, id_type)

    @staticmethod
    def get_category_by_id(id_category: int):
        from models.emergency_category import EmergencyCategory
        with Session(engine) as session:
            return session.get(EmergencyCategory, id_category)
        
    @staticmethod
    def get_emergencies_by_user(user_id: int):
        with Session(engine) as session:
            return session.exec(
                select(Emergency)
                .where(Emergency.id_user == user_id)
                .order_by(Emergency.date_created.desc())
            ).all()
    
    @staticmethod
    def get_responses_by_user(user_id: int):
        from models.emergency_response import EmergencyResponse

        with Session(engine) as session:
            return session.exec(
                select(EmergencyResponse)
                .where(EmergencyResponse.id_user == user_id)
                .order_by(EmergencyResponse.response_date.desc())
            ).all()