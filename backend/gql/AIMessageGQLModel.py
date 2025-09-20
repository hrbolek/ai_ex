import typing
import strawberry


from .DocumentGQLModel import DocumentGQLModel, DocumentFragmentGQLModel

AISearchGQLModel = typing.Annotated["AISearchGQLModel", strawberry.lazy(".AISearchGQLModel")]

AttachmentGQLModel = typing.Union[
    DocumentGQLModel,
    DocumentFragmentGQLModel,
    AISearchGQLModel
]

@strawberry.type(
    description="One message"
)
class AIMessageGQLModel:

    msg: str = strawberry.field(
        description="the text part of message"
    )

    attachments: typing.List[AttachmentGQLModel] = strawberry.field(
        description="attachments to this message"
    )