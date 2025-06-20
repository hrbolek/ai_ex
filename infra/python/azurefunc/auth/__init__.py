import base64
import json

def main_auth(req):
    principal = req.headers.get("x-ms-client-principal")
    if principal:
        user_info = json.loads(base64.b64decode(principal))
        return f"Hello, {user_info['userDetails']}!"
    else:
        return "No identity"