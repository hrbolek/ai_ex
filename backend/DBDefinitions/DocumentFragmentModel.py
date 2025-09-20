import datetime
import typing
from sqlalchemy import ForeignKey, func, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from .BaseModel import BaseModel, UUIDColumn, UUIDFKey, IDType

class DocumentFragmentModel(BaseModel):
    __tablename__ = "document_fragments"

    master_fragments_path: Mapped[str] = mapped_column(
        nullable=True,
        default=None,
        index=True
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536), 
        nullable=True,
        default_factory=list
    )
    url: Mapped[str] = mapped_column(
        nullable=True,
        default=None,
        index=True
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        default=None,
        index=True
    )
    location: Mapped[str] = mapped_column(
        nullable=True,
        default=None,
        index=True
    )


# from sqlalchemy import (
#     create_engine, Column, Integer, Text, event, DDL
# )

# event.listen(
#     BaseModel.metadata,
#     "before_create",
#     DDL("CREATE EXTENSION IF NOT EXISTS vector")
# )


# with engine.begin() as conn:
#     conn.execute(
#         DDL("""
#         CREATE INDEX IF NOT EXISTS documents_embedding_idx
#         ON documents USING hnsw (embedding vector_l2_ops)
#         WITH (m = 16, ef_construction = 200)
#         """)
#     )

# session = Session()
# new_doc = Document(
#     content="Hello world",
#     embedding=[0.12, 0.05, /* … 1536 hodnot … */ 0.33]
# )
# session.add(new_doc)
# session.commit()