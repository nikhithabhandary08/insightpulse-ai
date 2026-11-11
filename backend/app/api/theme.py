
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.theme import Theme
from app.schemas.theme import ThemeCreate, ThemeResponse

router = APIRouter(
    prefix="/themes",
    tags=["Themes"]
)


@router.post("/", response_model=ThemeResponse)
def create_theme(
    theme: ThemeCreate,
    db: Session = Depends(get_db)
):
    existing_theme = db.query(Theme).filter(
        Theme.theme_id == theme.theme_id
    ).first()

    if existing_theme:
        raise HTTPException(
            status_code=400,
            detail="Theme ID already exists"
        )

    existing_name = db.query(Theme).filter(
        Theme.theme_name == theme.theme_name
    ).first()

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="Theme name already exists"
        )

    db_theme = Theme(**theme.model_dump())

    db.add(db_theme)
    db.commit()
    db.refresh(db_theme)

    return db_theme


@router.get("/", response_model=list[ThemeResponse])
def get_themes(db: Session = Depends(get_db)):
    return db.query(Theme).all()
