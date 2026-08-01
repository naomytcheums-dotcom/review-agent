from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_site_password
from app.config import settings
from app.database import get_db
from app.models import ReviewSettings
from app.schemas import ConfigStatusOut, ReviewSettingsIn, ReviewSettingsOut

router = APIRouter(dependencies=[Depends(require_site_password)])


@router.get("/api/settings", response_model=ReviewSettingsOut)
def get_settings(db: Session = Depends(get_db)):
    review_settings = db.query(ReviewSettings).first()
    if not review_settings:
        review_settings = ReviewSettings()
        db.add(review_settings)
        db.commit()
        db.refresh(review_settings)
    return review_settings


@router.put("/api/settings", response_model=ReviewSettingsOut)
def upsert_settings(payload: ReviewSettingsIn, db: Session = Depends(get_db)):
    review_settings = db.query(ReviewSettings).first()
    if not review_settings:
        review_settings = ReviewSettings()
        db.add(review_settings)
    review_settings.trigger_phrase = payload.trigger_phrase
    db.commit()
    db.refresh(review_settings)
    return review_settings


@router.get("/api/config-status", response_model=ConfigStatusOut)
def config_status():
    return ConfigStatusOut(
        gitlab_configured=bool(settings.gitlab_token),
        gitlab_url=settings.gitlab_url,
        llm_configured=bool(settings.llm_api_key),
    )
