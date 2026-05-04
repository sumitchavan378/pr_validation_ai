"""Readiness score and PR status from structured issues."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

SEVERITY_WEIGHTS = {
    "critical": 10,
    "high": 7,
    "medium": 4,
    "low": 1,
}


def _normalize_severity(raw: str | None) -> str:
    if not raw:
        return "low"
    s = raw.strip().lower()
    if s in SEVERITY_WEIGHTS:
        return s
    return "low"


def penalty_points_for_issues(issues: Iterable[dict[str, Any]]) -> float:
    """Sum severity weights for a list of issues."""
    total = 0.0
    for issue in issues:
        sev = _normalize_severity(str(issue.get("severity", "")))
        total += float(SEVERITY_WEIGHTS.get(sev, 1))
    return total


def readiness_score_from_penalty(
    *,
    total_checks: int,
    penalty_points: float,
    max_penalty_cap: float | None = None,
) -> float:
    """
    Map penalty to readiness score.

    Uses PassedChecks / TotalChecks * 100 where passed checks are reduced by
    weighted issue burden (each severity consumes fractional checks).
    """
    if total_checks <= 0:
        return 100.0
    cap = max_penalty_cap if max_penalty_cap is not None else float(total_checks) * 10.0
    effective_penalty = min(penalty_points, cap)
    # Each penalty point removes 1/total_checks fraction of a perfect score ceiling
    # scaled so heavy penalties drive score down quickly.
    burden_units = effective_penalty / 10.0  # one critical ~= one full check failure
    passed = max(0.0, float(total_checks) - burden_units)
    return max(0.0, min(100.0, (passed / float(total_checks)) * 100.0))


def count_by_severity(issues: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in issues:
        k = _normalize_severity(str(issue.get("severity", "")))
        if k in counts:
            counts[k] += 1
    return counts


@dataclass(frozen=True)
class StatusResult:
    label: str  # RED | YELLOW | GREEN
    readiness_score: float
    penalty_points: float


def derive_pr_status(
    issues: list[dict[str, Any]],
    *,
    total_checks: int = 20,
    high_issue_yellow_threshold: int = 3,
) -> StatusResult:
    """
    Configurable thresholds:
    - Any Critical -> RED
    - High count >= threshold -> YELLOW (unless RED)
    - Else GREEN
    """
    penalty = penalty_points_for_issues(issues)
    score = readiness_score_from_penalty(total_checks=total_checks, penalty_points=penalty)
    counts = count_by_severity(issues)

    if counts["critical"] > 0:
        return StatusResult(label="RED", readiness_score=score, penalty_points=penalty)
    if counts["high"] >= high_issue_yellow_threshold:
        return StatusResult(label="YELLOW", readiness_score=score, penalty_points=penalty)
    return StatusResult(label="GREEN", readiness_score=score, penalty_points=penalty)
