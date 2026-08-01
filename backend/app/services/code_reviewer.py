import json
import re

from app.config import settings
from app.services.llm_client import get_client

SYSTEM_PROMPT = (
    "You are a senior software engineer reviewing a single code change from a merge "
    "request. Be direct and specific — point out real problems (bugs, security issues, "
    "poor naming, missing error handling, unnecessary complexity), not style nitpicks "
    "unless they matter. If the change is genuinely fine, say so briefly instead of "
    "inventing issues.\n\n"
    "Respond with ONLY valid JSON, no markdown fences, no extra text, in exactly this "
    "shape:\n"
    '{"verdict": "accept" or "reject", "score": 0-100, "review_markdown": "the review '
    'body in Markdown — start with a one-line verdict summary, then bullet points for '
    'each issue found, with a suggested fix if useful"}'
)


def _strip_code_fence(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def review_code_change(file_path: str, original_code: str, new_code: str) -> dict:
    client = get_client()

    user_message = (
        f"File path: {file_path}\n\n"
        f"Original code:\n```\n{original_code}\n```\n\n"
        f"New code:\n```\n{new_code}\n```\n\n"
        "Please review this code change."
    )

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=1536,
    )
    raw = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(_strip_code_fence(raw))
        verdict = parsed.get("verdict", "reject")
        score = int(parsed.get("score", 0))
        return {
            "verdict": verdict if verdict in ("accept", "reject") else "reject",
            "score": max(0, min(100, score)),
            "review_markdown": parsed.get("review_markdown", raw),
        }
    except (json.JSONDecodeError, AttributeError, ValueError, TypeError):
        return {"verdict": "reject", "score": 0, "review_markdown": raw}
