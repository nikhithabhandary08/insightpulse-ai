from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyResponse

router = APIRouter(
    prefix="/surveys",
    tags=["Surveys"]
)


@router.post("/", response_model=SurveyResponse)
def create_survey(
    survey: SurveyCreate,
    db: Session = Depends(get_db)
):
    existing_survey = db.query(Survey).filter(
        Survey.survey_id == survey.survey_id
    ).first()

    if existing_survey:
        raise HTTPException(
            status_code=400,
            detail="Survey ID already exists"
        )

    db_survey = Survey(**survey.model_dump())

    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)

    return db_survey


@router.get("/", response_model=list[SurveyResponse])
def get_surveys(db: Session = Depends(get_db)):
    return db.query(Survey).all()