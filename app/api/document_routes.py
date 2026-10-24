from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.database import get_db

from app.services.document_service import (
    get_documents,
    get_document,
    get_document_status
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.get("")
def get_all_documents(
    db: Session = Depends(get_db)
):

    documents = get_documents(db)

    return {
        "status": True,
        "document_count": len(documents),
        "documents": documents
    }


@router.get("/{document_id}/status")
def get_status(
    document_id: int,
    db: Session = Depends(get_db)
):
    # Lightweight endpoint for polling: no extracted_text in the payload
    status = get_document_status(db, document_id)

    if status is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return status


@router.get("/{document_id}")
def get_single_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = get_document(
        db,
        document_id
    )

    if document:
        return {
            "status": True,
            "document": document
        }

    return {
        "status": False,
        "message": "Document not found"
    }