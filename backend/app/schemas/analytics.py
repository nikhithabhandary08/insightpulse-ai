
from pydantic import BaseModel


class SentimentSummary(BaseModel):
    positive: int
    negative: int
    neutral: int


class AnalyticsSummary(BaseModel):
    total_reviews: int
    sentiment: SentimentSummary
