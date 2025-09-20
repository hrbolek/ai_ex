import datetime
import typing
from sqlalchemy import ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .BaseModel import BaseModel, UUIDColumn, UUIDFKey, IDType

class ChatMessageModel(BaseModel):
    __tablename__ = "chat_messages"

    # timestamp: Mapped[datetime.datetime] = mapped_column(default=None, nullable=True, server_default=sqlalchemy.sql.func.now(), comment="date time of creation")

    conversation_id: Mapped[IDType] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        default=None,
        nullable=True,
        index=True
    )

    # role zprávy: 'user', 'assistant', případně 'agent'
    role: Mapped[str] = mapped_column(
        nullable=False, 
        default=None, 
        index=True
    )

    # vlastní obsah zprávy
    content: Mapped[str] = mapped_column(
        nullable=True, 
        default=None
    )

    # libovolná další metadata jako JSON
    metadata: Mapped[typing.Dict[str, typing.Any]] = mapped_column(
        JSON, 
        nullable=True,
        default_factory=lambda:dict
    )

    # pokud zpráva vznikla voláním skillu, uložíme jeho jméno sem
    skill_name: Mapped[str] = mapped_column(
        nullable=False, 
        default=None, 
        index=True,
        comment=""
    )

    # zda je tahle zpráva klíčová (summary, system directive apod.)
    important: Mapped[bool] = mapped_column(nullable=False, default=None, index=True, comment="summary, system directive etc.")

    conversation = relationship("Conversation", back_populates="messages")