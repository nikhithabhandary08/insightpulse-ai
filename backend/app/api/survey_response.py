
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.survey_response import SurveyResponse
from app.schemas.survey_response import (
    SurveyResponseCreate,
    SurveyResponseOutput
)

router = APIRouter(
    prefix="/survey-responses",
    tags=["Survey Responses"]
)


@router.post("/", response_model=SurveyResponseOutput)
def create_survey_response(
    response: SurveyResponseCreate,
    db: Session = Depends(get_db)
):
    existing_response = db.query(SurveyResponse).filter(
        SurveyResponse.response_id == response.response_id
    ).first()

    if existing_response:
        raise HTTPException(
            status_code=400,
            detail="Response ID already exists"
        )

    db_response = SurveyResponse(**response.model_dump())

    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    return db_response


@router.get("/", response_model=list[SurveyResponseOutput])
def get_survey_responses(
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500)
):
    return (
        db.query(SurveyResponse)
        .order_by(SurveyResponse.response_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
