import asyncio
from pathlib import Path

from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.contents.chat_history import ChatHistory

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

import strawberry.types
from dotenv import load_dotenv
env_path = Path(__file__).parent / "../../local.env.txt"
env_path = env_path.resolve()
load_dotenv(dotenv_path=env_path)


here = Path(__file__).parent.resolve()
skills_dir = here / "Skills"
# skill_files = [f for f in skills_dir.glob("*.py") if f.name != "__init__.py"]

# import importlib.util
# import sys
# def import_module_from_file(module_path):
#     name = module_path.stem
#     spec = importlib.util.spec_from_file_location(name, str(module_path))
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)
#     return module

# skill_modules = []
# for file in skills_dir.glob("*.py"):
#     if not file.name.startswith("_"):
#         mod = import_module_from_file(file)
#         skill_modules.append(mod)

# plugins = {}
# for file in skills_dir.glob("*.py"):
#     if not file.name.startswith("_"):
#         mod = import_module_from_file(file)
#         func = getattr(mod, file.stem, None)
#         if func:
#             plugins[file.stem] = func 
# # 1. Init Semantic Kernel
# from semantic_kernel import Kernel

# kernel = Kernel(plugins=plugins)

from semantic_kernel.functions import KernelPlugin
from semantic_kernel import Kernel
from semantic_kernel.exceptions import PluginInitializationError
from pathlib import Path

skills_dir = Path(__file__).parent / "Skills"
plugins = {}

# Pro každý .py soubor načti plugin
for skill_path in skills_dir.glob("*.py"):
    if skill_path.name.startswith("_"):
        continue
    plugin_name = skill_path.stem  # např. studentPage
    try:
        plugin = KernelPlugin.from_python_file(plugin_name, str(skill_path))
        plugins[plugin_name] = plugin
    except PluginInitializationError as e:
        pass


import os
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
account = os.getenv("AZURE_COGNITIVE_ACCOUNT_NAME", "")
model_name = os.getenv("AZURE_CHAT_DEPLOYMENT_NAME", "") or "summarization-deployment"
endpoint = f"https://{account}.openai.azure.com"

from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
azure_chat = AzureChatCompletion(
    service_id="azure-gpt4",
    api_key=OPENAI_API_KEY,
    endpoint=endpoint,
    deployment_name=model_name,
    # api_version="2024-02-15-preview"  # nebo verze, co máš v Azure portálu
    api_version="2024-02-01"
)


AZURE_ORCHESTRATION_DEPLOYMENT_NAME=os.getenv("AZURE_ORCHESTRATION_DEPLOYMENT_NAME")
azure_orchestrator = AzureChatCompletion(
    service_id="azure-orchestrator",
    api_key=OPENAI_API_KEY,
    endpoint=endpoint,
    deployment_name=AZURE_ORCHESTRATION_DEPLOYMENT_NAME,
    # api_version="2024-02-15-preview"  # nebo verze, co máš v Azure portálu
    # api_version="2025-04-14"
)



from semantic_kernel import Kernel
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt

kernel = Kernel()

# ... předpokládejme, že jste přidali chat_service již dříve ...

# # 1) Vytvoříme ChatPromptTemplate s in‐line promptem
# template = """
# You are a JSON generator for ProgramInputFilter objects.
# Valid fields (all optional):
# • id: { "_eq": "<UUID>", "_in": ["<UUID1>", ...] }
# • name: { "_eq": "<string>", "_in": ["<str1>", ...], "_like": "<substring>" }
# • _and, _or: Lists of nested ProgramInputFilter.

# Examples:
# - "Chci programy s id 1234":
#   { "id": { "_eq": "1234" } }
# - "Only programs whose name contains "app" or "service":
#   { "_or": [ { "name": { "_like": "%app%" } }, { "name": { "_like": "%service%" } } ] }
# - "All" → {}

# Now, given the user query, output **only** the JSON object for ProgramInputFilter.
# User Query: {{$user_input}}
# Result:
# """

