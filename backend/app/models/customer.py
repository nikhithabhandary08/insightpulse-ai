
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True, unique=True)
    country = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
