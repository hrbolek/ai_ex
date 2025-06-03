import azure.functions as func
from adddocument import main as adddocumentmain
from removedocument import main as removedocumentmain
from search import main as searchmain


app = func.FunctionApp()
func_adddocument = app.route(route="adddocument", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])(adddocumentmain)
func_removedocument = app.route(route="removedocument", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(removedocumentmain)
func_search = app.route(search="search", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(searchmain)