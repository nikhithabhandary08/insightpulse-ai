
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float
)
from sqlalchemy.sql import func

from app.db.database import Base


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    # Unique response ID: RESP-SUR-2026-000001-001
    response_id = Column(
        String(100),
        primary_key=True,
        index=True
    )

    # Survey relationship
    survey_id = Column(
        String(50),
        ForeignKey("surveys.survey_id"),
        nullable=False
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

    # Channel relationship
    channel_id = Column(
        String(50),
        ForeignKey("channels.channel_id"),
        nullable=False
    )

    # Original survey feedback
    response_text = Column(
        Text,
        nullable=False
    )

    # Predicted sentiment
    sentiment = Column(
        String(20),
        nullable=True
    )

    # Sentiment prediction confidence (0.0 to 1.0)
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

    # Survey submission timestamp
    submitted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
