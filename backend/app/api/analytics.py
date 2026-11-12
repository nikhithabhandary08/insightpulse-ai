
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

    # 1. Calculate overall sentiment analytics
    distribution, unclassified = get_sentiment_distribution(feedback)

    classified = sum(distribution.values())

    percentages = {
        sentiment: round(count / classified * 100, 2)
        if classified else 0
        for sentiment, count in distribution.items()
    }

    # 2. Calculate theme-wise sentiment analytics
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
            "positive_percentage": round(
                counts["positive"] / total * 100, 2
            ) if total else 0,
            "negative_percentage": round(
                counts["negative"] / total * 100, 2
            ) if total else 0
        })

    theme_analytics.sort(
        key=lambda item: item["feedback_count"],
        reverse=True
    )

    # 3. Identify highest positive and negative themes
    highest_negative_themes = []
    highest_positive_themes = []

    if theme_analytics:
        max_negative = max(
            item["negative_percentage"]
            for item in theme_analytics
        )

        max_positive = max(
            item["positive_percentage"]
            for item in theme_analytics
        )

        highest_negative_themes = [
            item["theme"]
            for item in theme_analytics
            if item["negative_percentage"] == max_negative
        ]

        highest_positive_themes = [
            item["theme"]
            for item in theme_analytics
            if item["positive_percentage"] == max_positive
        ]

    # 4. Build the verified report using Python
    verified_findings = [
        "OVERALL CUSTOMER FEEDBACK SUMMARY",
        f"Total feedback analyzed: {len(feedback)}",
        f"Classified feedback: {classified}",
        f"Unclassified feedback: {unclassified}",
        "",
        "SENTIMENT DISTRIBUTION"
    ]

    for sentiment in SENTIMENTS:
        verified_findings.append(
            f"{sentiment.capitalize()}: "
            f"{distribution.get(sentiment, 0)} "
            f"({percentages.get(sentiment, 0)}%)"
        )

    verified_findings.extend([
        "",
        "THEME-WISE ANALYSIS"
    ])

    for item in theme_analytics:
        verified_findings.append(
            f"{item['theme']}: "
            f"{item['feedback_count']} feedback records, "
            f"{item['positive_percentage']}% positive, "
            f"{item['negative_percentage']}% negative."
        )

    verified_findings.extend([
        "",
        "HIGHEST POSITIVE SENTIMENT",
        ", ".join(highest_positive_themes)
        if highest_positive_themes else "Not available",
        "",
        "HIGHEST NEGATIVE SENTIMENT",
        ", ".join(highest_negative_themes)
        if highest_negative_themes else "Not available",
        "",
        "DATA LIMITATION",
        "This is synthetic customer feedback generated for "
        "application testing and evaluation. It may not "
        "represent real customer behaviour."
    ])

    verified_report = "\n".join(verified_findings)

    # 5. Ask Llama to generate recommendations only
    prompt = f"""
You are a professional customer feedback intelligence analyst.

VERIFIED DATA:
{json.dumps({
    "total_feedback": len(feedback),
    "classified_feedback": classified,
    "unclassified_feedback": unclassified,
    "sentiment_distribution": distribution,
    "sentiment_percentages": percentages,
    "theme_analytics": theme_analytics,
    "highest_positive_themes": highest_positive_themes,
    "highest_negative_themes": highest_negative_themes
}, indent=2)}

TASK:
Provide concise, practical recommendations for investigating
and improving customer feedback themes.

RULES:
- This dataset is synthetic.
- Do not invent customer complaints or experiences.
- Do not assume causes such as errors, delays, or staff issues.
- Do not present possible causes as observed facts.
- Do not claim one theme has the highest negative sentiment
  when multiple themes are tied.
- Do not repeat the supplied statistics.
- Do not repeat the same recommendation.
- Do not invent business outcomes.
- Frame recommendations as actions to investigate or evaluate.
- Include recommendations for Performance, Customer Support,
  and Feature Request.
- Keep the response professional and concise.

Return only:
1. Areas to investigate
2. Recommended actions
3. Suggested follow-up measurements
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

    # 6. Combine verified findings and AI recommendations
    final_report = (
        verified_report
        + "\n\nACTIONABLE BUSINESS RECOMMENDATIONS\n"
        + ai_response
    )

    return {
        "total_feedback_analyzed": len(feedback),
        "classified_feedback": classified,
        "unclassified_feedback": unclassified,
        "sentiment_distribution": distribution,
        "sentiment_percentages": percentages,
        "theme_analytics": theme_analytics,
        "highest_positive_themes": highest_positive_themes,
        "highest_negative_themes": highest_negative_themes,
        "ai_insights": final_report
    }
