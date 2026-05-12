"""
repositories/chat_message_repository.py

Patrón: métodos estáticos con Session propia, igual que EmergencyRepository.
"""

from typing import List
from sqlmodel import Session, select
from db.session import engine
from models.chat_message import ChatMessage, ChatMessageCreate


class ChatMessageRepository:

    @staticmethod
    def create(data: ChatMessageCreate) -> ChatMessage:
        with Session(engine) as session:
            msg = ChatMessage.model_validate(data)
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg

    @staticmethod
    def get_by_emergency(id_emergency: int) -> List[ChatMessage]:
        with Session(engine) as session:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.id_emergency == id_emergency)
                .order_by(ChatMessage.timestamp.asc())
            )
            return session.exec(stmt).all()

    @staticmethod
    def get_by_id(id_message: int) -> ChatMessage | None:
        with Session(engine) as session:
            return session.get(ChatMessage, id_message)