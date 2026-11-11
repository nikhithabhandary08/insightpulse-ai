
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float,
    Integer
)
from sqlalchemy.sql import func

from app.db.database import Base


class ActionItem(Base):
    __tablename__ = "action_items"

    # Unique action ID
    action_id = Column(
        String(50),
        primary_key=True,
        index=True
    )

    # Related feedback theme
    theme_id = Column(
        String(50),
        ForeignKey("themes.theme_id"),
        nullable=False
    )

    # Action details
    action_title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    # Priority: Low, Medium, High, Critical
    priority = Column(
        String(30),
        nullable=False,
        default="Medium"
    )

    # Status: Open, In Progress, Resolved
    status = Column(
        String(30),
        nullable=False,
        default="Open"
    )

    # Number of feedback records supporting this action
    source_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    # Measured negative feedback percentage
    negative_percentage = Column(
        Float,
        nullable=True
    )

    # Threshold that triggered the action
    threshold_percentage = Column(
        Float,
        nullable=True
    )

    # Action creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
