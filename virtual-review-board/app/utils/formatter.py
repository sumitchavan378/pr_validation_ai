"""Build GitHub PR comment markdown from structured review data."""

from __future__ import annotations

from typing import Any


def _issue_block(issue: dict[str, Any]) -> str:
    loc = issue.get("location") or issue.get("file") or "unknown"
    line = issue.get("line")
    if line is not None and ":" not in str(loc):
        loc = f"{loc}:{line}"
    title = issue.get("title") or issue.get("summary") or "Issue"
    sev = issue.get("severity", "")
    lines = [f"- **[{loc}]** {title}"]
    if sev:
        lines.append(f"  - **Severity:** {sev}")
    if issue.get("why"):
        lines.append(f"  - **Why:** {issue['why']}")
    if issue.get("exploit_scenario"):
        lines.append(f"  - **Exploit scenario:** {issue['exploit_scenario']}")
    if issue.get("rule"):
        lines.append(f"  - **Rule:** {issue['rule']}")
    if issue.get("fix"):
        lines.append(f"  - **Fix:** {issue['fix']}")
    if issue.get("recommendation"):
        lines.append(f"  - **Recommendation:** {issue['recommendation']}")
    if issue.get("patch"):
        lines.append("  - **Suggested patch:**")
        lines.append("```diff")
        lines.append(str(issue["patch"]).strip())
        lines.append("```")
    if issue.get("example_refactor"):
        lines.append("  - **Example refactor:**")
        lines.append("```")
        lines.append(str(issue["example_refactor"]).strip())
        lines.append("```")
    return "\n".join(lines)


def _dict_issues(items: list[Any]) -> list[dict[str, Any]]:
    return [i for i in items if isinstance(i, dict)]


def limit_issues_for_comment(
    critical: list[dict[str, Any]],
    high: list[dict[str, Any]],
    medium: list[dict[str, Any]],
    minor: list[dict[str, Any]],
    *,
    include_minor: bool,
    max_high_issues: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int]:
    """Apply PR comment display limits; returns buckets and count of omitted high issues."""
    high_omitted = 0
    if max_high_issues >= 0 and len(high) > max_high_issues:
        high_omitted = len(high) - max_high_issues
        high = high[:max_high_issues]
    if not include_minor:
        minor = []
    return critical, high, medium, minor, high_omitted


def truncate_pr_comment(body: str, max_chars: int) -> str:
    """Trim comment body to max_chars, preserving a short truncation notice."""
    if max_chars <= 0 or len(body) <= max_chars:
        return body
    notice = "\n\n---\n_Comment truncated to fit the configured character limit._"
    budget = max_chars - len(notice)
    if budget <= 0:
        return body[:max_chars]
    trimmed = body[:budget].rstrip()
    return trimmed + notice


def build_pr_comment(
    *,
    overall_status: str,
    readiness_score: float,
    critical: list[dict[str, Any]],
    high: list[dict[str, Any]],
    medium: list[dict[str, Any]],
    minor: list[dict[str, Any]],
    final_recommendation: str,
    app_name: str = "Virtual Review Board",
    include_minor: bool = False,
    high_omitted_count: int = 0,
) -> str:
    """Assemble the final markdown body for a single PR comment."""
    status_line = overall_status.upper()
    if "RED" in status_line:
        emoji_status = "🔴 RED"
    elif "YELLOW" in status_line:
        emoji_status = "🟡 YELLOW"
    else:
        emoji_status = "🟢 GREEN"

    parts: list[str] = [
        f"## 🤖 {app_name} Report",
        "",
        f"**Overall Status:** {emoji_status}",
        f"**Review Readiness Score:** {readiness_score:.0f}%",
        "",
        "### 🔴 Critical Issues",
    ]
    crit = _dict_issues(list(critical))
    hi = _dict_issues(list(high))
    med = _dict_issues(list(medium))
    mino = _dict_issues(list(minor))
    if crit:
        parts.extend(_issue_block(i) for i in crit)
    else:
        parts.append("_None detected._")
    parts.extend(["", "### 🟠 High Priority Issues"])
    if hi:
        parts.extend(_issue_block(i) for i in hi)
        if high_omitted_count > 0:
            parts.append(f"_…and {high_omitted_count} more high priority issue(s) omitted._")
    else:
        parts.append("_None detected._")
    parts.extend(["", "### 🟡 Medium Priority Suggestions"])
    if med:
        parts.extend(_issue_block(i) for i in med)
    else:
        parts.append("_None._")
    if include_minor:
        parts.extend(["", "### 🟢 Minor / Optional Improvements"])
        if mino:
            parts.extend(_issue_block(i) for i in mino)
        else:
            parts.append("_None._")

    parts.extend(["", "### Final Recommendation", "", final_recommendation, ""])
    return "\n".join(parts)


def categorize_issues_for_comment(
    issues: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Split issues into Critical / High / Medium / Minor buckets from severity field."""
    critical: list[dict[str, Any]] = []
    high: list[dict[str, Any]] = []
    medium: list[dict[str, Any]] = []
    minor: list[dict[str, Any]] = []
    for item in issues:
        if not isinstance(item, dict):
            continue
        sev = str(item.get("severity", "low")).strip().lower()
        if sev == "critical":
            critical.append(item)
        elif sev == "high":
            high.append(item)
        elif sev == "medium":
            medium.append(item)
        else:
            minor.append(item)
    return critical, high, medium, minor


def flatten_agent_issues(agent_json: dict[str, Any], default_severity: str | None = None) -> list[dict[str, Any]]:
    """Normalize agent JSON payloads to a list of issue dicts."""
    issues = agent_json.get("issues")
    if not isinstance(issues, list):
        return []
    out: list[dict[str, Any]] = []
    for item in issues:
        if not isinstance(item, dict):
            continue
        if default_severity and "severity" not in item:
            item = {**item, "severity": default_severity}
        out.append(item)
    return out
