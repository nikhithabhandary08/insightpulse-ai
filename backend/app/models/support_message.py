
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class SupportMessage(Base):
    __tablename__ = "support_messages"

    message_id = Column(String(100), primary_key=True, index=True)

    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    channel_id = Column(String(50), ForeignKey("channels.channel_id"), nullable=False)

    ticket_id = Column(String(50), nullable=False)
    message_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
