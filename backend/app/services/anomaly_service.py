
import re
import json
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.survey_response import SurveyResponse
from app.models.support_message import SupportMessage
from app.models.anomaly_record import AnomalyRecord
from app.models.theme import Theme


# Approved theme taxonomy
ALLOWED_THEMES = {
    "Performance",
    "Customer Support",
    "Feature Request",
}

# PII detection patterns
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)


def detect_pii(text):
    """Detect email addresses and Indian mobile numbers."""

    if not text:
        return []

    findings = []

    if EMAIL_PATTERN.search(text):
        findings.append("Email address detected")

    if PHONE_PATTERN.search(text):
        findings.append("Phone number detected")

    return findings


def detect_rating_mismatch(rating, text):
    """Identify obvious contradictions between rating and review text."""

    if not text or rating is None:
        return False

    normalized_text = text.lower()

    negative_words = [
        "terrible",
        "worst",
        "bad",
        "poor",
        "useless",
        "disappointed",
        "awful",
        "horrible",
        "not working",
        "very slow",
    ]

    positive_words = [
        "excellent",
        "amazing",
        "excellent service",
        "love it",
        "very good",
        "perfect",
        "wonderful",
        "fantastic",
        "great experience",
    ]

    has_negative = any(
        word in normalized_text for word in negative_words
    )

    has_positive = any(
        word in normalized_text for word in positive_words
    )

    if rating >= 4 and has_negative:
        return True

    if rating <= 2 and has_positive:
        return True

    return False

def detect_sentiment_mismatch(sentiment, text):
    """Identify obvious contradictions between sentiment and review text."""

    if not text or not sentiment:
        return False

    normalized_text = text.lower()
    normalized_sentiment = sentiment.strip().lower()

    negative_words = [
        "terrible",
        "worst",
        "bad",
        "poor",
        "useless",
        "disappointed",
        "awful",
        "horrible",
        "not working",
        "very slow",
        "keeps crashing",
    ]

    positive_words = [
        "excellent",
        "amazing",
        "excellent service",
        "love it",
        "very good",
        "perfect",
        "wonderful",
        "fantastic",
        "great experience",
    ]

    has_negative = any(
        word in normalized_text for word in negative_words
    )

    has_positive = any(
        word in normalized_text for word in positive_words
    )

    if normalized_sentiment == "positive" and has_negative:
        return True

    if normalized_sentiment == "negative" and has_positive:
        return True

    return False

def create_anomaly(
    db,
    anomaly_id,
    source_type,
    source_id,
    anomaly_type,
    severity,
    description,
    details=None,
):
    """Insert an anomaly only if it does not already exist."""

    existing = db.query(AnomalyRecord).filter(
        AnomalyRecord.anomaly_id == anomaly_id
    ).first()

    if existing:
        return False

    record = AnomalyRecord(
        anomaly_id=anomaly_id,
        source_type=source_type,
        source_id=source_id,
        anomaly_type=anomaly_type,
        severity=severity,
        description=description,
        details=details,
        status="Open",
    )

    db.add(record)
    return True



