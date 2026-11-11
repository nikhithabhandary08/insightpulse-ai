
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime

from app.db.database import Base


class AnomalyRecord(Base):
    __tablename__ = "anomaly_records"

    anomaly_id = Column(String(50), primary_key=True, index=True)

    source_type = Column(String(50), nullable=False)
    source_id = Column(String(100), nullable=False)

    anomaly_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)

    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)

    status = Column(String(30), nullable=False, default="Open")

    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
