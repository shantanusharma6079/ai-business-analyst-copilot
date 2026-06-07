from fastapi import APIRouter
from app.schemas.question import QuestionRequest
from fastapi import Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services.rag_service import ask_question

router = APIRouter(
    prefix="/ask",
    tags=["Ask"]
)

@router.post("")
def ask(data: QuestionRequest, db: Session = Depends(get_db)):
    answer = ask_question(db, data.question)
    return {
        "status": True,
        "question": data.question,
        "answer": answer
    }