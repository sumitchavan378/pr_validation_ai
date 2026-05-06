"""Fetch PR diffs, changed files, and optional full file contents."""

from __future__ import annotations

import base64
import re
from typing import Any
from urllib.parse import quote

from app.config import Settings
from app.github.client import GitHubClient, GitHubAPIError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_changed_files_from_diff(diff_text: str) -> list[str]:
    """
    Extract changed file paths from a unified diff.

    Matches lines like: diff --git a/path b/path
    """
    paths: list[str] = []
    pattern = re.compile(r"^diff --git a/(.+?) b/(.+?)$")
    for line in diff_text.splitlines():
        m = pattern.match(line)
        if m:
            b_path = m.group(2)
            if b_path not in paths:
                paths.append(b_path)
    return paths


def parse_diff_hunks(diff_text: str) -> list[dict[str, Any]]:
    """Return list of {path, header_lines} for each file in the diff."""
    files: list[dict[str, Any]] = []
    current: str | None = None
    buf: list[str] = []
    for line in diff_text.splitlines():
        m = re.match(r"^diff --git a/(.+?) b/(.+?)$", line)
        if m:
            if current is not None:
                files.append({"path": current, "content": "\n".join(buf)})
            current = m.group(2)
            buf = [line]
            continue
        if current is not None:
            buf.append(line)
    if current is not None:
        files.append({"path": current, "content": "\n".join(buf)})
    return files


class DiffFetcher:
    def __init__(self, client: GitHubClient, settings: Settings):
        self._client = client
        self._settings = settings

    def fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        path = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        diff = self._client.get_text(
            path,
            accept="application/vnd.github.diff",
        )
        if len(diff) > self._settings.max_diff_chars:
            logger.warning(
                "diff_truncated",
                extra={"component": "diff_fetcher", "original_len": len(diff)},
            )
            return diff[: self._settings.max_diff_chars] + "\n\n<!-- truncated -->"
        return diff

    def fetch_changed_files(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while True:
            chunk = self._client.get_json(
                f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
                params={"per_page": 100, "page": page},
            )
            if not isinstance(chunk, list) or not chunk:
                break
            items.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return items

    def fetch_pr_metadata(self, owner: str, repo: str, pr_number: int) -> dict[str, Any]:
        return self._client.get_json(f"/repos/{owner}/{repo}/pulls/{pr_number}")

    def fetch_file_content(self, owner: str, repo: str, path: str, ref: str) -> str | None:
        """Return decoded file text or None if missing/binary/error."""
        try:
            encoded = quote(path, safe="")
            data = self._client.get_json(
                f"/repos/{owner}/{repo}/contents/{encoded}",
                params={"ref": ref},
            )
        except GitHubAPIError as exc:
            logger.warning(
                "file_fetch_failed",
                extra={"component": "diff_fetcher", "path": path, "error_detail": str(exc)},
            )
            return None
        if not isinstance(data, dict):
            return None
        if data.get("type") != "file":
            return None
        enc = data.get("encoding")
        content = data.get("content")
        if enc != "base64" or not isinstance(content, str):
            return None
        try:
            raw = base64.b64decode(content).decode("utf-8", errors="replace")
        except (ValueError, UnicodeError):
            return None
        if len(raw) > self._settings.max_file_content_chars:
            return raw[: self._settings.max_file_content_chars] + "\n\n<!-- truncated -->"
        return raw

    def build_context_bundle(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        head_sha: str,
    ) -> dict[str, Any]:
        meta = self.fetch_pr_metadata(owner, repo, pr_number)
        diff = self.fetch_pr_diff(owner, repo, pr_number)
        changed = self.fetch_changed_files(owner, repo, pr_number)
        file_paths = [c.get("filename") for c in changed if isinstance(c, dict) and c.get("filename")]
        full_files: dict[str, str] = {}
        for fp in file_paths:
            if not isinstance(fp, str):
                continue
            text = self.fetch_file_content(owner, repo, fp, head_sha)
            if text is not None:
                full_files[fp] = text
        return {
            "title": meta.get("title", ""),
            "body": meta.get("body") or "",
            "head_sha": head_sha,
            "base_ref": (meta.get("base") or {}).get("ref"),
            "head_ref": (meta.get("head") or {}).get("ref"),
            "diff": diff,
            "changed_files": changed,
            "full_files": full_files,
        }
