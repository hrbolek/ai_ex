import strawberry


from .Query import Query
from .Mutation import Mutation
from .Subscription import Subscription

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