# pt_cfg = PromptTemplateConfig(
#     template=template,
#     template_format="semantic-kernel",
#     input_variables=["user_input"]
# )

# # 2) Zaregistrujeme ji jako semantickou funkci
# filter_fn = kernel.add_function(
#     plugin_name="FilterSkill",
#     function=None,                    # None → prompt‐function, not native code
#     function_name="BuildFilter",
#     description="Turn free‐text into a ProgramInputFilter JSON",
#     prompt=None,
#     prompt_template_config=pt_cfg,    # inject our inline Jinja prompt
#     # prompt_execution_settings=exec_settings,
#     template_format="semantic-kernel"
# )  # :contentReference[oaicite:0]{index=0}



# Kernel s načtenými pluginy
kernel = Kernel(
    services=[
        # azure_orchestrator,
        azure_chat,
    ],
    plugins=plugins,
    # ai_service_selector=
    )
from semantic_kernel.processes.kernel_process import KernelProcessStep, KernelProcessStepContext
# from semantic_kernel.functions import KernelPlugin
# from semantic_kernel import Kernel
# from pathlib import Path

# skills_dir = Path(__file__).parent
# plugin = KernelPlugin.from_directory("Skills", str(skills_dir))

# kernel = Kernel(plugins={"MyPlugin": plugin})

# kernel.import_skill(my_skill_module, "my_skill")


# import uuid
# import strawberry


# @strawberry.input()
# class StreamInputGQlModel:
#     id: uuid.UUID

# @strawberry.subscription
# async def BasicChatStream(self, info: strawberry.types.Info, stream: StreamInputGQlModel):
#     pass

async def createGQLClient(*, url: str = "http://localhost:33001/api/gql", username: str, password: str):
    import aiohttp
    async def getToken():
        authurl = url.replace("/api/gql", "/oauth/login3")
        async with aiohttp.ClientSession() as session:
            # print(headers, cookies)
            async with session.get(authurl) as resp:
                json = await resp.json()

            payload = {
                **json,
                "username": username,
                "password": password
            }
            async with session.post(authurl, json=payload) as resp:
                json = await resp.json()
            # print(f"createGQLClient: {json}")
            token = json["token"]
        return token
    token = await getToken()
    total_attempts = 10
    async def client(query, variables, cookies={"authorization": token}):
        # gqlurl = "http://host.docker.internal:33001/api/gql"
        # gqlurl = "http://localhost:33001/api/gql"
        nonlocal total_attempts
        if total_attempts < 1:
            raise Exception(msg="Max attempts to reauthenticate to graphql endpoint has been reached")
        attempts = 2
        while attempts > 0:
            
            payload = {"query": query, "variables": variables}
            # print("Query payload", payload, flush=True)
            try:
                async with aiohttp.ClientSession() as session:
                    # print(headers, cookies)
                    async with session.post(url, json=payload, cookies=cookies) as resp:
                        # print(resp.status)
                        if resp.status != 200:
                            text = await resp.text()
                            # print(text, flush=True)
                            raise Exception(f"Unexpected GQL response", text)
                        else:
                            text = await resp.text()
                            # print(text, flush=True)
                            response = await resp.json()
                            # print(response, flush=True)
                            return response
            except aiohttp.ContentTypeError as e:
                attempts = attempts - 1
                total_attempts = total_attempts - 1
                print(f"attempts {attempts}-{total_attempts}", flush=True)
                nonlocal token
                token = await getToken()

    return client

