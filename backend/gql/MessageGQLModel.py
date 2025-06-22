import typing
import strawberry


from .DocumentGQLModel import DocumentGQLModel, DocumentFragmentGQLModel

SearchGQLModel = typing.Annotated["SearchGQLModel", strawberry.lazy(".SearchGQLModel")]

AttachmentGQLModel = typing.Union[
    DocumentGQLModel,
    DocumentFragmentGQLModel,
    SearchGQLModel
]

@strawberry.type(
    description="One message"
)
class MessageGQLModel:

    msg: str = strawberry.field(
        description="the text part of message"
    )

    attachments: typing.List[AttachmentGQLModel] = strawberry.field(
        description="attachments to this message"
    )