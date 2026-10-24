import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    CheckConstraint
)
from sqlalchemy.sql import func

from .db import Base

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    document_type = Column(String)
    file_path = Column(String)
    extracted_text = Column(Text)
    status = Column(
        String(20),
        nullable=False,
        server_default=DocumentStatus.PENDING.value
    )
    error = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'ready', 'failed')",
            name="ck_documents_status"
        ),
    )