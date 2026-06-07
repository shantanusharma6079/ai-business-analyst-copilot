from pydantic import BaseModel

class DocumentCreate(BaseModel):
    file_name: str
    document_type: str

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    document_type: str

    class Config:
        from_attributes = True