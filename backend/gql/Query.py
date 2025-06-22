import strawberry

from .DocumentGQLModel import DocumentQuery
from .SearchGQLModel import SearchQuery
from .UserChannelGQLModel import UserChannelQuery

@strawberry.type(
    description="Query root type"
)
class Query(DocumentQuery, SearchQuery, UserChannelQuery):
    pass