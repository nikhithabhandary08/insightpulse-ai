
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Integer
from sqlalchemy.sql import func

from app.db.database import Base


class Review(Base):
    __tablename__ = "reviews"

    # Unique review ID: REV-2026-000001
    review_id = Column(
        String(50),
        primary_key=True,
        index=True
    )

    # Customer relationship
    customer_id = Column(
        String(50),
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    # Product relationship
    product_id = Column(
        String(50),
        ForeignKey("products.product_id"),
        nullable=False
    )

    # Feedback channel relationship
    channel_id = Column(
        String(50),
        ForeignKey("channels.channel_id"),
        nullable=False
    )

    # Original customer feedback
    review_text = Column(
        Text,
        nullable=False
    )

    # Customer rating from 1 to 5
    rating = Column(
        Integer,
        nullable=True
    )

    # Predicted sentiment: Positive, Neutral, Negative, Mixed
    sentiment = Column(
        String(20),
        nullable=True
    )

    # Model prediction confidence (0.0 to 1.0)
    sentiment_confidence = Column(
        Float,
        nullable=True
    )

    # Assigned theme relationship
    theme_id = Column(
        String(50),
        ForeignKey("themes.theme_id"),
        nullable=True
    )

    # Model-predicted theme
    predicted_theme = Column(
        String(100),
        nullable=True
    )

    # Review submission timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
