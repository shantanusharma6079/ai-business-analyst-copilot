from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import (get_db)
from app.schemas.search import (SearchRequest)
from app.services.search_service import (search_chunks)

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

@router.post("")
def search(
    data: SearchRequest,
    db: Session = Depends(get_db)
):
    results = search_chunks(db, data.query)
    
    return {
        "status": True,
        "query": data.query,
        "results": [
            {
                "chunk_id": row[0],
                "chunk_text": row[1],
                "similarity": row[2]
            }
            for row in results
        ]
    }