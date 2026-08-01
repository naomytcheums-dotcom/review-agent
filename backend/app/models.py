from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReviewSettings(Base):
    __tablename__ = "ra_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    trigger_phrase: Mapped[str] = mapped_column(String, default="/review")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CodeReview(Base):
    __tablename__ = "ra_reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[str] = mapped_column(String, default="")
    mr_iid: Mapped[str] = mapped_column(String, default="")
    old_path: Mapped[str] = mapped_column(String, default="")
    new_path: Mapped[str] = mapped_column(String, default="")
    diff_snippet: Mapped[str] = mapped_column(Text, default="")

    start_sha: Mapped[str] = mapped_column(String, default="")
    head_sha: Mapped[str] = mapped_column(String, default="")
    base_sha: Mapped[str] = mapped_column(String, default="")
    old_line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_line: Mapped[int | None] = mapped_column(Integer, nullable=True)

    verdict: Mapped[str] = mapped_column(String, default="")
    score: Mapped[int] = mapped_column(Integer, default=0)
    review_markdown: Mapped[str] = mapped_column(Text, default="")

    status: Mapped[str] = mapped_column(String, default="draft")
    error_message: Mapped[str] = mapped_column(Text, default="")
    triggered_by: Mapped[str] = mapped_column(String, default="manual")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
