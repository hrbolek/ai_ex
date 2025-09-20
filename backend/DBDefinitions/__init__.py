import sqlalchemy
import datetime


from .BaseModel import BaseModel
from .ChatMessageModel import ChatMessageModel
from .ConversationModel import ConversationModel

from sqlalchemy import (
    create_engine,
    event, 
    DDL
)
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


async def startEngine(connectionstring, makeDrop=False, makeUp=True):
    """Provede nezbytne ukony a vrati asynchronni SessionMaker"""
    asyncEngine = create_async_engine(connectionstring)

    event.listen(
        BaseModel.metadata,
        "before_create",
        DDL("CREATE EXTENSION IF NOT EXISTS vector")
    )

    async with asyncEngine.begin() as conn:
        # Specialne pro povoleni extension pgvector v postgresql

        if makeDrop:
            await conn.run_sync(BaseModel.metadata.drop_all)
            print("BaseModel.metadata.drop_all finished")

        if makeUp:
            await conn.run_sync(BaseModel.metadata.create_all)
            print("BaseModel.metadata.create_all finished")

        await conn.execute(DDL(
            "CREATE INDEX IF NOT EXISTS documents_embedding_idx"
            "ON documents USING hnsw (embedding vector_l2_ops)"
            "WITH (m = 16, ef_construction = 200)"
            )
        )

    async_sessionMaker = sessionmaker(
        asyncEngine, expire_on_commit=False, class_=AsyncSession
    )
    return async_sessionMaker


import os


def ComposeConnectionString():
    """Odvozuje connectionString z promennych prostredi (nebo z Docker Envs, coz je fakticky totez).
    Lze predelat na napr. konfiguracni file.
    """
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "example")
    database = os.environ.get("POSTGRES_DB", "data")
    hostWithPort = os.environ.get("POSTGRES_HOST", "localhost:5432")

    driver = "postgresql+asyncpg"  # "postgresql+psycopg2"
    connectionstring = f"{driver}://{user}:{password}@{hostWithPort}/{database}"
    connectionstring = os.environ.get("CONNECTION_STRING", connectionstring)

    return connectionstring
