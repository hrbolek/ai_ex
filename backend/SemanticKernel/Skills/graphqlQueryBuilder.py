from typing import List, Tuple, Dict, Annotated
from collections import deque
from graphql import parse, build_ast_schema
from graphql.language.ast import (
    TypeNode,
    DocumentNode,
    NamedTypeNode, 
    NonNullTypeNode, 
    ListTypeNode,
    ObjectTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    UnionTypeDefinitionNode
)
import json
from pathlib import Path


# Utility imports from utils_sdl_2 (support both relative and absolute imports)
try:
    from Skills.utils_sdl_2 import (
        build_medium_fragment, 
        get_read_vector_values, 
        select_ast_by_path, 
        get_read_scalar_values,
        build_large_fragment
    )
except ImportError:
    from SemanticKernel.Skills.utils_sdl_2 import (
    # from .utils_sdl_2 import (
        build_medium_fragment, 
        get_read_vector_values, 
        select_ast_by_path, 
        get_read_scalar_values,
        build_large_fragment
    )

# 1️⃣ Define the GraphQLQueryBuilder class
class GraphQLQueryBuilder:
    def __init__(self, sdlfilename: str = None, disabled_fields: list[str]=[]):
        _path = Path(__file__).parent
        sdl_path =  _path / ("../sdl.graphql" if sdlfilename is None else _path)
        sdl_path = sdl_path.resolve()
        with open(sdl_path, "r", encoding="utf-8") as f:
            sdl_lines = f.readlines()
        sdl = "\n".join(sdl_lines)

        self.ast = parse(sdl)
        self.schema = build_ast_schema(self.ast)
        self.adjacency = self._build_adjacency(self.ast, disabled_fields)

    def _unwrap_type(self, t):
        # Unwrap AST type nodes (NonNull, List) to get NamedTypeNode
        while isinstance(t, (NonNullTypeNode, ListTypeNode)):
            t = t.type
        if isinstance(t, NamedTypeNode):
            return t.name.value
        raise TypeError(f"Unexpected type node: {t}")

    def _build_adjacency(self, ast, disabled_fields: list[str]) -> Dict[str, List[Tuple[str, str]]]:
        edges: Dict[str, List[Tuple[str, str]]] = {}
        for defn in ast.definitions:
            if hasattr(defn, 'fields'):
                from_type = defn.name.value
                for field in defn.fields:
                    if field.name.value in disabled_fields:
                        continue
                    to_type = self._unwrap_type(field.type)
                    edges.setdefault(from_type, []).append((field.name.value, to_type))
        return edges

    def _find_path(self, source: str, target: str) -> List[Tuple[str, str]]:
        queue = deque([(source, [])])
        visited = {source}
        while queue:
            current, path = queue.popleft()
            for field, nxt in self.adjacency.get(current, []):
                if nxt == target:
                    return path + [(field, nxt)]
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [(field, nxt)]))
        return []

    def build_query_vector(self, types: List[str]) -> str:
        print(f"building query vector for types {types}")
        root = types[0]
        rootfragment = build_large_fragment(self.ast, root)
        page_operations = get_read_vector_values(self.ast)
        page_operation = page_operations[root][0]
        # print(f"page_operation {page_operation}")

        field = select_ast_by_path(self.ast, ["Query", page_operation])
        
        args = [(f"${arg.name.value}: {arg.type.name.value}" + ("!" if isinstance(arg.type, NonNullTypeNode) else "")) for arg in field.arguments]
        args_str = ", ".join(args)
        args2 = [(f"{arg.name.value}: ${arg.name.value}") for arg in field.arguments]
        args2_str = ", ".join(args2)
        args3 = [
                (
                    f"# ${arg.name.value}: {arg.type.name.value}" + 
                    ("!" if isinstance(arg.type, NonNullTypeNode) else "") + 
                    f" # {arg.description.value}"
                ) 
                for arg in field.arguments
            ]
        args3_str = "\n".join(args3)
        args3_str += "\n\n# to get more results, adjust parameters $skip and / or $limit and call the query until the result is empty vector\n"
        # print(f"args: {args}")

        # print(f"field: {field}, {field.name.value}")
        # Generate fragment definitions for each type
        fragments = [
            build_medium_fragment(self.ast, t)
            for t in types
        ]
        # Precompute full paths from root to each target
        full_paths = {t: self._find_path(root, t) for t in types[1:]}

        def build_spread(current: str, remaining_path: List[Tuple[str, str]]) -> str:
            # If no more path, insert fragment spread
            if not remaining_path:
                return f"...{current}MediumFragment"
            field, next_type = remaining_path[0]
            sub = build_spread(next_type, remaining_path[1:])
            return f"{field} {{ {sub} }}"

        # Build selection sets for each target and combine
        selections = [
            build_spread(root, path)
            for path in full_paths.values()
        ]
        selections.append(rootfragment)

        unique_selections = list(dict.fromkeys(selections))
        selection_str = " ".join(unique_selections)
        query = f"query {page_operation}({args_str})\n{args3_str}\n{{\n   {page_operation}({args2_str})\n   {{\n    ...{root}MediumFragment\n ...{root}LargeFragment\n    {selection_str} \n   }} \n}}"
        # Append fragments after the main query
        fragments_str = "\n\n".join(fragments)
        result = f"{query}\n\n{fragments_str}"
        print(f"vector query \n{result}")
        return result
    
    def build_query_scalar(self, types: List[str]) -> str:
        print(f"building query scalar for types {types}")
        root = types[0]
        rootfragment = build_large_fragment(self.ast, root)
        page_operations = get_read_scalar_values(self.ast)
        page_operation = page_operations[root][0]
        # print(f"page_operation {page_operation}")

        field = select_ast_by_path(self.ast, ["Query", page_operation])
        args = [(f"${arg.name.value}: {arg.type.name.value}" + ("!" if isinstance(arg.type, NonNullTypeNode) else "")) for arg in field.arguments]
        args_str = ", ".join(args)
        args2 = [(f"{arg.name.value}: ${arg.name.value}") for arg in field.arguments]
        args2_str = ", ".join(args2)
        # print(f"args: {args}")

        # print(f"field: {field}, {field.name.value}")
        # Generate fragment definitions for each type
        fragments = [
            build_medium_fragment(self.ast, t)
            for t in types
        ]
        fragments.append(rootfragment)
        # Precompute full paths from root to each target
        full_paths = {t: self._find_path(root, t) for t in types[1:]}

        def build_spread(current: str, remaining_path: List[Tuple[str, str]]) -> str:
            # If no more path, insert fragment spread
            if not remaining_path:
                return f"...{current}MediumFragment"
            field, next_type = remaining_path[0]
            sub = build_spread(next_type, remaining_path[1:])
            return f"{field} {{ {sub} }}"

        # Build selection sets for each target and combine
        selections = [
            build_spread(root, path)
            for path in full_paths.values()
        ]
        unique_selections = list(dict.fromkeys(selections))
        selection_str = " ".join(unique_selections)
        query = f"query {page_operation}({args_str})\n{{\n   {page_operation}({args2_str})\n   {{\n    ...{root}MediumFragment\n    ...{root}LargeFragment\n    {selection_str} \n   }} \n}}"
        # Append fragments after the main query
        fragments_str = "\n\n".join(fragments)
        return f"{query}\n\n{fragments_str}"    

