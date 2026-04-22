from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector # Ensure this is the import
from .base import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("chat_folders.id", ondelete="CASCADE"))
    content = Column(String, nullable=False)
    filename = Column(String)
    embedding = Column(Vector(384))