import typing
from typing import Annotated
import uuid
import fastapi
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request, UploadFile, File, Form, HTTPException, Depends
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, bindparam
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

import logging

from ..DBDefinitions import (
    DocumentFragmentModel, 
    ComposeConnectionString, 
    startEngine
)

from pydantic import BaseModel, Field
from .chunk_embed import (
    EmbeddingService, 
    E5Provider, 
    AzureOpenAIEmbeddingProvider, 
    extract_text, 
    split_text_to_chunks_with_overlap
)


class DocumentCreate(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    url: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)

class DocumentUpdate(BaseModel):
    id: uuid.UUID
    title: typing.Optional[str] = Field(None, min_length=1, max_length=200)
    content: typing.Optional[str] = Field(None, min_length=1)

class DocumentDelete(BaseModel):
    id: uuid.UUID

class OperationResponse(BaseModel):
    status: str
    doc_id: uuid.UUID
    filename: typing.Optional[str] = None
    content_type: typing.Optional[str] = None
    size: typing.Optional[int] = None
    title: typing.Optional[str] = None


@asynccontextmanager
async def router_lifespan(router: APIRouter):
    client = httpx.AsyncClient(timeout=5)
    # uložím na app.state, aby byl dostupný v endpointu
    # (FastAPI sloučí stav routeru do app)
    connectionString = ComposeConnectionString()
    engine = await startEngine(connectionString, makeDrop=True, makeUp=True)
    # engine = await startEngine(connectionString)
    # router.app.state.sessionMaker = engine

    service_e5 = EmbeddingService(provider=E5Provider(
    ))
    service_az = EmbeddingService(provider=AzureOpenAIEmbeddingProvider(
    ))

    yield {
        "http_client": client,
        "embedding_service": service_e5,
        # "embedding_service": service_az,
        "session_maker": engine
    }
    await client.aclose()

def get_embedding_service(request: Request) -> EmbeddingService:
    app_state = request.state
    svc = getattr(app_state, "embedding_service", None)
    if svc is None:
        # lepší fail fast, když lifespan neběží
        logging.info(f"state keys: {list(app_state.__dict__.keys())}")
        s = getattr(app_state, "_state")
        logging.info(f"s: {type(s)}: {s}")
        raise HTTPException(500, "EmbeddingService not initialized")
    return typing.cast(EmbeddingService, svc)

def get_session_maker(request: Request) -> AsyncSession:
    session_maker = getattr(request.state, "session_maker", None)
    if session_maker is None:
        # lepší fail fast, když lifespan neběží
        raise HTTPException(500, "session_maker not initialized")
    return typing.cast(AsyncSession, session_maker)

def create_api_router(prefix="/api") -> fastapi.APIRouter:
    router = fastapi.APIRouter(
        prefix=f"{prefix}/documents",
        lifespan=router_lifespan
    )

    @router.get("/query")
    async def query(
        service: Annotated[EmbeddingService, Depends(get_embedding_service)],
        session_maker: Annotated[AsyncSession, Depends(get_session_maker)],
        query: str
    ):
        query_vector = await service.embed_one(query, is_query=True)
        qvec_list = query_vector.tolist()

        async with session_maker() as session:
            qparam = bindparam("qvec", value=qvec_list, type_=Vector(1536))
            # distance_expr = DocumentFragmentModel.embedding.op("<=>")(qparam)
            distance_expr = (
                DocumentFragmentModel.embedding.op("<=>")(qparam)
                .cast(DOUBLE_PRECISION)
                .label("distance")
            )
            stmt = (
                select(
                    DocumentFragmentModel.id,
                    DocumentFragmentModel.url,
                    DocumentFragmentModel.content,
                    distance_expr.label("distance"),
                )
                .order_by(distance_expr.desc())
                .limit(5)
            )

            result = await session.execute(stmt)
            # result = await session.execute(
            #     """
            #     SELECT id, url, content, embedding <=> :qvec AS distance
            #     FROM documents
            #     ORDER BY distance
            #     LIMIT 5
            #     """,
            #     {"qvec": query_vector.tolist()}
            # )
            rows = result.all()
            return [
                {
                    "id": r.id,
                    "url": r.url,
                    "content": r.content,
                    "distance": r.distance
                }
                for r in rows
            ]
        # return {"query": query, "result": f"Result for query '{query}'"}
    
    @router.post(
        "/create",
        # response_model=OperationResponse,
        summary="Nahraje dokument (soubor) s volitelným titulkem",
    )
    async def add_document(
        service: Annotated[EmbeddingService, Depends(get_embedding_service)],
        session_maker: Annotated[AsyncSession, Depends(get_session_maker)],
        file: UploadFile = File(..., description="Nahrávaný soubor (PDF, DOCX, PNG, …)"),
        title: str = Form(..., description="Titulek dokumentu"),
        url: str = Form(..., description="url dokumentu"),
    ) -> OperationResponse:
        logging.info((
            "working on"
            f"file.filename={file.filename}, file.content_type={file.content_type}"
        ))

        doc_id = uuid.uuid4()
        # path = _doc_path(doc_id, file.filename or "upload.bin")

        # Uložení na disk (streamově po částech, aby se nečetlo celé do paměti)
        # size = 0
        # with open(path, "wb") as out:
        #     while True:
        #         chunk = await file.read(1024 * 1024)
        #         if not chunk:
        #             break
        #         size += len(chunk)
        #         out.write(chunk)
        document_text = extract_text(file)
        logging.info((
            f"Extracted {len(document_text)} characters of text from uploaded document"
            "\n"
            f"file.filename={file.filename}, file.content_type={file.content_type}"
            "\n"
            f"{document_text[:200]}{'...' if len(document_text) > 200 else ''}"
        ))
        async with session_maker() as session:
            for index, chunk in enumerate(split_text_to_chunks_with_overlap(document_text, max_chunk_size=300, overlap=50)):
                text = " ".join(chunk)
                logging.info((
                    f"Extracted {len(text)} characters of text from uploaded document"
                    "\n"
                    f"{text[:200]}{'...' if len(text) > 200 else ''}"
                ))
                vec = await service.embed_one(text)
                fragment = DocumentFragmentModel(
                    id=uuid.uuid4(),
                    master_fragments_path=str(doc_id),
                    embedding=vec.tolist(),
                    url=url,
                    content=text,
                    location="",
                )
                session.add(fragment)
            await session.commit()

        return OperationResponse(
            status="document added",
            doc_id=doc_id,
            filename=file.filename,
            content_type=file.content_type,
            # size=size,
            title=title,
        )

    
    @router.post("/delete")
    async def delete_document(doc: dict):
        return {"status": "document deleted", "doc_id": doc.get("id")}
    
    @router.post("/update")
    async def update_document(doc: dict):
        return {"status": "document updated", "doc_id": doc.get("id"), "document": doc}
    
    return router