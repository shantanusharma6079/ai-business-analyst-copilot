from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    Index
)

from pgvector.sqlalchemy import Vector
from app.database.db import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_text = Column(Text)
    page = Column(Integer)
    embedding = Column(Vector(384))

    __table_args__ = (
        # Must use vector_cosine_ops to serve the <=> (cosine distance) operator
        Index(
            "ix_document_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"}
        ),
    )
