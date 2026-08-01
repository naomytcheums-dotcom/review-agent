from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewSettingsIn(BaseModel):
    trigger_phrase: str


class ReviewSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trigger_phrase: str
    updated_at: datetime


class AnalyzeIn(BaseModel):
    project_id: str
    mr_iid: str


class CodeReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: str
    mr_iid: str
    old_path: str
    new_path: str
    diff_snippet: str
    verdict: str
    score: int
    review_markdown: str
    status: str
    error_message: str
    triggered_by: str
    created_at: datetime
    posted_at: datetime | None


class AnalyzeResult(BaseModel):
    files_found: int
    reviews_created: int
    reviews: list[CodeReviewOut]


class ConfigStatusOut(BaseModel):
    gitlab_configured: bool
    gitlab_url: str
    llm_configured: bool
