
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.action_item import ActionItem
from app.models.theme import Theme
from app.schemas.action_item import ActionItemCreate, ActionItemResponse


router = APIRouter(prefix="/action-items", tags=["Action Items"])


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


@router.get("/", response_model=list[ActionItemResponse])
def get_action_items(db: Session = Depends(get_db)):
    return (
        db.query(ActionItem)
        .order_by(ActionItem.created_at.desc())
        .all()
    )


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
