import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.document_routes import router as document_router
from app.api.upload_routes import router as upload_router
from app.api.search_routes import router as search_router
from app.api.ask_routes import router as ask_router
from app.database.db import SessionLocal
from app.services.document_service import fail_interrupted_documents

# Schema is managed by Alembic: run `alembic upgrade head`

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background tasks live in memory: any that were running died with the old process
    db = SessionLocal()
    try:
        count = fail_interrupted_documents(db)
        if count:
            logger.warning("Marked %s interrupted document(s) as failed", count)
    finally:
        db.close()

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(document_router)
app.include_router(upload_router)
app.include_router(search_router)
app.include_router(ask_router)
