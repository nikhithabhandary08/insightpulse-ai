
import json
import requests

from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.dependencies import get_db
from app.models.review import Review
from app.models.survey_response import SurveyResponse
from app.models.support_message import SupportMessage
from app.models.theme import Theme
from app.models.product import Product
from app.services.llm_service import generate_insights


router = APIRouter(prefix="/analytics", tags=["Analytics"])

SENTIMENTS = ["positive", "neutral", "negative", "mixed"]


def get_all_feedback(db: Session):
    """Collect feedback from all three sources in a common format."""

    feedback = []

    reviews = db.query(Review).all()
    for item in reviews:
        feedback.append({
            "source_type": "Review",
            "source_id": item.review_id,
            "text": item.review_text,
            "sentiment": (item.sentiment or "").lower(),
            "theme_id": item.theme_id,
            "predicted_theme": item.predicted_theme,
            "product_id": item.product_id,
            "channel_id": item.channel_id,
            "created_at": item.created_at
        })

    responses = db.query(SurveyResponse).all()
    for item in responses:
        feedback.append({
            "source_type": "SurveyResponse",
            "source_id": item.response_id,
            "text": item.response_text,
            "sentiment": (item.sentiment or "").lower(),
            "theme_id": item.theme_id,
            "predicted_theme": item.predicted_theme,
            "product_id": item.product_id,
            "channel_id": item.channel_id,
            "created_at": item.submitted_at
        })

    messages = db.query(SupportMessage).all()
    for item in messages:
        feedback.append({
            "source_type": "SupportMessage",
            "source_id": item.message_id,
            "text": item.message_text,
            "sentiment": (item.sentiment or "").lower(),
            "theme_id": item.theme_id,
            "predicted_theme": item.predicted_theme,
            "product_id": None,
            "channel_id": item.channel_id,
            "created_at": item.created_at
        })

    return feedback


def get_sentiment_distribution(feedback):
    distribution = {sentiment: 0 for sentiment in SENTIMENTS}
    unclassified = 0

    for item in feedback:
        sentiment = item["sentiment"]

        if sentiment in distribution:
            distribution[sentiment] += 1
        else:
            unclassified += 1

    return distribution, unclassified


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    feedback = get_all_feedback(db)
    distribution, unclassified = get_sentiment_distribution(feedback)

    return {
        "total_feedback": len(feedback),
        "classified_feedback": sum(distribution.values()),
        "unclassified_feedback": unclassified,
        "sentiment_distribution": distribution
    }


@router.get("/themes")
def get_theme_analytics(db: Session = Depends(get_db)):
    feedback = get_all_feedback(db)
    theme_counts = defaultdict(int)

    themes = {
        theme.theme_id: theme.theme_name
        for theme in db.query(Theme).all()
    }

    for item in feedback:
        theme_id = item["theme_id"]
        if theme_id:
            theme_counts[theme_id] += 1

    results = [
        {
            "theme_id": theme_id,
            "theme_name": themes.get(theme_id, "Unknown"),
            "feedback_count": count
        }
        for theme_id, count in theme_counts.items()
    ]

    return sorted(
        results,
        key=lambda item: item["feedback_count"],
        reverse=True
    )


@router.get("/sentiment-by-theme")
def get_sentiment_by_theme(db: Session = Depends(get_db)):
    feedback = get_all_feedback(db)

    themes = {
        theme.theme_id: theme.theme_name
        for theme in db.query(Theme).all()
    }

    analytics = defaultdict(
        lambda: {sentiment: 0 for sentiment in SENTIMENTS}
    )

    for item in feedback:
        theme_id = item["theme_id"]
        sentiment = item["sentiment"]

        if theme_id and sentiment in SENTIMENTS:
            theme_name = themes.get(theme_id, "Unknown")
            analytics[theme_name][sentiment] += 1

    return dict(analytics)