def run_anomaly_detection(db: Session):
    """
    Scan reviews, survey responses and support messages.
    Store detected anomalies in anomaly_records.
    """

    detected = defaultdict(int)

    themes = {
        theme.theme_name
        for theme in db.query(Theme).all()
    }

    allowed_themes = ALLOWED_THEMES.intersection(themes)

    # -------------------------------------------------
    # 1. Review checks
    # -------------------------------------------------

    reviews = db.query(Review).all()

    for review in reviews:
        text = review.review_text or ""
        source_id = review.review_id

        # PII detection
        pii_findings = detect_pii(text)

        if pii_findings:
            if create_anomaly(
                db,
                f"ANOM-REV-PII-{source_id}",
                "Review",
                source_id,
                "PII_LEAK",
                "High",
                "Possible personal information found in review text.",
                json.dumps(pii_findings),
            ):
                detected["PII_LEAK"] += 1

        # Invalid predicted theme
        predicted_theme = review.predicted_theme

        if (
            predicted_theme
            and predicted_theme not in allowed_themes
        ):
            if create_anomaly(
                db,
                f"ANOM-REV-THEME-{source_id}",
                "Review",
                source_id,
                "INVALID_THEME",
                "Medium",
                "Predicted theme is outside the approved taxonomy.",
                str(predicted_theme),
            ):
                detected["INVALID_THEME"] += 1

        # Rating-text mismatch
        if detect_rating_mismatch(review.rating, text):
            if create_anomaly(
                db,
                f"ANOM-REV-RATING-{source_id}",
                "Review",
                source_id,
                "RATING_TEXT_MISMATCH",
                "Medium",
                "Review rating appears inconsistent with its text.",
                f"Rating: {review.rating}",
            ):
                detected["RATING_TEXT_MISMATCH"] += 1

        # Sentiment-text mismatch
        if detect_sentiment_mismatch(review.sentiment, text):
            if create_anomaly(
                db,
                f"ANOM-REV-SENTIMENT-{source_id}",
                "Review",
                source_id,
                "SENTIMENT_TEXT_MISMATCH",
                "Medium",
                "Review sentiment appears inconsistent with its text.",
                f"Stored sentiment: {review.sentiment}",
            ):
                detected["SENTIMENT_TEXT_MISMATCH"] += 1

    # -------------------------------------------------
    # 2. Survey response checks
    # -------------------------------------------------

    responses = db.query(SurveyResponse).all()

    duplicate_groups = defaultdict(list)

    for response in responses:
        text = response.response_text or ""
        source_id = response.response_id

        # PII detection
        pii_findings = detect_pii(text)

        if pii_findings:
            if create_anomaly(
                db,
                f"ANOM-RESP-PII-{source_id}",
                "SurveyResponse",
                source_id,
                "PII_LEAK",
                "High",
                "Possible personal information found in survey response.",
                json.dumps(pii_findings),
            ):
                detected["PII_LEAK"] += 1

        # Invalid predicted theme
        predicted_theme = response.predicted_theme

        if (
            predicted_theme
            and predicted_theme not in allowed_themes
        ):
            if create_anomaly(
                db,
                f"ANOM-RESP-THEME-{source_id}",
                "SurveyResponse",
                source_id,
                "INVALID_THEME",
                "Medium",
                "Predicted theme is outside the approved taxonomy.",
                str(predicted_theme),
            ):
                detected["INVALID_THEME"] += 1

        # Group possible duplicate submissions
        normalized_text = " ".join(text.lower().split())

        duplicate_key = (
            response.survey_id,
            response.customer_id,
            response.product_id,
            normalized_text,
        )

        duplicate_groups[duplicate_key].append(response)

    # Flag all records after the first in a duplicate group
    for group in duplicate_groups.values():
        if len(group) > 1:
            for duplicate in group[1:]:
                if create_anomaly(
                    db,
                    f"ANOM-RESP-DUP-{duplicate.response_id}",
                    "SurveyResponse",
                    duplicate.response_id,
                    "DUPLICATE_SUBMISSION",
                    "Medium",
                    "Possible duplicate survey submission detected.",
                    f"Survey ID: {duplicate.survey_id}",
                ):
                    detected["DUPLICATE_SUBMISSION"] += 1

    # -------------------------------------------------
    # 3. Support message checks
    # -------------------------------------------------

    messages = db.query(SupportMessage).all()

    for message in messages:
        text = message.message_text or ""
        source_id = message.message_id

        # PII detection
        pii_findings = detect_pii(text)

        if pii_findings:
            if create_anomaly(
                db,
                f"ANOM-MSG-PII-{source_id}",
                "SupportMessage",
                source_id,
                "PII_LEAK",
                "High",
                "Possible personal information found in support message.",
                json.dumps(pii_findings),
            ):
                detected["PII_LEAK"] += 1

        # Invalid predicted theme
        predicted_theme = message.predicted_theme

        if (
            predicted_theme
            and predicted_theme not in allowed_themes
        ):
            if create_anomaly(
                db,
                f"ANOM-MSG-THEME-{source_id}",
                "SupportMessage",
                source_id,
                "INVALID_THEME",
                "Medium",
                "Predicted theme is outside the approved taxonomy.",
                str(predicted_theme),
            ):
                detected["INVALID_THEME"] += 1

    db.commit()

    total = sum(detected.values())

    return {
        "status": "completed",
        "records_scanned": (
            len(reviews) + len(responses) + len(messages)
        ),
        "anomalies_detected": total,
        "anomaly_breakdown": dict(detected),
    }
