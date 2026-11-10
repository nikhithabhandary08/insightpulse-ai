
from sqlalchemy import Column, String, Text

from app.db.database import Base


class SentimentLabel(Base):
    __tablename__ = "sentiment_labels"

    sentiment_id = Column(String(50), primary_key=True, index=True)
    sentiment_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
