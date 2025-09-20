import strawberry

from .shared import IDType

@strawberry.federation.type(keys=["id"], extend=True)
class UserGQLModel:
    id: IDType = strawberry.federation.field(external=True)