from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import sync_schema
from app.routers import reviews, settings_router, webhook

app = FastAPI(title="Review Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings_router.router)
app.include_router(reviews.router)
app.include_router(webhook.router)


@app.on_event("startup")
def on_startup():
    sync_schema()


@app.get("/api/health")
def health():
    return {"status": "ok"}
