from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200
)

def split_pages(pages):
    # Split each page on its own so every chunk belongs to exactly one page
    chunks = []

    for page in pages:
        for text in splitter.split_text(page["text"]):
            chunks.append({
                "page": page["page"],
                "text": text
            })

        # A table is never split: one chunk per table, with its context on top
        for table in page.get("tables", []):
            chunks.append({
                "page": page["page"],
                "text": format_table(table)
            })

    return chunks

def format_table(table):
    parts = []

    if table.get("heading"):
        parts.append(f"## {table['heading']}")
    if table.get("caption"):
        parts.append(table["caption"])
    parts.append(table["markdown"])

    return "\n\n".join(parts)
