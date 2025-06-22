import strawberry


from .DocumentGQLModel import DocumentMutations, DocumentFragmentMutations

@strawberry.type(
    description="Mutation root type"
)
class Mutation(
    DocumentMutations,
    DocumentFragmentMutations
):
    pass