
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.dependencies import get_db
from app.models.review import Review
from app.models.theme import Theme
from app.models.product import Product


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    total_reviews = db.query(Review).count()

    sentiment_counts = (
        db.query(Review.sentiment, func.count(Review.review_id))
        .group_by(Review.sentiment)
        .all()
    )

    sentiment_distribution = {
        "positive": 0,
        "negative": 0,
        "neutral": 0
    }

    for sentiment, count in sentiment_counts:
        if sentiment in sentiment_distribution:
            sentiment_distribution[sentiment] = count

    return {
        "total_reviews": total_reviews,
        "sentiment_distribution": sentiment_distribution
    }


@router.get("/themes")
def get_theme_analytics(db: Session = Depends(get_db)):
    results = (
        db.query(
            Theme.theme_id,
            Theme.theme_name,
            func.count(Review.review_id).label("feedback_count")
        )
        .outerjoin(Review, Theme.theme_id == Review.theme_id)
        .group_by(Theme.theme_id, Theme.theme_name)
        .order_by(func.count(Review.review_id).desc())
        .all()
    )

    return [
        {
            "theme_id": theme_id,
            "theme_name": theme_name,
            "feedback_count": feedback_count
        }
        for theme_id, theme_name, feedback_count in results
    ]


@router.get("/sentiment-by-theme")
def get_sentiment_by_theme(db: Session = Depends(get_db)):
    results = (
        db.query(
            Theme.theme_name,
            Review.sentiment,
            func.count(Review.review_id).label("feedback_count")
        )
        .join(Review, Theme.theme_id == Review.theme_id)
        .group_by(Theme.theme_name, Review.sentiment)
        .order_by(Theme.theme_name)
        .all()
    )

    analytics = {}

    for theme_name, sentiment, count in results:
        if theme_name not in analytics:
            analytics[theme_name] = {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }

        if sentiment in analytics[theme_name]:
            analytics[theme_name][sentiment] = count

    return analytics


@router.get("/product-categories")
def get_product_category_analytics(db: Session = Depends(get_db)):
    results = (
        db.query(
            Product.category,
            func.count(Review.review_id).label("review_count")
        )
        .join(Review, Product.product_id == Review.product_id)
        .group_by(Product.category)
        .order_by(func.count(Review.review_id).desc())
        .all()
    )

    return [
        {
            "category": category,
            "review_count": review_count
        }
        for category, review_count in results
    ]
