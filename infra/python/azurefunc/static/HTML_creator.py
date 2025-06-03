from pathlib import Path

# binding na storage account
# 


def get_content(extension):
    # Get the current directory
    current_dir = Path(__file__).parent
    # Find CSS files
    for file in current_dir.glob('*.{}'.format(extension)):
        try:
            content = file.read_text(encoding="utf-8")
            print(f"Loaded {file.name} ({len(content)} characters)")
            return content
        except Exception as e:
            print(f"Error reading {file}: {e}")

def run_static_HTML(root):
    css_content = get_content("css")
    js_content = get_content("js")
    html_content = get_content("html")

    html_content = html_content.replace("$STYLE$", css_content)
    html_content = html_content.replace("$SCRIPT$", js_content)
    # $STYLE$
    # $SRIPT$
    current_dir = Path(__file__).parent
    with open(f"{current_dir}" + "/result.py", "w", encoding="utf-8") as f:
        f.write("HTML=\"\"\"")
        f.write(html_content + "\"\"\"")
    print(len(html_content))


if __name__ == "__main__":
    run_static_HTML(root=".")