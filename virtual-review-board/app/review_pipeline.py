"""Shared PR review execution (webhook server and GitHub Actions)."""

from __future__ import annotations

from app.config import Settings
from app.crew.crew_runner import run_virtual_review_board
from app.github.check_run import create_check_run
from app.github.client import GitHubClient, GitHubAPIError
from app.github.comment_poster import post_pr_comment
from app.github.diff_fetcher import DiffFetcher
from app.utils.formatter import build_pr_comment, categorize_issues_for_comment
from app.utils.logger import get_logger

logger = get_logger(__name__)


def execute_pr_review(
    owner: str,
    repo: str,
    pr_number: int,
    head_sha: str,
    settings: Settings,
) -> None:
    """Fetch context, run agents, post PR comment and optional check run."""
    client = GitHubClient(settings.github_token)
    fetcher = DiffFetcher(client, settings)
    try:
        bundle = fetcher.build_context_bundle(owner, repo, pr_number, head_sha)
        result = run_virtual_review_board(bundle, settings)
        lead = result["lead_report"]
        merged = list(result.get("merged_issues") or [])
        status = result["status_result"].label
        crit, hi, med, minor = categorize_issues_for_comment(merged)
        patches = lead.get("suggested_patches") or []
        if not isinstance(patches, list):
            patches = []
        patches_str = [str(p) for p in patches if p]
        for issue in merged:
            if isinstance(issue, dict) and issue.get("patch"):
                patches_str.append(str(issue["patch"]))

        body = build_pr_comment(
            overall_status=status,
            readiness_score=float(lead.get("readiness_score", 0)),
            critical=crit,
            high=hi,
            medium=med,
            minor=minor,
            suggested_patches=patches_str,
            final_recommendation=str(lead.get("final_recommendation") or "_No recommendation._"),
            app_name=settings.github_app_name,
        )
        post_pr_comment(client, owner, repo, pr_number, body)

        if settings.enable_github_check_run:
            conclusion = "failure" if status == "RED" else "success"
            title = f"Virtual Review Board — {status}"
            summary = f"Readiness score: {float(lead.get('readiness_score', 0)):.0f}%"
            create_check_run(
                client,
                owner,
                repo,
                head_sha,
                name=settings.github_app_name,
                conclusion=conclusion,
                title=title,
                summary=summary,
                text=body[:65000],
            )
    except GitHubAPIError as exc:
        logger.exception(
            "review_github_error",
            extra={
                "component": "review_pipeline",
                "repo": f"{owner}/{repo}",
                "pr_number": pr_number,
                "error_detail": str(exc),
            },
        )
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "review_unhandled_error",
            extra={
                "component": "review_pipeline",
                "repo": f"{owner}/{repo}",
                "pr_number": pr_number,
                "error_detail": str(exc),
            },
        )
        raise

