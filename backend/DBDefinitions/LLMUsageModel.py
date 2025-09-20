import datetime
import typing
from sqlalchemy import ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .BaseModel import BaseModel, UUIDColumn, UUIDFKey, IDType

class ConversationModel(BaseModel):
    __tablename__ = "llm_usage"

    user_id: Mapped[IDType] = UUIDFKey(ForeignKey("users.id"), nullable=True, default=None, index=True)

    tokens: Mapped[int] = mapped_column(nullable=True, default=0)
