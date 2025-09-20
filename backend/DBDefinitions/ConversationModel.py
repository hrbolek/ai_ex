import datetime
import typing
from sqlalchemy import ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .BaseModel import BaseModel, UUIDColumn, UUIDFKey, IDType

class ConversationModel(BaseModel):
    __tablename__ = "conversations"

    user_id: Mapped[IDType] = UUIDFKey(ForeignKey("users.id"), nullable=True, default=None, index=True)

    messages = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.timestamp"
    )