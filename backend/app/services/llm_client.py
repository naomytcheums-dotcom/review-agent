from openai import OpenAI

from app.config import settings


def get_client() -> OpenAI:
    if not settings.llm_api_key:
        raise RuntimeError("LLM_API_KEY is not configured.")
    kwargs = {"api_key": settings.llm_api_key}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return OpenAI(**kwargs)
