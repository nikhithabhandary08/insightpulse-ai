
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(String(50), primary_key=True, index=True)
    channel_name = Column(String(100), nullable=False, unique=True)
    description = Column(String(250), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
