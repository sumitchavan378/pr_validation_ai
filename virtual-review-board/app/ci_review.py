"""Entry point for GitHub Actions: run review from GITHUB_EVENT_PATH."""

from __future__ import annotations

import json
import os
import sys

from app.config import Settings, get_settings
from app.github.pr_events import ALLOWED_ACTIONS
from app.review_pipeline import execute_pr_review
from app.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


def _load_event() -> dict:
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path:
        raise SystemExit("GITHUB_EVENT_PATH is not set (are you running inside GitHub Actions?)")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    settings = get_settings()
    setup_logging(settings.log_level)

    event = _load_event()
    action = event.get("action")
    if action not in ALLOWED_ACTIONS:
        logger.info("ci_skip_action", extra={"component": "ci_review", "action": action})
        return 0

    pr = event.get("pull_request")
    if not isinstance(pr, dict):
        logger.warning("ci_no_pull_request", extra={"component": "ci_review"})
        return 0

    repo_full = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in repo_full:
        raise SystemExit("GITHUB_REPOSITORY must be owner/repo")
    owner, repo = repo_full.split("/", 1)
    number = pr.get("number")
    head_sha = (pr.get("head") or {}).get("sha")
    if not isinstance(number, int) or not head_sha:
        raise SystemExit("pull_request payload missing number or head.sha")

    logger.info(
        "ci_review_start",
        extra={
            "component": "ci_review",
            "repo": repo_full,
            "pr_number": number,
            "action": action,
        },
    )
    execute_pr_review(owner, repo, number, head_sha, settings)
    logger.info(
        "ci_review_done",
        extra={"component": "ci_review", "repo": repo_full, "pr_number": number},
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as e:
        raise e
    except Exception as exc:  # noqa: BLE001
        logger.exception("ci_review_fatal", extra={"component": "ci_review", "message": str(exc)})
        raise SystemExit(1) from exc
