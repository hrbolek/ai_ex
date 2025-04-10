import datetime
import os
from azure.data.tables import TableServiceClient, TableClient
import azure.functions as func

async def getUser_id(req: func.HttpRequest) -> str:
    """Extract user ID from the request headers."""
    user_id = req.headers.get('x-ms-client-principal-id')
    if not user_id:
        user_id = "ff3c3ce1-e0ff-4208-8c68-720dbf6ea4d4"
    return user_id

def getRequestsTableClient() -> TableClient:
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("Azure Storage connection string is not set in environment variables.")
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    return table_service_client.get_table_client(table_name="requests")

def getOrCreateQuotaEntity(user_id: str, table_client: TableClient):
    try:
        entity = table_client.get_entity(partition_key=user_id, row_key="requests")
    except Exception as e:
        if "ResourceNotFound" in str(e):
            entity = None
        else:
            raise
    if not entity:
        entity = {
            'PartitionKey': user_id,
            'RowKey': "requests",
            'RequestCount': 0,
            'LastUpdated': datetime.datetime.utcnow().isoformat()
        }
        table_client.create_entity(entity=entity)
    return entity

async def updateUserQuota(req: func.HttpRequest) -> bool:
    """Update user quota in the database."""
    user_id = await getUser_id(req)
    table_client = getRequestsTableClient()
    entity = getOrCreateQuotaEntity(user_id, table_client)
    requestCount = int(entity['RequestCount'])
    last_updated = datetime.datetime.fromisoformat(entity['LastUpdated'])
    now = datetime.datetime.utcnow()
    
    last_sunday = now - datetime.timedelta(days=now.weekday() + 1)
    if (last_sunday - last_updated).days >= 0:
        requestCount = 0
    entity['RequestCount'] = requestCount + 1
    entity['LastUpdated'] = datetime.datetime.utcnow().isoformat()
    table_client.update_entity(entity=entity)
    requestCount = int(entity['RequestCount'])
    quota = os.getenv("MAX_REQUESTS_PER_USER_PER_WEEK")
    return requestCount < int(quota)
