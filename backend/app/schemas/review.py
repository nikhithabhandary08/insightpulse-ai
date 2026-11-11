from pydantic import BaseModel, ConfigDict
from typing import Optional


class ReviewCreate(BaseModel):
    review_id: str
    customer_id: str
    product_id: str
    channel_id: str
    review_text: str
    theme_id: Optional[str] = None


class ReviewResponse(ReviewCreate):
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)