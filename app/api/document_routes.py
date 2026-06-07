from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db

from app.services.document_service import (
    get_documents,
    get_document
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