from semantic_kernel.functions import kernel_function
from semantic_kernel.functions import KernelArguments

class GraphQLBuilderPlugin:
    @kernel_function(
        name="buildVectorQuery",
        # description="Automaticaly generated skill for acces to graphql endpoint from sdl for Query.programPage."
    )
    # 2️⃣ Define the native skill function
    def graphql_vetor_query_builder_skill(
        self, 
        graphql_types: Annotated[List[str], "List of GraphQL output type names, e.g. ['ProgramGQLModel','StudentGQLModel']"],
        arguments: KernelArguments = None
    ) -> str:
        """
        Build a GraphQL query to fetch multiple entities (vector) based on the supplied types.

        Args:
          graphql_types: ordered list of type names, where the first element is the root field
          arguments.sdl_doc: AST of the GraphQL SDL (DocumentNode)
        
        Returns:
          A nested GraphQL query string selecting each type in turn.
        """
        # types = json.loads(graphgql_types) 
        # types = payload["types"]
        # sdl = payload["sdl"]
        print(f"graphql_vetor_query_builder_skill(graphgql_types={graphql_types})")
        builder = GraphQLQueryBuilder(disabled_fields=["createdby", "changedby"])
        return builder.build_query_vector(graphql_types)
    

    @kernel_function(
        name="buildScalarQuery",
        # description="Automaticaly generated skill for acces to graphql endpoint from sdl for Query.programPage."
    )
    # 2️⃣ Define the native skill function
    def graphql_scalar_query_builder_skill(
        self, 
        graphql_types: Annotated[List[str], "List of GraphQL output type names, where last type is the scalar identifier"],
        arguments: KernelArguments = None
    ) -> str:
        """
        Build a GraphQL query to fetch a single entity by its ID.

        Args:
          graphql_types: ordered list of type names, e.g. ['ProgramGQLModel','StudentGQLModel']
        
        Returns:
          A GraphQL query string with an `$id` variable for fetching one entity.
        """
        # types = json.loads(graphgql_types)
        # types = payload["types"]
        # sdl = payload["sdl"]
        print(f"graphql_scalar_query_builder_skill(graphgql_types={graphql_types})")
        builder = GraphQLQueryBuilder(disabled_fields=["createdby", "changedby"])
        return builder.build_query_scalar(graphql_types)
    

def main():
    # sestav mi dotaz GroupGQLModel a UserGQLModel
    _path = Path(__file__).parent
    sdl_path =  _path / "../sdl.graphql"
    sdl_path = sdl_path.resolve()
    with open(sdl_path, "r", encoding="utf-8") as f:
        sdl_lines = f.readlines()
    sdl = "\n".join(sdl_lines)

    ast = parse(sdl)


    fragment = build_medium_fragment(ast, "UserGQLModel")
    print("UserGQLModel")
    print(fragment)
    # pass

    graphqltypes = ["GroupGQLModel", "UserGQLModel"]
    graphqltypes = ["FacilityGQLModel", "EventGQLModel"]
    # graphqltypes = ["GroupGQLModel", "MembershipGQLModel", "EventGQLModel"]
    builder = GraphQLQueryBuilder(disabled_fields=["createdby", "changedby"])
    query = builder.build_query_vector(graphqltypes)
    print(query)

if __name__ == "__main__":
    main()