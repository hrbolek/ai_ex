import strawberry

from .DocumentGQLModel import DocumentQuery
from .AISearchGQLModel import AISearchQuery
from .UserChannelGQLModel import UserChannelQuery
from .AIApiCallGQLModel import AIApiCallQuery

@strawberry.type(
    description="Query root type"
)
class Query(
    DocumentQuery, 
    AISearchQuery, 
    UserChannelQuery,
    AIApiCallQuery
):
    pass