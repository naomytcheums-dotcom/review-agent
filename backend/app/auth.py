import hmac

from fastapi import Header, HTTPException

from app.config import settings


def require_site_password(x_site_password: str = Header(default="")) -> None:
    if not settings.site_password:
        return
    if not hmac.compare_digest(x_site_password, settings.site_password):
        raise HTTPException(401, "Invalid or missing site password.")
