import asyncio

from sqlalchemy.orm import Session

from app.models import CodeReview
from app.services import gitlab_client
from app.services.code_reviewer import review_code_change
from app.services.diff_parser import parse_last_diff_line, split_diff_code
from app.services.gitlab_client import GitLabError


class ReviewError(RuntimeError):
    pass


def _eligible_changes(changes: dict) -> list[dict]:
    eligible = []
    for change in changes.get("changes", []):
        if change.get("renamed_file") or change.get("deleted_file"):
            continue
        diff = change.get("diff", "")
        if not diff.startswith("@@"):
            continue
        eligible.append(change)
    return eligible


async def analyze_mr(db: Session, project_id: str, mr_iid: str, triggered_by: str = "manual") -> dict:
    try:
        changes = await gitlab_client.get_mr_changes(project_id, mr_iid)
    except GitLabError as exc:
        raise ReviewError(str(exc)) from exc

    diff_refs = changes.get("diff_refs", {})
    eligible = _eligible_changes(changes)

    created = []
    for change in eligible:
        diff = change["diff"]
        line_info = parse_last_diff_line(diff)
        split = split_diff_code(diff)

        try:
            result = await asyncio.to_thread(
                review_code_change, change.get("new_path", ""), split["original_code"], split["new_code"]
            )
            status, error_message = "draft", ""
        except Exception as exc:  # noqa: BLE001
            result = {"verdict": "", "score": 0, "review_markdown": ""}
            status, error_message = "failed", f"Error generating review: {exc}"

        review = CodeReview(
            project_id=project_id,
            mr_iid=mr_iid,
            old_path=change.get("old_path", ""),
            new_path=change.get("new_path", ""),
            diff_snippet=diff[:4000],
            start_sha=diff_refs.get("start_sha", ""),
            head_sha=diff_refs.get("head_sha", ""),
            base_sha=diff_refs.get("base_sha", ""),
            old_line=line_info["old_line"],
            new_line=line_info["new_line"],
            verdict=result["verdict"],
            score=result["score"],
            review_markdown=result["review_markdown"],
            status=status,
            error_message=error_message,
            triggered_by=triggered_by,
        )
        db.add(review)
        created.append(review)

    db.commit()
    for review in created:
        db.refresh(review)

    return {"files_found": len(eligible), "reviews_created": len(created), "reviews": created}


async def post_review(db: Session, review_id: int) -> CodeReview:
    review = db.get(CodeReview, review_id)
    if not review:
        raise ReviewError("Review not found.")
    if review.status == "posted":
        return review
    if review.status == "failed" and not review.review_markdown:
        raise ReviewError("This review failed to generate and has nothing to post.")

    try:
        await gitlab_client.post_discussion(
            review.project_id,
            review.mr_iid,
            body=review.review_markdown,
            old_path=review.old_path,
            new_path=review.new_path,
            start_sha=review.start_sha,
            head_sha=review.head_sha,
            base_sha=review.base_sha,
            old_line=review.old_line,
            new_line=review.new_line,
        )
        review.status = "posted"
        from datetime import datetime

        review.posted_at = datetime.utcnow()
    except GitLabError as exc:
        review.status = "failed"
        review.error_message = str(exc)

    db.commit()
    db.refresh(review)
    return review


async def analyze_and_post_all(db: Session, project_id: str, mr_iid: str) -> dict:
    """Used by the webhook path: the trigger comment itself is the human approval, so post immediately."""
    result = await analyze_mr(db, project_id, mr_iid, triggered_by="webhook")
    for review in result["reviews"]:
        if review.status == "draft":
            await post_review(db, review.id)
    return result
