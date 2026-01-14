from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class RedactionLog(Base):
    __tablename__ = "redaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    input_type = Column(Text, nullable=False)
    redacted_output = Column(Text, nullable=False)
    entity_count = Column(Integer)
    columns_redacted = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
