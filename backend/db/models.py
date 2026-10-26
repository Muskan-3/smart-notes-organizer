# The Note table: one row per processed note (PDF, image, or audio).

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func

from db.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "pdf", "image", or "audio"
    extracted_text = Column(Text, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    tags = Column(JSON, nullable=False)  # stored as a JSON list, e.g. ["cloud", "aws", ...]
    category = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
