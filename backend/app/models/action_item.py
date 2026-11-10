
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class ActionItem(Base):
    __tablename__ = "action_items"

    action_id = Column(String(50), primary_key=True, index=True)

    theme_id = Column(String(50), ForeignKey("themes.theme_id"), nullable=False)

    action_title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(30), nullable=False, default="medium")
    status = Column(String(30), nullable=False, default="open")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
