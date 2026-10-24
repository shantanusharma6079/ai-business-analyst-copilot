from fastapi import FastAPI
from app.api.document_routes import router as document_router
from app.api.upload_routes import router as upload_router
from app.api.search_routes import router as search_router
from app.api.ask_routes import router as ask_router

# Schema is managed by Alembic: run `alembic upgrade head`

app = FastAPI()

app.include_router(document_router)
app.include_router(upload_router)
app.include_router(search_router)
app.include_router(ask_router)