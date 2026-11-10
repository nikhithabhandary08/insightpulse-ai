
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    response_id = Column(String(100), primary_key=True, index=True)

    survey_id = Column(String(50), ForeignKey("surveys.survey_id"), nullable=False)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)

    response_text = Column(Text, nullable=False)

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
