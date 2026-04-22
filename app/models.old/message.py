from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.dialects.postgresql import UUID


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("chat_folders.id", ondelete="CASCADE"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())