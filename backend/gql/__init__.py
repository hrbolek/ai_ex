import strawberry


from .Query import Query
from .Mutation import Mutation
from .Subscription import Subscription

from strawberry.extensions import SchemaExtension

class EntraIdExtension(SchemaExtension):

    async def on_operation(self):
        # request: Request = self.execution_context.context["request"]
        yield
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
