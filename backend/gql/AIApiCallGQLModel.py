import asyncio
import typing
import strawberry

from .SubscriptionChannels import get_user_channels, get_channel_queue
from .AIMessageGQLModel import AIMessageGQLModel
from .shared import IDType, get_user_from_info

@strawberry.input(
    description="input for the search"
)
class AIApiCallInputGQLModel:
    query: str = strawberry.field(
        description="text of the query"
    )
    id: IDType = strawberry.field(
        description="channel id"
    )


from SemanticKernel import openChat
from builtins import anext

streams = {}
@strawberry.interface(
    description=""
)
class AIApiCallQuery:


    @strawberry.field(description="")
    async def api_query_by_text(self, info: strawberry.types.Info, api_call: AIApiCallInputGQLModel) -> None:
        user = get_user_from_info(info=info)
        user_id = user["id"]
        queue: asyncio.Queue = get_channel_queue(user_id=user_id, channel_id="ba05ce5d-5bbe-4847-bc44-d4b4b2c94771")
        
        stream = streams.get(api_call.id, None)
        if stream is None:
            stream = await openChat()
            # firstresponse = await stream.asend(None)
            streams[api_call.id] = stream

            await queue.put(
                AIMessageGQLModel(msg=f"startujeme chat", attachments=[])
            )

        # text = await anext(stream)
        # text = await stream.asend(api_call.query)
        text = await stream(api_call.query)
        print(f"{api_call.query} -> {text}")
        await queue.put(
            AIMessageGQLModel(msg=f"{text}", attachments=[])
        )

        pass


    # @strawberry.field(description="")
    # async def api_query_by_text(
    #     self,
    #     info: strawberry.types.Info,
    #     api_call: AIApiCallInputGQLModel
    # ) -> typing.List[typing.Optional[AIMessageGQLModel]]:
    #     # yield AIMessageGQLModel(msg="Ahoj", attachments=[])
    #     # yield AIMessageGQLModel(msg="Ahoj1", attachments=[])
    #     # yield AIMessageGQLModel(msg="Ahoj2", attachments=[])
    #     # yield AIMessageGQLModel(msg="Ahoj3", attachments=[])
    #     return (AIMessageGQLModel(msg=f"Ahoj {i}", attachments=[]) for i in range(10))
