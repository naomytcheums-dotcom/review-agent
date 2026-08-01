from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_site_password
from app.database import get_db
from app.models import CodeReview
from app.schemas import AnalyzeIn, AnalyzeResult, CodeReviewOut
from app.services.review_runner import ReviewError, analyze_mr, post_review

router = APIRouter(prefix="/api/reviews", tags=["reviews"], dependencies=[Depends(require_site_password)])


@router.get("", response_model=list[CodeReviewOut])
def list_reviews(db: Session = Depends(get_db)):
    return db.query(CodeReview).order_by(CodeReview.created_at.desc()).limit(50).all()


@router.post("/analyze", response_model=AnalyzeResult)
async def analyze(payload: AnalyzeIn, db: Session = Depends(get_db)):
    try:
        result = await analyze_mr(db, payload.project_id, payload.mr_iid, triggered_by="manual")
    except ReviewError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Error analyzing merge request: {exc}") from exc
    return result


@router.post("/{review_id}/post", response_model=CodeReviewOut)
async def post(review_id: int, db: Session = Depends(get_db)):
    try:
        review = await post_review(db, review_id)
    except ReviewError as exc:
        raise HTTPException(400, str(exc)) from exc
    return review