async def BasicChaStreamImplementation(context: dict):
    inQueue: asyncio.Queue = context["inQueue"]
    outQueue: asyncio.Queue = context["outQueue"],
    user: dict = context["User"]
    userFullName: str = user["fullname"]
    welcomeMessage = {
        "__typename": "MessageGQLModel",
        "prompt": f"Hello {userFullName}",
    }
    systemMessages = [
        {"role": "system", "content": f"You are assistant for employee at university. Logged user's name is {userFullName}"},
    ]
    await outQueue.put(welcomeMessage)

    response = await inQueue.get()
    stop = response["__typename"] == "StopGQLModel"
    dialogMessages = []
    while not stop:
        dialogMessages.append(
            {"role": "user", "content": response["message"]}
        )
        
        prompt = "\n".join(systemMessages)
        prompt += "\n".join(dialogMessages)
        result = await kernel.invoke_prompt(prompt=prompt.strip())
        result_str = f"{result}"
        dialogMessages.append(
            {"role": "system", "content": result_str}
        )
        await outQueue.put({
            "__typename": "MessageGQLModel",
            "systemResponse": result_str
        })
        response = await inQueue.get()

from semantic_kernel.contents.chat_message_content import ChatMessageContent
# from semantic_kernel import KernelArguments
from semantic_kernel.functions import KernelArguments
from semantic_kernel.filters import FilterTypes, AutoFunctionInvocationContext

async def openChat():
    gqlClient = None
    gqlClient = await createGQLClient(
        username="john.newbie@world.com",
        password="john.newbie@world.com"
    )
    

    skills = []
    for plugin in kernel.plugins.values():
        skills.extend(plugin.functions.keys())
        print(skills)

    history = ChatHistory()
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    
    async def inject_gql_client(
        context: AutoFunctionInvocationContext,
        next
    ):
        # sem se nikdy nedostane do JSONu pro LLM, 
        # naváže se těsně před voláním Python‐funkce
        context.arguments["gqlclient"] = gqlClient
        await next(context)
    
    kernel.add_filter(FilterTypes.AUTO_FUNCTION_INVOCATION, inject_gql_client)
    
    def trim_history(history: ChatHistory, max_msgs: int = 20):
        entries = history.serialize()  # seznam dictů s role, skill, content
        preserved = [e for e in entries if e.get("metadata", {}).get("important")]
        others    = [e for e in entries if e not in preserved]
        to_keep   = preserved + others[-(max_msgs - len(preserved)):]
        history.clear()
        for e in to_keep:
            history.add(e["role"], e["content"], metadata=e.get("metadata"))

    # user_input = yield "Chat session initialized. Zadejte dotaz nebo 'exit'."
    async def hook(user_input):
        if user_input.strip().lower() == "exit":
            return None
        history.add_user_message(user_input)
        result = await azure_chat.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
            arguments=KernelArguments()
        )

        return result
        
    return hook


