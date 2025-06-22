import uuid
import strawberry
import strawberry.types

IDType = uuid.UUID

user_id = "9fec7130-cb9f-464c-abb8-f727938e1246"
def get_user_from_info(info: strawberry.types.Info):
    return {
        "id": user_id
    }