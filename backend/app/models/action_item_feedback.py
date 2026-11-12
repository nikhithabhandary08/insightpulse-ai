from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class ActionItemFeedback(Base):
    __tablename__ = "action_item_feedback"

    mapping_id = Column(
        String(50),
        primary_key=True,
        index=True
    )

    action_id = Column(
        String(50),
        ForeignKey("action_items.action_id"),
        nullable=False,
        index=True
    )

    source_type = Column(
        String(30),
        nullable=False
    )

    source_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )