import azure.functions as func
from adddocument import adddocumenthandler as adddocument
from search import searchdocumenthandler as searchdocument
from removedocument import removedocumenthandler as removedocument

from static import statichandler as staticmain

app = func.FunctionApp()
func_adddocument = app.route(route="adddocument", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])(adddocument)
func_search = app.route(route="searchold", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(searchdocument)
func_removedocument = app.route(route="removedocument", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(removedocument)
func_static = app.route(route="static", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(staticmain)


from search_with_kernels import searchkernelshandler as searchdocument2

func_search2 = app.route(route="search2", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(searchdocument2)

from search_with_kernel_plugin import searchkernelsPluginhandler
func_search3 = app.route(route="search", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(searchkernelsPluginhandler)

from auth import main_auth

func_with_auth = app.route(route="auth", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET", "OPTIONS"])(main_auth)