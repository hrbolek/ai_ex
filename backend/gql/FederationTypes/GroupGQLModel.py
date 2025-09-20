import strawberry

from .shared import IDType

@strawberry.federation.type(keys=["id"], extend=True)
class GroupGQLModel:
    id: IDType = strawberry.federation.field(external=True)
