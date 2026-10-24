from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException
from fastapi import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from app.dependencies.database import get_db
from sqlalchemy.orm import Session
from app.services.document_service import (create_document, run_ingestion)
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

@router.post("", status_code=202)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Read one byte past the limit: enough to detect "too big" without loading it all
    data = await file.read(MAX_UPLOAD_BYTES + 1)

    # Rejected files never reach disk or the database.
    # Parsing is blocking work, so keep it off the event loop.
    try:
        await run_in_threadpool(validate_pdf, data)
    except InvalidPDFError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(data)

    document = create_document(db, file.filename, file_path)

    # Runs after the response is sent; pass the id, not the ORM object
    background_tasks.add_task(run_ingestion, document.id)

    return {
        "document_id": document.id,
        "file_name": document.file_name,
        "status": document.status,
        "status_url": f"/documents/{document.id}/status"
    }
