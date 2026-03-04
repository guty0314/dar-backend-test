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