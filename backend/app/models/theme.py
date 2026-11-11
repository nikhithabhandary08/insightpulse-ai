
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Theme(Base):
    __tablename__ = "themes"

    # Unique theme ID: THEME-000001
    theme_id = Column(
        String(50),
        primary_key=True,
        index=True
    )

    # Allowed themes:
    # Performance, Customer Support, Feature Request
    theme_name = Column(
        String(100),
        nullable=False,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
