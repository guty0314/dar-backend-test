from sqlmodel import Session, select
from db.session import engine
from models.activity_log import ActivityLog


class ActivityLogRepository:

    @staticmethod
    def log(
        id_user: int,
        username: str,
        full_name: str | None,
        action: str,
        detail: str | None = None,
        ip_address: str | None = None,
    ):
        with Session(engine) as session:
            entry = ActivityLog(
                id_user=id_user,
                username=username,
                full_name=full_name,
                action=action,
                detail=detail,
                ip_address=ip_address,
            )
            session.add(entry)
            session.commit()

    @staticmethod
    def get_all(limit: int = 200):
        with Session(engine) as session:
            return session.exec(
                select(ActivityLog)
                .order_by(ActivityLog.timestamp.desc())
                .limit(limit)
            ).all()

    @staticmethod
    def get_by_user(id_user: int, limit: int = 100):
        with Session(engine) as session:
            return session.exec(
                select(ActivityLog)
                .where(ActivityLog.id_user == id_user)
                .order_by(ActivityLog.timestamp.desc())
                .limit(limit)
            ).all()