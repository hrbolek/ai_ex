import strawberry
import typing

import strawberry.types

from .shared import get_user_from_info
from .SubscriptionChannels import get_channel_queue
from .MessageGQLModel import MessageGQLModel
@strawberry.type
class Subscription:
    # @strawberry.subscription
    # async def user_channel_messages(
    #     self, info,
    #     user_id: str,
    #     channel: str
    # ) -> typing.AsyncGenerator[str, None]:
    #     queue = get_channel_queue(user_id, channel)
    #     while True:
    #         msg = await queue.get()
    #         yield msg


    @strawberry.subscription(
        description="messages set to the user on dedicated channel"
    )
    async def user_channel_messages(
        self, info: strawberry.types.Info,
        channel: str
    ) -> typing.AsyncGenerator[typing.Optional[MessageGQLModel], None]:
        user = get_user_from_info(info)
        user_id = user["id"]
        queue = get_channel_queue(user_id, channel)
        while True:
            print(f"waiting for a msg ({user_id}.{channel})")
            msg = await queue.get()
            print(f"have msg {msg}")
            yield msg