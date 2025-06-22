import uuid
import asyncio
import typing
import strawberry
import strawberry.file_uploads
import strawberry.types

from .shared import IDType

from .AzureResolvers import (
    search_documents, 
    delete_documents_by_filter, 
    delete_document_fragment,
    update_document_folder_by_id_prefix
)

@strawberry.type(description="single fragment of the document created by chunking")
class DocumentFragmentGQLModel:
    id: typing.Optional[str] = strawberry.field(
        description="unique id for the document fragment",
        default=None
    )
    content: typing.Optional[str] = strawberry.field(
        description="part of document",
        default=None
    )
    vector: typing.Optional[typing.List[float]] = strawberry.field(
        description="embeding of the fragment",
        default_factory=list
    )
    location_start: typing.Optional[str] = strawberry.field(
        description="where this fragment begins in the document",
        default=None
    )
    location_end: typing.Optional[str] = strawberry.field(
        description="where this fragment ends in the document",
        default=None
    )
    url: typing.Optional[str] = strawberry.field(
        description="url where the document is available",
        default=None
    )
    pass

@strawberry.type(description="whole document in the index")
class DocumentGQLModel:
    url: typing.Optional[str] = strawberry.field(
        description="url where the document is available",
        default=None
    )
    # fragments: typing.List[DocumentFragmentGQLModel] = strawberry.field(
    #     description="list of fragments created by chunking"
    # )

    @strawberry.field(description="list of fragments created by chunking")
    async def fragments(self, info: strawberry.types.info) -> typing.List[DocumentFragmentGQLModel]:
        pass

    def fragments_sync(self):
        pass

    @classmethod
    def get_fragments_sync(cls, url):
        pass

@strawberry.input(
    description="Filter for documents"
)
class DocumentWhereFilter:
    url: typing.Optional[str] = strawberry.field(
        description="url where the document is located"
    )

@strawberry.input(
    description="Filter for document fragments"
)
class DocumentFragmentWhereFilter:
    url: typing.Optional[str] = strawberry.field(
        description="url where the document is located"
    )

@strawberry.interface(
    description=""
)
class DocumentQuery:
    @strawberry.field(
        description=""
    )
    async def document_page(
        self, 
        info: strawberry.types.Info, 
        skip: typing.Optional[int] = 0, 
        limit: typing.Optional[int] = 10, 
        where: typing.Optional[DocumentWhereFilter] = None
    ) -> typing.List[DocumentGQLModel]:
        filter = None
        if where:
            val = where.url.replace("'", "''")
            filter = f"document_folder eq '{val}'"
        results = await asyncio.to_thread(search_documents, filter_str=filter, skip=skip, limit=limit)
        urls = {result["document_folder"] for result in results}
        
        docs = [DocumentGQLModel(url=url) for url in urls]
        return docs

    @strawberry.field(
        description=""
    )
    async def document_fragment_page(
        self,
        info: strawberry.types.Info, 
        skip: typing.Optional[int] = 0, 
        limit: typing.Optional[int] = 10, 
        where: typing.Optional[DocumentFragmentWhereFilter] = None
    ) -> typing.List[DocumentFragmentGQLModel]:
        filter = None
        if where:
            val = where.url.replace("'", "''")
            filter = f"document_folder eq '{val}'"
        results = await asyncio.to_thread(search_documents, filter_str=filter, skip=skip, limit=limit)
        
        fragments = [DocumentFragmentGQLModel(id=result["id"], url=result["document_folder"]) for result in results]
        return fragments        

@strawberry.input(description="defines data needed for insert a new document into index")
class DocumentInsertGQLModel:
    url: str = strawberry.field(
        description="url which is associated with the document, also the document should be available at this url"
    )
    document: strawberry.file_uploads.Upload = strawberry.field(
        description="the document which should be indexed"
    )
    created_by: strawberry.Private[IDType] = None

@strawberry.input(description="defines data needed for update of existing document in index")
class DocumentUpdateGQLModel:
    url: str = strawberry.field(
        description="url which is associated with the document, also the document should be available at this url"
    )
    document: strawberry.file_uploads.Upload = strawberry.field(
        description="the document which should be indexed"
    )
    updated_by: strawberry.Private[IDType] = None

@strawberry.input(description="defines data needed for delete of existing document in index")
class DocumentDeleteGQLModel:
    url: str = strawberry.field(
        description="url which is associated with the document, also the document should be available at this url"
    )

