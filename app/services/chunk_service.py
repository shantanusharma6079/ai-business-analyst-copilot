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

    return chunks
