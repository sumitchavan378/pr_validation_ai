"""Optional GitHub Check Runs for PR head commit."""

from __future__ import annotations

from typing import Any

from app.github.client import GitHubClient, GitHubAPIError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_check_run(
    client: GitHubClient,
    owner: str,
    repo: str,
    head_sha: str,
    name: str,
    *,
    conclusion: str,
    title: str,
    summary: str,
    text: str | None = None,
) -> dict[str, Any] | None:
    """
    Create a completed check run.

    conclusion: success | failure | neutral
    """
    payload: dict[str, Any] = {
        "name": name,
        "head_sha": head_sha,
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": title,
            "summary": summary,
            "text": text or "",
        },
    }
    try:
        return client.post_json(f"/repos/{owner}/{repo}/check-runs", payload)
    except GitHubAPIError as exc:
        logger.warning(
            "check_run_failed",
            extra={"component": "check_run", "error_detail": str(exc), "status": exc.status_code},
        )
        return None