@strawberry.interface(description="mutations for the documents")
class DocumentMutations:
    @classmethod
    def index_document(url: str, file: strawberry.file_uploads.Upload):
        pass

    @classmethod
    def update_document(url: str, file: strawberry.file_uploads.Upload):
        pass

    @classmethod
    def delete_document(url: str, file: strawberry.file_uploads.Upload):
        pass

    @strawberry.mutation(
        description="inserts a document"
    )
    async def document_insert(
        self, 
        info: strawberry.types.Info, 
        document: DocumentInsertGQLModel,
        file: strawberry.file_uploads.Upload
    )-> typing.Optional[DocumentGQLModel]:
        cls = type(self)
        print(document.url)
        print(document.document)
        print(type(document.document))
        print(type(file))
        print(dir(file))
        # print(dir(document.document))
        # result = asyncio.to_thread(cls.document_insert, url=document.url, document=document.document)
        result = DocumentGQLModel(
            url=document.url,
            # document=document.document
        )
        return None
        pass

    @strawberry.mutation(
        description="update the document"
    )
    async def document_update(self, info: strawberry.types.Info, document: DocumentUpdateGQLModel)-> DocumentGQLModel:
        cls = type(self)
        result = await asyncio.to_thread(cls.update_document, url=document.url, document=document.document)
        
        pass

    @strawberry.mutation(
        description="delete the document"
    )
    async def document_delete(self, info: strawberry.types.Info, document: DocumentDeleteGQLModel)-> int:
        filter = f"document_folder eq '{document.url}'"
        result = await asyncio.to_thread(delete_documents_by_filter, filter_str=filter)
        return result


    @strawberry.mutation(
        description="upgrade of ..."
    )
    async def documents_upgrade(self) -> str:
        remap = {
            "17_1_aaaaa": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Statut%20UO%20ve%20zn%C4%9Bn%C3%AD%201.%20a%C5%BE%204.%20zm%C4%9Bny.pdf",
            "17_1_b_01_06_2023": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Volebn%C3%AD%20%C5%99%C3%A1d%20AS%20UO%20ve%20zn%C4%9Bn%C3%AD%201.%20zm%C4%9Bny.pdf",
            "17_1_ggg": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/SZ%C5%98%20UO_ve%20zn%C4%9Bn%C3%AD%201.%20a%202.%20zm%C4%9Bny.pdf",
            "17_1_h_uplne_zneni_po_2_zmene-1": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Stipendijn%C3%AD%20%C5%99%C3%A1d%20ve%20zn%C4%9Bn%C3%AD%201.%20a%202.%20zm%C4%9Bny.pdf",
            "17_1_ff": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/%C5%98V%C5%982025.pdf",
            "17_1_k4": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/%C5%98%C3%A1d%20habilita%C4%8Dn%C3%ADho%20%C5%99%C3%ADzen%C3%AD%20a%20%C5%99%C3%ADzen%C3%AD%20ke%20jmenov%C3%A1n%C3%AD%20profesorem%20na%20Univerzit%C4%9B%20obrany%20v%20Brn%C4%9B.pdf",
            "17_1_k3": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/%C5%98%C3%A1d%20celo%C5%BEivotn%C3%ADho%20vzd%C4%9Bl%C3%A1v%C3%A1n%C3%AD%20UO%20v%20Brn%C4%9B.pdf",
            "17_1-j": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Pravidla%20kvality_Novela%202023.pdf",
            "17_1_e": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Jednac%C3%AD%20%C5%99%C3%A1d%20V%C4%9Bdeck%C3%A9%20rady%20Univerzity%20obrany%20v%20Brn%C4%9B.pdf",
            "17_1_k1": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Jednac%C3%AD%20%C5%99%C3%A1d%20Rady%20pro%20vnit%C5%99n%C3%AD%20hodnocen%C3%AD%20Univerzity%20obrany%20v%20Brn%C4%9B.pdf",
            "17_1_c_01_09_2023": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Jednac%C3%AD%20%C5%99%C3%A1d%20Akademick%C3%A9ho%20sen%C3%A1tu%20Univerzity%20obrany%20v%20Brn%C4%9B.pdf",
            "17_1_i": "https://lib.unob.cz/UNOB_CZ/UNOB/DOKUMENTY/VNITRNI-PREDPISY/Disciplin%C3%A1rn%C3%AD%20%C5%99%C3%A1d%20pro%20studenty%20Univerzity%20obrany%20v%20Brn%C4%9B.pdf"
        }
        total_result = 0
        for id_prefix, new_folder in remap.items():
            result = await asyncio.to_thread(update_document_folder_by_id_prefix, id_prefix=id_prefix, new_folder=new_folder)
            total_result += result
        return f"OK ({total_result})"


@strawberry.input(description="defines data needed for delete of existing document in index")
class DocumentFragmentDeleteGQLModel:
    id: str = strawberry.field(
        description="unique"
    )

@strawberry.interface(description="mutations for the documents")
class DocumentFragmentMutations:
    @strawberry.mutation(
        description="delete the document fragment"
    )
    async def document_fragment_delete(self, info: strawberry.types.Info, document: DocumentFragmentDeleteGQLModel)-> bool:
        result = await asyncio.to_thread(delete_document_fragment, document_id=document.id)
        return result
