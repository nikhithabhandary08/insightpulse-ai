
from pydantic import BaseModel, ConfigDict
from typing import Optional


class SurveyCreate(BaseModel):
    survey_id: str
    survey_title: str
    description: Optional[str] = None
    status: str = "active"


class SurveyResponse(SurveyCreate):
    model_config = ConfigDict(from_attributes=True)
