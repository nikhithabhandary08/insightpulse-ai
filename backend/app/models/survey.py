
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Survey(Base):
    __tablename__ = "surveys"

    survey_id = Column(String(50), primary_key=True, index=True)
    survey_title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
