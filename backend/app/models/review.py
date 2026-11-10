
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(String(50), primary_key=True, index=True)

    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    channel_id = Column(String(50), ForeignKey("channels.channel_id"), nullable=False)

    review_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
