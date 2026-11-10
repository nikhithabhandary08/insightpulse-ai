
from sqlalchemy import Column, String, Text

from app.db.database import Base


class Theme(Base):
    __tablename__ = "themes"

    theme_id = Column(String(50), primary_key=True, index=True)
    theme_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
