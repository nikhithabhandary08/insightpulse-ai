
from pydantic import BaseModel, ConfigDict
from typing import Optional


class ThemeCreate(BaseModel):
    theme_id: str
    theme_name: str
    description: Optional[str] = None


class ThemeResponse(ThemeCreate):
    model_config = ConfigDict(from_attributes=True)
