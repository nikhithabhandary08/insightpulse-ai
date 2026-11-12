
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.action_item import ActionItem
from app.models.action_item_feedback import ActionItemFeedback
from app.models.theme import Theme
from app.models.review import Review
from app.models.survey_response import SurveyResponse
from app.models.support_message import SupportMessage
from app.schemas.action_item import ActionItemCreate, ActionItemResponse
from app.services.action_service import generate_action_items


router = APIRouter(prefix="/action-items", tags=["Action Items"])


def redact_pii(text: str) -> str:
    """Mask email addresses and phone numbers in displayed feedback."""

    if not text:
        return text

    # Mask email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED EMAIL]",
        text
    )

    # Mask Indian phone numbers
    text = re.sub(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        "[REDACTED PHONE]",
        text
    )

    return text


# Create a manual ActionItem
@router.post("/", response_model=ActionItemResponse, status_code=201)
def create_action_item(
    action_data: ActionItemCreate,
    db: Session = Depends(get_db)
):
    existing_action = db.query(ActionItem).filter(
        ActionItem.action_id == action_data.action_id
    ).first()

    if existing_action:
        raise HTTPException(
            status_code=409,
            detail="Action item ID already exists."
        )

    theme = db.query(Theme).filter(
        Theme.theme_id == action_data.theme_id
    ).first()

    if not theme:
        raise HTTPException(
            status_code=404,
            detail="Theme not found."
        )

    action_item = ActionItem(**action_data.model_dump())

    db.add(action_item)
    db.commit()
    db.refresh(action_item)

    return action_item


# Automatically generate ActionItems
@router.post("/generate")
def generate_automatic_action_items(
    db: Session = Depends(get_db)
):
    try:
        return generate_action_items(db)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="ActionItem generation failed."
        )


# Get all ActionItems
@router.get("/", response_model=list[ActionItemResponse])
def get_action_items(
    db: Session = Depends(get_db)
):
    return (
        db.query(ActionItem)
        .order_by(ActionItem.created_at.desc())
        .all()
    )


# Get feedback sources linked to an ActionItem
@router.get("/{action_id}/sources")
def get_action_item_sources(
    action_id: str,
    db: Session = Depends(get_db)
):
    action = db.query(ActionItem).filter(
        ActionItem.action_id == action_id
    ).first()

    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action item not found."
        )

    mappings = (
        db.query(ActionItemFeedback)
        .filter(
            ActionItemFeedback.action_id == action_id
        )
        .order_by(ActionItemFeedback.source_id)
        .all()
    )

    source_models = {
        "Review": (Review, "review_id", "review_text", "created_at"),
        "SurveyResponse": (
            SurveyResponse,
            "response_id",
            "response_text",
            "submitted_at"
        ),
        "SupportMessage": (
            SupportMessage,
            "message_id",
            "message_text",
            "created_at"
        )
    }

    sources = []

    for mapping in mappings:
        source_config = source_models.get(mapping.source_type)

        if not source_config:
            continue

        model, id_field, text_field, date_field = source_config

        source_record = (
            db.query(model)
            .filter(
                getattr(model, id_field) == mapping.source_id
            )
            .first()
        )

        if not source_record:
            continue

        original_text = getattr(source_record, text_field)

        sources.append({
            "source_type": mapping.source_type,
            "source_id": mapping.source_id,
            "feedback_text": redact_pii(original_text),
            "sentiment": source_record.sentiment,
            "created_at": getattr(source_record, date_field)
        })

    return {
        "action_id": action.action_id,
        "action_title": action.action_title,
        "source_count": len(sources),
        "sources": sources
    }


# Get an ActionItem by ID
@router.get("/{action_id}", response_model=ActionItemResponse)
def get_action_item(
    action_id: str,
    db: Session = Depends(get_db)
):
    action_item = db.query(ActionItem).filter(
        ActionItem.action_id == action_id
    ).first()

    if not action_item:
        raise HTTPException(
            status_code=404,
            detail="Action item not found."
        )

    return action_item
