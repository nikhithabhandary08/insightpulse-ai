
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class SentimentLabel(Base):
    __tablename__ = "sentiment_labels"

    # Unique sentiment ID
    sentiment_id = Column(
        String(50),
        primary_key=True,
        index=True
    )

    # Allowed values: Positive, Neutral, Negative, Mixed
    sentiment_name = Column(
        String(50),
        nullable=False,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
