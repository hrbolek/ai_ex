import strawberry


from .Query import Query
from .Mutation import Mutation
from .Subscription import Subscription

from strawberry.extensions import SchemaExtension
from uoishelpers.schema import WhoAmIExtension

class EntraIdExtension(SchemaExtension):

    async def on_operation(self):
        context = self.execution_context.context
        request = context["request"]
        yield
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[]
)

schema.extensions.append(WhoAmIExtension)