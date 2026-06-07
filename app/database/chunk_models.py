from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)

from pgvector.sqlalchemy import Vector
from app.database.db import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_text = Column(Text)
    embedding = Column(Vector(384))