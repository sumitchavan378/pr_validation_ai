"""GitHub REST client with retries, backoff, and typed helpers."""

from __future__ import annotations

import time
from typing import Any

import requests
from requests import Response

from app.utils.logger import get_logger

logger = get_logger(__name__)


class GitHubAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None, body: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class GitHubClient:
    """Thin wrapper around GitHub REST v3 with exponential backoff."""

    def __init__(self, token: str, base_url: str = "https://api.github.com", max_retries: int = 5):
        self._token = token
        self._base = base_url.rstrip("/")
        self._max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "virtual-review-board/1.0",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Response:
        url = f"{self._base}{path}"
        merged = dict(self._session.headers)
        if headers:
            merged.update(headers)

        delay = 1.0
        last_exc: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                resp = self._session.request(
                    method,
                    url,
                    headers=merged,
                    params=params,
                    json=json_body,
                    timeout=60,
                )
                if resp.status_code == 403 and "rate limit" in (resp.text or "").lower():
                    self._sleep_on_rate_limit(resp)
                    continue
                if resp.status_code in (502, 503, 504):
                    time.sleep(delay)
                    delay = min(delay * 2, 32.0)
                    continue
                if 500 <= resp.status_code < 600:
                    time.sleep(delay)
                    delay = min(delay * 2, 32.0)
                    continue
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                logger.warning(
                    "github_request_retry",
                    extra={"component": "github", "error_detail": str(exc), "attempt": attempt},
                )
                time.sleep(delay)
                delay = min(delay * 2, 32.0)
        raise GitHubAPIError(f"GitHub request failed after retries: {last_exc}")

    @staticmethod
    def _sleep_on_rate_limit(resp: Response) -> None:
        reset = resp.headers.get("X-RateLimit-Reset")
        if reset and reset.isdigit():
            sleep_for = max(0.0, float(reset) - time.time()) + 1.0
            sleep_for = min(sleep_for, 60.0)
        else:
            sleep_for = 5.0
        logger.warning("github_rate_limited", extra={"component": "github", "sleep_s": sleep_for})
        time.sleep(sleep_for)

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        r = self._request("GET", path, params=params)
        if r.status_code >= 400:
            raise GitHubAPIError(f"GET {path} failed", r.status_code, r.text)
        return r.json()

    def get_text(self, path: str, accept: str) -> str:
        r = self._request("GET", path, headers={"Accept": accept})
        if r.status_code >= 400:
            raise GitHubAPIError(f"GET {path} failed", r.status_code, r.text)
        return r.text

    def post_json(self, path: str, body: dict[str, Any]) -> Any:
        r = self._request("POST", path, json_body=body)
        if r.status_code >= 400:
            raise GitHubAPIError(f"POST {path} failed", r.status_code, r.text)
        if not r.content:
            return {}
        return r.json()
