import httpx

from app.config import settings


class GitLabError(RuntimeError):
    pass


def _headers() -> dict:
    if not settings.gitlab_token:
        raise GitLabError("GitLab is not configured on this server.")
    return {"PRIVATE-TOKEN": settings.gitlab_token}


async def get_mr_changes(project_id: str, mr_iid: str) -> dict:
    url = f"{settings.gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/changes"
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=_headers())
        if response.is_error:
            raise GitLabError(f"GitLab API error: {response.status_code} {response.text}")
        return response.json()


async def post_discussion(
    project_id: str,
    mr_iid: str,
    body: str,
    old_path: str,
    new_path: str,
    start_sha: str,
    head_sha: str,
    base_sha: str,
    old_line: int | None,
    new_line: int | None,
) -> None:
    url = f"{settings.gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/discussions"
    data = {
        "body": body,
        "position[position_type]": "text",
        "position[old_path]": old_path,
        "position[new_path]": new_path,
        "position[start_sha]": start_sha,
        "position[head_sha]": head_sha,
        "position[base_sha]": base_sha,
    }
    if new_line is not None:
        data["position[new_line]"] = str(new_line)
    if old_line is not None:
        data["position[old_line]"] = str(old_line)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, data=data, headers=_headers())
        if response.is_error:
            raise GitLabError(f"GitLab API error posting discussion: {response.status_code} {response.text}")
