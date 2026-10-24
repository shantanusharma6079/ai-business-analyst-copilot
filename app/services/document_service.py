from app.database.models import Document, DocumentStatus
from app.database.chunk_models import (DocumentChunk)
from app.services.embedding_service import (generate_embeddings)
from app.services.pdf_service import (extract_pdf_pages)
from app.services.chunk_service import (split_pages, format_table)

def create_document(db, file_name, file_path):
    document = Document(
        file_name = file_name,
        document_type = "pdf",
        file_path = file_path,
        status = DocumentStatus.PENDING.value
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

def set_status(db, document, status, error=None):
    document.status = status.value
    document.error = error
    db.commit()

def ingest_document(db, document):
    # pending -> processing -> ready | failed
    set_status(db, document, DocumentStatus.PROCESSING)

    try:
        pages = extract_pdf_pages(document.file_path)
        skipped = [page for page in pages if page.get("error")]

        if len(skipped) == len(pages):
            raise ValueError(f"All {len(pages)} pages failed, first error: {skipped[0]['error']}")

        text = "\n".join(
            "\n\n".join([page["text"]] + [format_table(table) for table in page["tables"]])
            for page in pages
        )

        if not text.strip():
            raise ValueError("No extractable text (blank pages, or OCR found nothing)")

        chunks = split_pages(pages)
        chunk_count = store_chunks(db, document.id, chunks)

        # On a ready document, error holds a warning about skipped pages
        warning = None
        if skipped:
            numbers = ", ".join(str(page["page"]) for page in skipped)
            warning = f"Skipped pages {numbers}. First error: {skipped[0]['error']}"[:1000]

        # Chunks, text and status commit together: all or nothing
        document.extracted_text = text
        set_status(db, document, DocumentStatus.READY, warning)

        return chunk_count

    except Exception as e:
        db.rollback()
        set_status(db, document, DocumentStatus.FAILED, f"{type(e).__name__}: {e}"[:1000])

        return 0

def get_documents(db):
    return db.query(Document).all()

def get_document(db, document_id):
    return db.query(Document).filter(Document.id == document_id).first()

def store_chunks(db, document_id, chunks):
    # Adds rows to the session; the caller commits
    rows = []
    embeddings = generate_embeddings([chunk["text"] for chunk in chunks])

    for chunk, embedding in zip(chunks, embeddings):
        row = DocumentChunk(
            document_id = document_id,
            chunk_text = chunk["text"],
            page = chunk["page"],
            ocr_confidence = chunk.get("ocr_confidence"),
            embedding = embedding
        )
        rows.append(row)

    db.add_all(rows)

    return len(rows)
