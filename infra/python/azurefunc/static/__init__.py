

import azure.functions as func

from .result import HTML
# --- HELPERS -------------------------------------------------


# def get_content(extension):
#     # Get the current directory
#     current_dir = os.path.dirname(__file__)
#     # Find CSS files
#     for file in current_dir.glob('*.{}'.format(extension)):
#         try:
#             content = file.read_text(encoding="utf-8")
#             print(f"Loaded {file.name} ({len(content)} characters)")
#             return content
#         except Exception as e:
#             print(f"Error reading {file}: {e}")

# css_content = get_content("css")
# js_content = get_content("js")
# html_content = get_content("html")

# html_content = html_content.replace("$STYLE$", css_content)
# html_content = html_content.replace("$SCRIPT$", js_content)

def main(req: func.HttpRequest) -> func.HttpResponse:

        
    html = HTML.replace('*/', '*/\n')
    return func.HttpResponse(
        html,
        mimetype="text/html",
        status_code=200
    )
