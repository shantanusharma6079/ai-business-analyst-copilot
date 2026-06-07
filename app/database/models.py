from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)
from sqlalchemy.sql import func

from .db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    document_type = Column(String)
    file_path = Column(String)
    extracted_text = Column(Text)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )