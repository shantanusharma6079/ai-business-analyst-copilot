from app.database.models import Document
from app.database.chunk_models import (DocumentChunk)
from app.services.embedding_service import (generate_embedding)

def save_document(db, file_name, file_path, text):
    document = Document(
        file_name = file_name,
        document_type = "pdf",
        file_path = file_path,
        extracted_text = text
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

def get_documents(db):
    return db.query(Document).all()

def get_document(db, document_id):
    return db.query(Document).filter(Document.id == document_id).first()

def store_chunks(db, document_id, chunks):
    rows = []
    
    for chunk in chunks:
        embedding = generate_embedding(chunk)
        row = DocumentChunk(
            document_id = document_id,
            chunk_text = chunk,
            embedding = embedding
        )
        rows.append(row)
    
    db.add_all(rows)
    db.commit()
    
    return len(rows)