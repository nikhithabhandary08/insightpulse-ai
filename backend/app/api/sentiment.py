
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.sentiment_service import predict_feedback_sentiment


router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"]
)


class SentimentRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Customer feedback text"
    )


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float


@router.post("/predict", response_model=SentimentResponse)
def predict_sentiment(request: SentimentRequest):

    try:
        result = predict_feedback_sentiment(request.text)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
