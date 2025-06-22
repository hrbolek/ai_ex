import typing
import strawberry


from .shared import IDType, get_user_from_info
from .SubscriptionChannels import get_user_channels

# from .
@strawberry.type(
    description=""
)
class UserChannelGQLModel:
    id: IDType = strawberry.field(
        description="id of the channel"
    )


@strawberry.interface(
    description="base queries"
)
class UserChannelQuery:
    @strawberry.field(
        description="returns channels associated with the user"
    )
    async def my_channels(self, info: strawberry.types.Info) -> typing.List[UserChannelGQLModel]:
        user_id = get_user_from_info(info)
        channel_queues = get_user_channels(user_id)
        result = (UserChannelGQLModel(id=channel_id) for channel_id in channel_queues.keys())
        return result