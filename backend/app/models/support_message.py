
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


class SupportMessage(Base):
    __tablename__ = "support_messages"

    # Unique message ID: MSG-<ticket-id>-001
    message_id = Column(
        String(100),
        primary_key=True,
        index=True
    )

    # Customer relationship
    customer_id = Column(
        String(50),
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    # Communication channel relationship
    channel_id = Column(
        String(50),
        ForeignKey("channels.channel_id"),
        nullable=False
    )

    # Support ticket ID
    ticket_id = Column(
        String(50),
        nullable=False,
        index=True
    )

    # Original customer support message
    message_text = Column(
        Text,
        nullable=False
    )

    # Predicted sentiment: Positive, Neutral, Negative, Mixed
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

    # Message timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
