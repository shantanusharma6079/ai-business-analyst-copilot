from app.services.search_service import (search_chunks)
from app.services.llm_service import (generate_response)

def format_source(row):
    source = f"{row.file_name}"
    if row.page is not None:
        source += f", page {row.page}"
    if row.ocr_confidence is not None:
        source += f", OCR confidence {row.ocr_confidence:.0f}%"
    return source

def get_sources(chunks):
    # One entry per (document, page), in ranking order
    sources = []
    seen = set()

    for row in chunks:
        key = (row.document_id, row.page)
        if key in seen:
            continue
        seen.add(key)
        sources.append({
            "document_id": row.document_id,
            "file_name": row.file_name,
            "page": row.page,
            "ocr_confidence": row.ocr_confidence
        })

    return sources

def ask_question(db, question):
    chunks = search_chunks(db, question)

    context = "\n\n".join([
        f"[Source: {format_source(row)}]\n{row.chunk_text}"
        for row in chunks
    ])

    prompt = f"""
        You are a senior business analyst.

        Answer ONLY using the provided context.

        If the answer is not found,
        say you don't know.

        Context:

        {context}

        Question:

        {question}
    """

    answer = generate_response(prompt)

    return {
        "answer": answer,
        "sources": get_sources(chunks)
    }
