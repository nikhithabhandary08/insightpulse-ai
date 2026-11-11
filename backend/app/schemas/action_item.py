
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ActionItemCreate(BaseModel):
    action_id: str
    theme_id: str
    action_title: str
    description: str
    priority: str = "Medium"
    status: str = "Open"
    source_count: int = Field(default=0, ge=0)
    negative_percentage: Optional[float] = None
    threshold_percentage: Optional[float] = None


class ActionItemResponse(ActionItemCreate):
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