async def main():
    import openai

    gqlClient = None
    gqlClient = await createGQLClient(
        username="john.newbie@world.com",
        password="john.newbie@world.com"
    )
    

    skills = []
    for plugin in kernel.plugins.values():
        skills.extend(plugin.functions.keys())
        print(skills)

    # for pname, plugin in kernel.plugins.items():
    #     print(f"Plugin: {pname}")
    #     print("  Functions:", list(plugin.functions))


    history = ChatHistory()
    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    
    async def inject_gql_client(
        context: AutoFunctionInvocationContext,
        next
    ):
        # sem se nikdy nedostane do JSONu pro LLM, 
        # naváže se těsně před voláním Python‐funkce
        context.arguments["gqlclient"] = gqlClient
        await next(context)
    
    kernel.add_filter(FilterTypes.AUTO_FUNCTION_INVOCATION, inject_gql_client)


    # kernel.add_filter(
    #     filter_type=FilterTypes.AUTO_FUNCTION_INVOCATION,
    #     filter=add_user_context_filter
    # )
    # extra_context = {"foo": "bar", "chat_history": "chat_history", "gqlclient": gqlClient}
    
    # from semantic_kernel.agents import ChatCompletionAgent
    # agent = ChatCompletionAgent(
    #     kernel=kernel,
    #     service=azure_chat,
    #     name="OrchestratorAgent",
    #     # instructions="You may call programPage(limit:int,skip:int) when needed.",
    #     instructions="",
    #     arguments=KernelArguments(extraContext=extra_context),
        
    # )    
    # extra_context = KernelArguments({"foo": "bar", "chat_history": history})
    

    # fn = kernel.get_function(
    #     plugin_name="graphql",
    #     function_name="detectTypes"
    # )
    # print(f"fn: {fn}")
    # try:
    #     result = await kernel.invoke(fn, user_prompt="najdi členy skupiny")
    #     print(f"result: {result}")
    # except Exception as e:
    #     print(e)

    while True:
        user_input = input("Uživatel: ")
        if user_input == "exit":
            break
        history.add_user_message(user_input)
        # print(f"history: {history.serialize()}")
        # https://learn.microsoft.com/en-us/semantic-kernel/concepts/ai-services/chat-completion/function-calling/?pivots=programming-language-python
        result = await azure_chat.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
            # context_variables={"extraContext": extra_context}
            arguments=KernelArguments()
        )

        # vrat mi 5 studijnich programu
        # 
        # result = await agent.get_response(
            
        #     user_input,
        #     kernel=kernel,
        #     arguments=KernelArguments(extraContext=extra_context)
        #     # history=history,
        #     # settings=execution_settings
        # )

        # result = await kernel.invoke_prompt(
        #     prompt=user_input,                      # text od uživatele
        #     history=history,                        # vaše ChatHistory
        #     settings=execution_settings,            # AzureChatPromptExecutionSettings s Auto()
        #     arguments=KernelArguments(
        #         extraContext=extra_context          # sem napochytíte user_id, extraContext, …
        #     )
        # ) 
        # azure_chat.
        # result = await kernel.invoke_prompt(
        #     prompt=user_input
        #     # function_name=None,
        #     # plugin_name=None,
        #     # arguments={"user_input": user_input}
        # )

        # def display(value: ChatMessageContent):
        #     print("="*30)
        #     print(value)
        #     print("="*30)
        #     # print(value.content)
        #     # value.content.
        #     print("="*30)
        #     print(f'usage: {value.metadata.get("usage")}')

        # if hasattr(result, "value"):
        #     if isinstance(result.value, list):
        #         for value in result.value:
        #             display(value)
        #     else:
        #         display(value)

        print(f"Assistant: {result}")


def create_graphql_detection_skill(kernel: Kernel):

    import json
    import graphql
    sdl_path = Path(__file__).parent / "./sdl.graphql"
    sdl_path = sdl_path.resolve()
    with open(sdl_path, "r", encoding="utf-8") as f:
        sdl_lines = f.readlines()
    sdl = "\n".join(sdl_lines)
    ast = graphql.parse(sdl)

    print(f"sdl_path: {sdl_path}")
    result = {}
    for node in ast.definitions:
        if isinstance(node, graphql.language.ast.ObjectTypeDefinitionNode):
            name = node.name.value
            if "Error" in name:
                continue
            description = node.description.value if node.description else None
            result[name] = {"name": name, "description": description}

    result = list(result.values())
    prompt = f"""
<message role="system">
    You can pair objects mentioned by the user with GraphQL types described in the JSON below.
    Analyze the user prompt and return only valid JSON: an array of strings, each exactly matching a type's `name`.
    Respond with a single JSON array—no additional text, no code fences.

    Rules:
    1. Exclude any types whose names end with `"Error"`, unless explicitly requested.
    2. Match on type name or on keywords found in the description.
    3. Detect 1:N (one-to-many) or N:1 relationships between the matched types, and order the array so that each parent type appears immediately before its child types.


    [EXAMPLE]
    prompt:
        "Give me a list of study programs and their students"
    output:
        ["ProgramGQLModel", "StudentGQLModel"]
    [END EXAMPLE]

    [GRAPHQLTYPES] 
```json
    {json.dumps(result, indent=2)}
```
    [END GRAPHQLTYPES] 


</message>
<message role="user">{{{{user_prompt}}}}</message>
"""
    prompt_path = Path(__file__).parent / "./types_prompt.txt"
    prompt_path = prompt_path.resolve()
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    # graphql_detection_skill = KernelFunctionFromPrompt.from_prompt(
    #     function_name="graphql_detection_skill",
    #     plugin_name="graphql",
    #     prompt=prompt
    # )    

    # kernel.add_function(
    #     plugin_name="graphql",
    #     # function=graphql_detection_skill,
    #     prompt=prompt,
    #     description=""
    # )


    ptc = PromptTemplateConfig(
        template=prompt,
        name="graphql_detection",
        template_format="handlebars",
        # execution_settings=req
    )    

    # print("=== RENDERED PROMPT ===")
    # print(prompt.replace("user_prompt", "najdi členy skupiny"))
    # print("=======================")

    graphql_fn = kernel.add_function(
        function_name="detectTypes",
        plugin_name="graphql",
        prompt_template_config=ptc,
        description="Detect GraphQL types from a user query, it is usefull when user want to query for data,"
    )
    return graphql_fn
     
