import os

# Config načítání
def getenv(key, default=""):
    return os.getenv(key, default)

from semantic_kernel.functions import kernel_function

@kernel_function()
async def filter_docs(documents) -> list:
    # Dummy filtr - vše povoleno
    return documents