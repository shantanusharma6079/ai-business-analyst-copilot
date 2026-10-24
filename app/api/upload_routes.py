from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.database.models import DocumentStatus
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from app.services.document_service import (create_document, ingest_document)
from app.services.validation_service import (
    MAX_UPLOAD_BYTES,
    InvalidPDFError,
    validate_pdf
)

import os

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_DIR = "uploads"

@router.post("")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):

    # Read one byte past the limit: enough to detect "too big" without loading it all
    data = await file.read(MAX_UPLOAD_BYTES + 1)

    # Rejected files never reach disk or the database
    try:
        validate_pdf(data)
    except InvalidPDFError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(data)

    document = create_document(db, file.filename, file_path)
    chunk_count = ingest_document(db, document)

    body = {
        "document_id": document.id,
        "file_name": document.file_name,
        "status": document.status,
        "error": document.error,
        "chunks_created": chunk_count
    }

    if document.status == DocumentStatus.FAILED.value:
        return JSONResponse(status_code=422, content=body)

    return body
