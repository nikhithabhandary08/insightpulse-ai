
import json
import requests

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.dependencies import get_db
from app.models.review import Review
from app.models.theme import Theme
from app.models.product import Product
from app.services.llm_service import generate_insights


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


@router.get("/ai-insights")
def get_ai_insights(db: Session = Depends(get_db)):
    total_reviews = db.query(Review).count()

    if total_reviews == 0:
        raise HTTPException(
            status_code=404,
            detail="No customer feedback is available for analysis."
        )

    # Calculate sentiment distribution
    sentiment_counts = (
        db.query(
            Review.sentiment,
            func.count(Review.review_id)
        )
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

    classified_reviews = sum(sentiment_distribution.values())
    unclassified_reviews = total_reviews - classified_reviews

    sentiment_percentages = {
        sentiment: round(count / classified_reviews * 100, 2)
        if classified_reviews else 0
        for sentiment, count in sentiment_distribution.items()
    }

    # Calculate sentiment counts for each theme
    theme_results = (
        db.query(
            Theme.theme_name,
            Review.sentiment,
            func.count(Review.review_id)
        )
        .join(Review, Theme.theme_id == Review.theme_id)
        .filter(Review.sentiment.isnot(None))
        .group_by(Theme.theme_name, Review.sentiment)
        .all()
    )

    theme_analytics = {}

    for theme_name, sentiment, count in theme_results:
        if theme_name not in theme_analytics:
            theme_analytics[theme_name] = {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }

        if sentiment in theme_analytics[theme_name]:
            theme_analytics[theme_name][sentiment] = count

    for theme_name, counts in theme_analytics.items():
        theme_total = sum(counts.values())

        counts["total_reviews"] = theme_total
        counts["negative_percentage"] = round(
            counts["negative"] / theme_total * 100, 2
        ) if theme_total else 0

    # Top themes by review volume
    top_themes = sorted(
        [
            {"theme": name, **counts}
            for name, counts in theme_analytics.items()
        ],
        key=lambda item: item["total_reviews"],
        reverse=True
    )[:8]

    # Themes with the most negative reviews
    negative_themes = sorted(
        [
            {"theme": name, **counts}
            for name, counts in theme_analytics.items()
            if counts["negative"] > 0
        ],
        key=lambda item: item["negative"],
        reverse=True
    )[:8]

    # Top product categories
    category_results = (
        db.query(
            Product.category,
            func.count(Review.review_id).label("review_count")
        )
        .join(Review, Product.product_id == Review.product_id)
        .group_by(Product.category)
        .order_by(func.count(Review.review_id).desc())
        .limit(5)
        .all()
    )

    top_categories = [
        {
            "category": category,
            "review_count": count
        }
        for category, count in category_results
    ]

    # Prepare factual statistics for Llama
    prompt = f"""
You are a professional customer feedback intelligence analyst.

Analyze these database statistics.

TOTAL REVIEWS: {total_reviews}

CLASSIFIED REVIEWS: {classified_reviews}

UNCLASSIFIED REVIEWS: {unclassified_reviews}

SENTIMENT COUNTS:
{json.dumps(sentiment_distribution)}

SENTIMENT PERCENTAGES:
{json.dumps(sentiment_percentages)}

TOP THEMES:
{json.dumps(top_themes)}

THEMES WITH MOST NEGATIVE REVIEWS:
{json.dumps(negative_themes)}

TOP PRODUCT CATEGORIES:
{json.dumps(top_categories)}

Write a concise business intelligence report with:

1. Overall Customer Feedback Summary
2. Positive Feedback Highlights
3. Major Customer Concerns
4. Actionable Business Recommendations

IMPORTANT:
- Use the supplied statistics only.
- Do not recalculate sentiment percentages.
- Theme totals are not positive review counts.
- Use separate positive, negative and neutral counts.
- Theme labels are automatically generated keywords,
  not confirmed explanations of customer problems.
- Do not invent causes or customer experiences.
- Distinguish observed facts from possible explanations.
- State limitations where evidence is insufficient.
"""

    try:
        ai_response = generate_insights(prompt)

        if not ai_response:
            raise HTTPException(
                status_code=503,
                detail="The AI model returned an empty response."
            )

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to Ollama. Ensure Ollama is running."
        )

    return {
        "total_reviews_analyzed": total_reviews,
        "classified_reviews": classified_reviews,
        "unclassified_reviews": unclassified_reviews,
        "sentiment_distribution": sentiment_distribution,
        "sentiment_percentages": sentiment_percentages,
        "top_themes": top_themes,
        "negative_themes": negative_themes,
        "top_categories": top_categories,
        "ai_insights": ai_response
    }
