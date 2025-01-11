import os
import re
import io
from pathlib import Path
from markitdown import MarkItDown


markitdown = MarkItDown()    

def docx2md(docx_content):
    stream = io.BytesIO(docx_content)
    # markdown_result = markitdown.convert_stream(stream, file_extension="docx")
    markdown_result = markitdown.convert_stream(stream, file_extension="docx")
    return markdown_result.text_content

def get_all_documents(directory="./sourcefiles"):
    results = []
    source_dir = Path(directory)
    for docx_file in source_dir.glob("*.docx"):
        source_file_name = f"{source_dir}" + "/" + docx_file.name
        results.append(source_file_name)
    return results

def read_file(source_file_name):
    with open(source_file_name, "rb") as file:
        docx_content = file.read()
    return docx_content

def write_file(source_file_name, markdown_result):
    name_parts = source_file_name.split('/')
    md_name_parts = [*name_parts[:-1], "output", name_parts[-1]]
    md_name = '/'.join(md_name_parts)
    
    md_name = md_name.replace(".docx", ".md")
    with open(md_name, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_result)
    return markdown_result

def process_into_md(directory="./sourcefiles"):
    all_docx = get_all_documents(directory)
    all_md = ((f, docx2md(read_file(f))) for f in all_docx)
    written = (write_file(f, c) for (f, c) in all_md)
    written = list(written)
    chunked = chunk_md(written)
    return 

def chunk_md(md_contents):
    output_dir = "./sourcefiles/output/"
    # Regex for section headers (e.g., "1.", "1.1")
    section_pattern = re.compile(r"^\d+(\.\d+)*\s.+", re.MULTILINE)

    start = 1
    for md_content in md_contents:
        # Split content into sections
        sections = section_pattern.split(md_content)
        headers = section_pattern.findall(md_content)

        # Combine headers and sections
        chunks = [f"{header}\n{text}" for header, text in zip(headers, sections)]

        # Save each chunk
        for i, chunk in enumerate(chunks, start=start):
            start = i
            chunk_file =  f"{output_dir}chunk_{i}.md"
            with open(chunk_file, "w", encoding="utf-8") as out_file:
                out_file.write(chunk)


process_into_md()


# import re
# from pathlib import Path

# # Read the file
# file_path = "1 Mgr_Podmínky PŘ v AR 2025-2026 - rev.md"
# output_dir = Path("./chunks")
# output_dir.mkdir(exist_ok=True)

# # Load file content
# with open(file_path, "r", encoding="utf-8") as file:
#     content = file.read()

# # Regex for section headers (e.g., "1.", "1.1")
# section_pattern = re.compile(r"^\d+(\.\d+)*\s.+", re.MULTILINE)

# # Split content into sections
# sections = section_pattern.split(content)
# headers = section_pattern.findall(content)

# # Combine headers and sections
# chunks = [f"{header}\n{text}" for header, text in zip(headers, sections)]

# # Save each chunk
# for i, chunk in enumerate(chunks, start=1):
#     chunk_file = output_dir / f"chunk_{i}.md"
#     with open(chunk_file, "w", encoding="utf-8") as out_file:
#         out_file.write(chunk)

# print(f"Chunks saved in {output_dir}")
