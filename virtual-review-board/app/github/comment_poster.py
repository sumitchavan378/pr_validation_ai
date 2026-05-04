"""Post issue comments on pull requests."""

from __future__ import annotations

from app.github.client import GitHubClient


def post_pr_comment(client: GitHubClient, owner: str, repo: str, pr_number: int, body: str) -> dict:
    path = f"/repos/{owner}/{repo}/issues/{pr_number}/comments"
    return client.post_json(path, {"body": body})
