import typing
import asyncio
import strawberry

import urllib.parse

from .shared import IDType, get_user_from_info
from .SubscriptionChannels import get_user_channels, get_channel_queue
from .DocumentGQLModel import DocumentFragmentGQLModel, DocumentGQLModel
from .MessageGQLModel import MessageGQLModel

from .AzureResolvers import searchdocumenthandler_, sumarize_

@strawberry.type(
    description="result of search by natural language"
)
class SearchGQLModel:
    
    document_fragments: typing.List[DocumentFragmentGQLModel] = strawberry.field(
        description="fragments retrieved during search"
    )

    @strawberry.field(
        description="get all related document, makes an aggregation"
    )
    async def documents() -> typing.List[DocumentGQLModel]:
        pass
    pass


@strawberry.input(
    description="input for the search"
)
class SearchInputGQLModel:
    query: str = strawberry.field(
        description="text of the query"
    )

@strawberry.interface(
    description=""
)
class SearchQuery:
    @classmethod
    def search(cls, query: str):
        pass

    @strawberry.field(
        description="query the index and return summary"
    )
    async def search_by_text(self, info: strawberry.types.Info, search: SearchInputGQLModel) -> typing.Optional[SearchGQLModel]:
        user = get_user_from_info(info=info)
        user_id = user["id"]
        # channels = get_user_channels(user_id=user_id, )
        queue: asyncio.Queue = get_channel_queue(user_id=user_id, channel_id="ba05ce5d-5bbe-4847-bc44-d4b4b2c94771")
        await queue.put(
            MessageGQLModel(msg=f"Připravuji odpověď na '{search.query}'. Podívám se do dokumentů", attachments=[])
        )
        docs_found = await asyncio.to_thread(searchdocumenthandler_, query=search.query)
        urls = {doc["document_folder"] for doc in docs_found}
        print(f"urls {urls}")
        documents = [DocumentGQLModel(url=url) for url in urls]
            #     docs.append({
            # "id":              r.get("id"),
            # "content":         r.get("content", ""),
            # "document_folder": r.get("document_folder"),
            # "score":           r.get("@search.score"),

        # await asyncio.sleep(1)
        # eoln = "\n"
        # md_message = f"""### Nalezené soubory{eoln}{eoln}- {eoln+'- '.join(urls)}"""
        md_message = """### Nalezené dokumenty\n\n"""
        for url in urls:
            fname = urllib.parse.unquote(url.split("/")[-1])
            md_link = f"[{fname}]({url})"
            md_message += f"- {md_link}" + "\n"

        await queue.put(
            MessageGQLModel(msg=md_message, attachments=[doc for doc in documents])
        )

        #         payload = {
        #     "query":    query,
        #     "summary":  summary,
        #     "documents": docs
        # }

        summary_result = await asyncio.to_thread(sumarize_, query=search.query, docs=docs_found)
        print(f"sumary_result\n{summary_result}")
        await queue.put(
            MessageGQLModel(msg=summary_result["summary"], attachments=[])
        )

        return None
