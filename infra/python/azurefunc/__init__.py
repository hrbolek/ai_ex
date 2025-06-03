import azure.functions as func
from .adddocument import main as adddocument
from .search import main as searchdocument
from .removedocument import main as removedocument

from .static import main as staticmain

app = func.FunctionApp()
func_adddocument = app.route(route="adddocument", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])(adddocument)
func_search = app.route(route="search", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(searchdocument)
func_removedocument = app.route(route="removedocument", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(removedocument)
func_static = app.route(route="static", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(staticmain)