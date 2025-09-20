from typing import List, Tuple, Dict, Annotated
import json

from semantic_kernel.functions import kernel_function
from semantic_kernel.functions import KernelArguments

class GraphQLRunQueryPlugin:
    @kernel_function(
        name="runQueryPage",
        # description="Automaticaly generated skill for acces to graphql endpoint from sdl for Query.programPage."
    )
    # 2️⃣ Define the native skill function
    async def run_graphql_query_for_page(
        self, 
        graphql_query: Annotated[str, "The full GraphQL query string, including pagination variables"],
        skip: Annotated[int, "Number of items to skip"] = 0,
        limit: Annotated[int, "Maximum number of items to return"] = 10,
        arguments: KernelArguments = None
    ) -> str:
        """
        Runs a GraphQL query against the API, applying `skip` and `limit` for paging.

        Args:
          graphql_query: valid GraphQL query string
          skip: number of records to skip (offset)
          limit: maximum number of records to return

        Returns:
          The list of entities under the `data` key in the GraphQL response.
          If the number of returned items is equal to limit, there are another items beyond limit.
        """
        # types = json.loads(graphgql_types)
        # types = payload["types"]
        # sdl = payload["sdl"]
        print(f"run_graphql_query_for_page skip: {skip}, limit: {limit}")
        variables = {
            "skip": skip, "limit": limit
        }
        
        # extra_context = arguments["extra_context"]
        gqlclient = arguments["gqlclient"]
        rows = await gqlclient(query=graphql_query, variables=variables)
        # rows = await response.json()

        assert "data" in rows, f"the response does not contain the data key {rows}"
        data = rows["data"]
        _, entities = next(iter(data.items()))
        # print(f"have got entity: \n{json.dumps(entity, indent=4)}")
        # assert "__typename" in entity, f"the response does not contain the data key {rows}"
        

        return entities
    
    @kernel_function(
        name="runQuerySingle",
        # description="Execute a GraphQL query to fetch a single entity by ID"
    )
    async def run_graphql_query_for_single_entity(
        self,
        graphql_query: Annotated[str, "The full GraphQL query string with an `$id` variable"],
        id: Annotated[str, "Primary key (UUID) of the requested entity"],
        arguments: KernelArguments = None
    ) -> str:
        """
        Runs a GraphQL query to fetch exactly one entity, passing `id` as a variable.

        Args:
          graphql_query: valid GraphQL query string (must accept `$id`)
          id: the entity's primary key

        Returns:
          The single entity object under the `data` key in the GraphQL response.
        """
        # types = json.loads(graphgql_types)
        # types = payload["types"]
        # sdl = payload["sdl"]
        print(f"run_graphql_query_for_single_entity id: {id}")
        variables = {
            "id": id
        }
        
        # extra_context = arguments["extra_context"]
        gqlclient = arguments["gqlclient"]
        rows = await gqlclient(query=graphql_query, variables=variables)
        # rows = await response.json()

        assert "data" in rows, f"the response does not contain the data key {rows}"
        data = rows["data"]
        _, entity = next(iter(data.items()))
        # print(f"have got entity: \n{json.dumps(entity, indent=4)}")
        # assert "__typename" in entity, f"the response does not contain the data key {rows}"
        
        return entity
    