@router.get("/product-categories")
def get_product_category_analytics(db: Session = Depends(get_db)):
    # Reviews and survey responses contain product IDs.
    # Support messages do not contain product IDs.

    category_counts = defaultdict(int)

    reviews = db.query(Review).all()
    responses = db.query(SurveyResponse).all()

    for item in reviews:
        product = db.query(Product).filter(
            Product.product_id == item.product_id
        ).first()

        if product:
            category_counts[product.category] += 1

    for item in responses:
        product = db.query(Product).filter(
            Product.product_id == item.product_id
        ).first()

        if product:
            category_counts[product.category] += 1

    return [
        {
            "category": category,
            "feedback_count": count
        }
        for category, count in sorted(
            category_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
    ]


@router.get("/sentiment-trends")
def get_sentiment_trends(
    period: str = Query(default="weekly", pattern="^(weekly|monthly)$"),
    db: Session = Depends(get_db)
):
    feedback = get_all_feedback(db)
    trends = defaultdict(
        lambda: {sentiment: 0 for sentiment in SENTIMENTS}
    )

    for item in feedback:
        created_at = item["created_at"]
        sentiment = item["sentiment"]

        if not created_at or sentiment not in SENTIMENTS:
            continue

        if period == "weekly":
            year, week, _ = created_at.isocalendar()
            period_key = f"{year}-W{week:02d}"
        else:
            period_key = created_at.strftime("%Y-%m")

        trends[period_key][sentiment] += 1

    return {
        "period": period,
        "trends": [
            {
                "date": key,
                **counts
            }
            for key, counts in sorted(trends.items())
        ]
    }


@router.get("/ai-insights")
def get_ai_insights(db: Session = Depends(get_db)):
    feedback = get_all_feedback(db)

    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="No customer feedback is available for analysis."
        )

    distribution, unclassified = get_sentiment_distribution(feedback)

    classified = sum(distribution.values())

    percentages = {
        sentiment: round(count / classified * 100, 2)
        if classified else 0
        for sentiment, count in distribution.items()
    }

    theme_results = get_theme_analytics(db)
    theme_sentiments = get_sentiment_by_theme(db)

    theme_analytics = []

    for theme in theme_results:
        counts = theme_sentiments.get(
            theme["theme_name"],
            {sentiment: 0 for sentiment in SENTIMENTS}
        )

        total = sum(counts.values())

        theme_analytics.append({
            "theme": theme["theme_name"],
            "feedback_count": total,
            "sentiment_counts": counts,
            "negative_percentage": round(
                counts["negative"] / total * 100, 2
            ) if total else 0
        })

    theme_analytics.sort(
        key=lambda item: item["feedback_count"],
        reverse=True
    )

    prompt = f"""
You are a professional customer feedback intelligence analyst.

Analyze these database statistics from reviews, survey responses,
and customer support messages.

TOTAL FEEDBACK: {len(feedback)}

CLASSIFIED FEEDBACK: {classified}

UNCLASSIFIED FEEDBACK: {unclassified}

SENTIMENT COUNTS:
{json.dumps(distribution)}

SENTIMENT PERCENTAGES:
{json.dumps(percentages)}

THEME ANALYTICS:
{json.dumps(theme_analytics[:8])}

Write a concise business intelligence report with:

1. Overall Customer Feedback Summary
2. Positive Feedback Highlights
3. Major Customer Concerns
4. Actionable Business Recommendations

IMPORTANT:
- Use only the supplied statistics.
- Do not invent causes or customer experiences.
- Distinguish observed facts from possible explanations.
- Include all four sentiment labels.
- Mention limitations where evidence is insufficient.
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
        "total_feedback_analyzed": len(feedback),
        "classified_feedback": classified,
        "unclassified_feedback": unclassified,
        "sentiment_distribution": distribution,
        "sentiment_percentages": percentages,
        "theme_analytics": theme_analytics,
        "ai_insights": ai_response
    }
