"""
models/chat_message.py
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ChatMessageBase(SQLModel):
    id_emergency: int = Field(nullable=False)
    id_user: Optional[int] = Field(default=None, nullable=True)
    sender_name: str = Field(nullable=False)
    sender_role: str = Field(nullable=False)
    message: str = Field(nullable=False)
    image_url: Optional[str] = Field(default=None, nullable=True)


class ChatMessage(ChatMessageBase, table=True):
    __tablename__ = "chat_message"
    __table_args__ = {"schema": "dar"}

    id_message: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"server_default": "now()"},
    )


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageRead(ChatMessageBase):
    id_message: int
    timestamp: datetime

    class Config:
        from_attributes = True