def explain_graphql_query():
    from graphql import (
        parse,
        build_ast_schema,
        print_ast
    )
    from graphql.language import DocumentNode, FieldNode
    from graphql.language.visitor import visit
    from graphql.utilities import TypeInfo
    from graphql import parse, build_ast_schema, TypeInfo, visit, GraphQLSchema
    from graphql.language.visitor import visit
    from graphql.language.ast import (
        DocumentNode,
        FieldNode,
        SelectionSetNode,
        OperationDefinitionNode,
    )
    from graphql.type.definition import (
        GraphQLObjectType,
        GraphQLNonNull,
        GraphQLList,
    )

    sdlfilename = "./sdl.graphql"
    _path = Path(__file__).parent
    sdl_path =  _path / sdlfilename
    sdl_path = sdl_path.resolve()
    schema_sdl = sdl_path.read_text(encoding="utf-8")
    schema_ast = parse(schema_sdl)
    schema = build_ast_schema(schema_ast)

    # map description z AST schématu
    field_meta: dict[tuple[str,str], str|None] = {}
    for defn in schema_ast.definitions:
        from graphql.language.ast import ObjectTypeDefinitionNode
        if isinstance(defn, ObjectTypeDefinitionNode):
            parent = defn.name.value
            for fld in defn.fields or []:
                desc = fld.description.value if fld.description else None
                field_meta[(parent, fld.name.value)] = desc
                    
    query = """
query groupPage($skip: Int, $limit: Int, $orderby: String, $where: GroupInputWhereFilter) {
  groupPage(skip: $skip, limit: $limit, orderby: $orderby, where: $where) {
    ...GroupGQLModelMediumFragment
    memberships {
      ...MembershipGQLModelMediumFragment
    }
  }
}

fragment GroupGQLModelMediumFragment on GroupGQLModel {
  __typename
  id
  lastchange
  created
  createdbyId
  changedbyId
  rbacobjectId
  name
  nameEn
  email
  abbreviation
  startdate
  enddate
  grouptypeId
  mastergroupId
  path
  valid
}

fragment MembershipGQLModelMediumFragment on MembershipGQLModel {
  __typename
  id
  lastchange
  created
  createdbyId
  changedbyId
  rbacobjectId
  userId
  groupId
  valid
  startdate
  enddate
}
    """

    # parse → AST (DocumentNode)
    query_ast = parse(query)

    # vytisknout strom
    print(query_ast)
    # nebo jako JSON
    import json
    def node_to_dict(node):
        # graphql-core AST nodes mají `.to_dict()` na Python 3.10+:
        return node.to_dict()

    print(json.dumps(node_to_dict(query_ast), indent=2))

    # zpět na string
    print(print_ast(query_ast))

    def unwrap_type(gtype):
        """Strip away NonNull and List wrappers to get the base Named type."""
        while isinstance(gtype, (GraphQLNonNull, GraphQLList)):
            gtype = gtype.of_type
        return gtype

    def type_node_to_str(type_node) -> str:
        """Renders a VariableDefinitionNode.type back to a string."""
        kind = type_node.kind  # e.g. 'NonNullType', 'ListType', or 'NamedType'
        if kind in ["NamedType", "named_type"]:
            return type_node.name.value
        if kind in ["NonNullType", "non_null_type"]:
            return f"{type_node_to_str(type_node.type)}!"
        if kind in ["ListType", "list_type"]:
            return f"[{type_node_to_str(type_node.type)}]"
        raise ValueError(f"Unknown kind {kind}")
    
    def print_query_with_header_comments(query_ast: DocumentNode, schema: GraphQLSchema) -> str:
        # 1) Gather input (variable) descriptions
        var_lines: list[str] = []

        for defn in query_ast.definitions:
            if isinstance(defn, OperationDefinitionNode) and defn.variable_definitions:
                # Předpokládáme, že dotaz obsahuje právě jedno root pole, např. userById
                root_sel = next(
                    (s for s in defn.selection_set.selections if isinstance(s, FieldNode)),
                    None
                )
                if not root_sel:
                    continue

                root_field_name = root_sel.name.value
                # query_type, mutation_type nebo subscription_type dle defn.operation
                root_type_map = {
                    "QUERY":       schema.query_type,
                    "mutation":    schema.mutation_type,
                    "subscription": schema.subscription_type
                }
                root_type = root_type_map[defn.operation.name]
                root_field_def = root_type.fields.get(root_field_name)

                for var_def in defn.variable_definitions:  # type: VariableDefinitionNode
                    name     = var_def.variable.name.value     # např. "id"
                    type_str = type_node_to_str(var_def.type)  # např. "UUID!"
                    # najdi popis argumentu
                    desc = None
                    if root_field_def and name in root_field_def.args:
                        arg_def = root_field_def.args[name]
                        desc = arg_def.description
                    # očisti whitespace
                    if desc:
                        desc = " ".join(desc.split())
                        var_lines.append(f"# @param {{{type_str}}} {name} - {desc}")
                    else:
                        var_lines.append(f"# @param {{{type_str}}} {name}")


        # 2) Gather output (field) descriptions with full dotted path
        out_lines: list[str] = []
        def walk(
            sel_set: SelectionSetNode,
            parent_type: GraphQLObjectType,
            prefix: str
        ):
            for sel in sel_set.selections:
                if not isinstance(sel, FieldNode):
                    continue
                fname = sel.name.value
                path  = f"{prefix}.{fname}" if prefix else fname

                fld_def = parent_type.fields.get(fname)
                if not fld_def:
                    continue

                # unwrap to get the NamedType
                base_type = unwrap_type(fld_def.type)  # GraphQLNamedType
                # fetch the description and normalize whitespace
                desc = field_meta.get((parent_type.name, fname))
                if desc:
                    desc = " ".join(desc.split())
                    # from:
                    # out_lines.append(f'# @property {{""}} {path} - {desc}')
                    # to:
                    out_lines.append(f'# @property {{{base_type.name}}} {path} - {desc}')

                # recurse into nested selections
                if sel.selection_set and isinstance(base_type, GraphQLObjectType):
                    walk(sel.selection_set, base_type, path)

        for defn in query_ast.definitions:
            if isinstance(defn, OperationDefinitionNode):
                # print(f"schema: \n{dir(schema)}")
                root_map = {
                    "QUERY": schema.query_type,
                    "mutation": schema.mutation_type,
                    "subscription": schema.subscription_type
                }
                root = root_map[defn.operation.name]
                walk(defn.selection_set, root, prefix="")

        # 3) Build the header block
        header = []
        if var_lines:
            header.append("# ")
            header.extend(var_lines)
        header.append("# @returns {Object}")
        if out_lines:
            header.append("# ")
            header.extend(out_lines)

        # 4) Print the actual query (unmodified) below
        query_str = print_ast(query_ast)

        return "\n".join(header + ["", query_str])  
    
    query_with_header_comments = print_query_with_header_comments(query_ast=query_ast, schema=schema)
    print(f"query_with_header_comments: \n{query_with_header_comments}")

explain_graphql_query()
create_graphql_detection_skill(kernel=kernel)
print("ast used")
# asyncio.run(main())