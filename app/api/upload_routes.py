from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from app.services.pdf_service import extract_pdf_text
from app.services.document_service import save_document
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from app.services.chunk_service import (split_document)
from app.services.document_service import (store_chunks)

import os

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_DIR = "uploads"

@router.post("")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    text = extract_pdf_text(file_path)

    document = save_document(db, file.filename, file_path, text)

    chunks = split_document(text)
    chunk_count = store_chunks(db, document.id, chunks)

    return {
        "document_id": document.id,
        "file_name": document.file_name,
        "chunks_created": chunk_count
    }