from fastapi import APIRouter, BackgroundTasks, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ReviewSettings
from app.services.review_runner import analyze_and_post_all

router = APIRouter(prefix="/api/webhook", tags=["webhook"])


async def _handle_note_event(project_id: str, mr_iid: str) -> None:
    db: Session = SessionLocal()
    try:
        await analyze_and_post_all(db, project_id, mr_iid)
    finally:
        db.close()


@router.post("/gitlab")
async def gitlab_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    attrs = payload.get("object_attributes", {})
    note = attrs.get("note", "")
    project_id = payload.get("project_id")
    mr_iid = payload.get("merge_request", {}).get("iid")

    if not project_id or not mr_iid:
        return {"status": "ignored", "reason": "not a merge request note event"}

    db = SessionLocal()
    try:
        review_settings = db.query(ReviewSettings).first()
        trigger_phrase = review_settings.trigger_phrase if review_settings else "/review"
    finally:
        db.close()

    if note.strip() != trigger_phrase:
        return {"status": "ignored", "reason": "note did not match trigger phrase"}

    background_tasks.add_task(_handle_note_event, str(project_id), str(mr_iid))
    return {"status": "queued"}
