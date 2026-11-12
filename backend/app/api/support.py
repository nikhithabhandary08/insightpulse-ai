
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.support_message import SupportMessage
from app.schemas.support_message import (
    SupportMessageCreate,
    SupportMessageResponse
)

router = APIRouter(
    prefix="/support-messages",
    tags=["Support Messages"]
)


@router.post("/", response_model=SupportMessageResponse)
def create_support_message(
    message: SupportMessageCreate,
    db: Session = Depends(get_db)
):
    existing_message = db.query(SupportMessage).filter(
        SupportMessage.message_id == message.message_id
    ).first()

    if existing_message:
        raise HTTPException(
            status_code=400,
            detail="Message ID already exists"
        )

    db_message = SupportMessage(**message.model_dump())

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


@router.get("/", response_model=list[SupportMessageResponse])
def get_support_messages(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500)
):
    return (
        db.query(SupportMessage)
        .order_by(SupportMessage.message_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
