from sqlmodel import Session, select
from datetime import datetime, timezone

from db.session import engine
from models.account_request import AccountRequest


class AccountRequestRepository:
    """
    Clase que accede a la base de datos para trabajar informacion respecto a las solicitudes de cuenta
    """
    @staticmethod
    def create(request: AccountRequest) -> AccountRequest:
        with Session(engine) as session:
            session.add(request)
            session.commit()
            session.refresh(request)
            return request

    @staticmethod
    def get_by_id(id_request: int) -> AccountRequest | None:
        with Session(engine) as session:
            return session.get(AccountRequest, id_request)

    @staticmethod
    def get_all(status: str | None = None) -> list[AccountRequest]:
        with Session(engine) as session:
            query = select(AccountRequest)
            if status:
                query = query.where(AccountRequest.status == status)
            return session.exec(
                query.order_by(AccountRequest.created_at.desc())
            ).all()

    @staticmethod
    def get_pending_by_username(username: str) -> AccountRequest | None:
        with Session(engine) as session:
            return session.exec(
                select(AccountRequest).where(
                    AccountRequest.username == username,
                    AccountRequest.status == "pending",
                )
            ).first()

    @staticmethod
    def mark_approved(id_request: int, reviewer_username: str) -> AccountRequest | None:
        with Session(engine) as session:
            request = session.get(AccountRequest, id_request)
            if not request:
                return None

            request.status = "approved"
            request.reviewed_by = reviewer_username
            request.reviewed_at = datetime.now(timezone.utc)

            session.add(request)
            session.commit()
            session.refresh(request)
            return request

    @staticmethod
    def mark_rejected(id_request: int, reviewer_username: str, reason: str | None) -> AccountRequest | None:
        with Session(engine) as session:
            request = session.get(AccountRequest, id_request)
            if not request:
                return None

            request.status = "rejected"
            request.reviewed_by = reviewer_username
            request.reviewed_at = datetime.now(timezone.utc)
            request.rejection_reason = reason

            session.add(request)
            session.commit()
            session.refresh(request)
            return request
