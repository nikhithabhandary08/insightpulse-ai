from collections import defaultdict
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.action_item import ActionItem
from app.models.action_item_feedback import ActionItemFeedback
from app.models.review import Review
from app.models.survey_response import SurveyResponse
from app.models.support_message import SupportMessage
from app.models.theme import Theme


NEGATIVE_THRESHOLD = 15.0


def generate_action_items(db: Session):
    """
    Generate ActionItems automatically when negative feedback
    for a theme exceeds the configured threshold.

    Feedback sources:
    - Reviews
    - Survey responses
    - Support messages
    """

    grouped_feedback = defaultdict(list)

    # Collect reviews
    for item in db.query(Review).all():
        grouped_feedback[item.theme_id].append({
            "source_type": "Review",
            "source_id": item.review_id,
            "sentiment": (item.sentiment or "").lower()
        })

    # Collect survey responses
    for item in db.query(SurveyResponse).all():
        grouped_feedback[item.theme_id].append({
            "source_type": "SurveyResponse",
            "source_id": item.response_id,
            "sentiment": (item.sentiment or "").lower()
        })

    # Collect support messages
    for item in db.query(SupportMessage).all():
        grouped_feedback[item.theme_id].append({
            "source_type": "SupportMessage",
            "source_id": item.message_id,
            "sentiment": (item.sentiment or "").lower()
        })

    themes = {
        theme.theme_id: theme.theme_name
        for theme in db.query(Theme).all()
    }

    created_actions = []
    skipped_actions = []

    for theme_id, records in grouped_feedback.items():

        if not theme_id or theme_id not in themes:
            continue

        total_count = len(records)

        negative_records = [
            record for record in records
            if record["sentiment"] == "negative"
        ]

        negative_count = len(negative_records)

        if total_count == 0:
            continue

        negative_percentage = round(
            (negative_count / total_count) * 100,
            2
        )

        if negative_percentage <= NEGATIVE_THRESHOLD:
            continue

        # Avoid duplicate automatic actions for the same theme.
        existing_action = (
            db.query(ActionItem)
            .filter(
                ActionItem.theme_id == theme_id,
                ActionItem.action_title.like("Automatic: %")
            )
            .first()
        )

        if existing_action:
            # Keep existing action and add any missing source mappings.
            existing_mappings = {
                (mapping.source_type, mapping.source_id)
                for mapping in db.query(ActionItemFeedback)
                .filter(
                    ActionItemFeedback.action_id
                    == existing_action.action_id
                )
                .all()
            }

            for record in records:
                source_key = (
                    record["source_type"],
                    record["source_id"]
                )

                if source_key not in existing_mappings:
                    db.add(ActionItemFeedback(
                        mapping_id=f"MAP-{uuid4().hex[:20]}",
                        action_id=existing_action.action_id,
                        source_type=record["source_type"],
                        source_id=record["source_id"]
                    ))

            existing_action.source_count = total_count
            existing_action.negative_percentage = negative_percentage
            existing_action.threshold_percentage = NEGATIVE_THRESHOLD

            skipped_actions.append(existing_action.action_id)
            continue

        # Determine priority using measured negative percentage.
        if negative_percentage >= 40:
            priority = "Critical"
        elif negative_percentage >= 30:
            priority = "High"
        else:
            priority = "Medium"

        theme_name = themes[theme_id]

        action = ActionItem(
            action_id=f"ACT-AUTO-{uuid4().hex[:12].upper()}",
            theme_id=theme_id,
            action_title=f"Automatic: Improve {theme_name}",
            description=(
                f"{negative_count} out of {total_count} feedback records "
                f"({negative_percentage}%) for {theme_name} are negative. "
                f"This exceeds the configured threshold of "
                f"{NEGATIVE_THRESHOLD}%. Investigate the linked feedback "
                f"records and define corrective actions."
            ),
            priority=priority,
            status="Open",
            source_count=total_count,
            negative_percentage=negative_percentage,
            threshold_percentage=NEGATIVE_THRESHOLD
        )

        db.add(action)
        db.flush()

        # Link all supporting source records.
        for record in records:
            db.add(ActionItemFeedback(
                mapping_id=f"MAP-{uuid4().hex[:20]}",
                action_id=action.action_id,
                source_type=record["source_type"],
                source_id=record["source_id"]
            ))

        created_actions.append(action.action_id)

    db.commit()

    return {
        "threshold_percentage": NEGATIVE_THRESHOLD,
        "actions_created": len(created_actions),
        "created_action_ids": created_actions,
        "existing_actions_updated": len(skipped_actions),
        "updated_action_ids": skipped_actions
    }