
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.sentiment_service import predict_feedback_sentiment

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db)
):
    existing_review = db.query(Review).filter(
        Review.review_id == review.review_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Review ID already exists"
        )

    try:
        sentiment_result = predict_feedback_sentiment(
            review.review_text
        )
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    db_review = Review(
        **review.model_dump(),
        sentiment=sentiment_result["sentiment"],
        sentiment_confidence=sentiment_result["confidence"]
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return db_review


@router.get("/", response_model=list[ReviewResponse])
def get_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()
