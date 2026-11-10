
from pydantic import BaseModel, ConfigDict


class SurveyResponseCreate(BaseModel):
    response_id: str
    survey_id: str
    customer_id: str
    response_text: str


class SurveyResponseOutput(SurveyResponseCreate):
    model_config = ConfigDict(from_attributes=True)
