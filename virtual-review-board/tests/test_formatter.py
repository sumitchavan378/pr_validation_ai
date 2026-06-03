"""Unit tests for markdown formatter."""

from app.utils.formatter import (
    build_pr_comment,
    categorize_issues_for_comment,
    flatten_agent_issues,
    limit_issues_for_comment,
    truncate_pr_comment,
)


def test_build_pr_comment_sections():
    md = build_pr_comment(
        overall_status="RED",
        readiness_score=42.7,
        critical=[{"title": "Leak", "location": "app.py", "line": 10, "severity": "Critical", "fix": "rotate"}],
        high=[],
        medium=[],
        minor=[],
        final_recommendation="Block merge.",
        app_name="Virtual Review Board",
    )
    assert "Virtual Review Board" in md
    assert "43%" in md
    assert "Critical Issues" in md
    assert "Suggested Patches" not in md
    assert "Block merge." in md


def test_categorize_issues_for_comment():
    crit, hi, med, minor = categorize_issues_for_comment(
        [
            {"severity": "Critical", "title": "a"},
            {"severity": "high", "title": "b"},
            {"severity": "Medium", "title": "c"},
            {"severity": "Low", "title": "d"},
        ]
    )
    assert len(crit) == 1 and len(hi) == 1 and len(med) == 1 and len(minor) == 1


def test_flatten_agent_issues():
    data = {"issues": [{"severity": "Low", "title": "x"}]}
    items = flatten_agent_issues(data, default_severity=None)
    assert len(items) == 1
    items2 = flatten_agent_issues({"foo": []})
    assert items2 == []


def test_build_pr_comment_hides_minor_section():
    md = build_pr_comment(
        overall_status="GREEN",
        readiness_score=90,
        critical=[],
        high=[],
        medium=[],
        minor=[{"title": "nit", "location": "a.py", "severity": "Low"}],
        final_recommendation="LGTM.",
        include_minor=False,
    )
    assert "Minor / Optional Improvements" not in md


def test_build_pr_comment_caps_high_with_notice():
    high = [{"title": f"issue-{i}", "location": f"f{i}.py", "severity": "High"} for i in range(7)]
    md = build_pr_comment(
        overall_status="YELLOW",
        readiness_score=60,
        critical=[],
        high=high[:5],
        medium=[],
        minor=[],
        final_recommendation="Review high items.",
        high_omitted_count=2,
    )
    assert "issue-4" in md
    assert "issue-5" not in md
    assert "2 more high priority issue(s) omitted" in md


def test_limit_issues_for_comment():
    crit = [{"severity": "Critical"}]
    high = [{"severity": "High"} for _ in range(8)]
    med = [{"severity": "Medium"}]
    minor = [{"severity": "Low"}]
    c, h, m, mi, omitted = limit_issues_for_comment(
        crit, high, med, minor, include_minor=False, max_high_issues=5
    )
    assert len(c) == 1 and len(h) == 5 and len(m) == 1 and mi == [] and omitted == 3


def test_truncate_pr_comment():
    body = "x" * 100
    assert truncate_pr_comment(body, 200) == body
    truncated = truncate_pr_comment(body, 5000)
    assert len(truncated) == 100
    truncated = truncate_pr_comment("a" * 5000, 200)
    assert len(truncated) <= 200
    assert "truncated" in truncated.lower()
