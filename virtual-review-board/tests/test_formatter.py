"""Unit tests for markdown formatter."""

from app.utils.formatter import build_pr_comment, categorize_issues_for_comment, flatten_agent_issues


def test_build_pr_comment_sections():
    md = build_pr_comment(
        overall_status="RED",
        readiness_score=42.7,
        critical=[{"title": "Leak", "location": "app.py", "line": 10, "severity": "Critical", "fix": "rotate"}],
        high=[],
        medium=[],
        minor=[],
        suggested_patches=["- a\n+ b"],
        final_recommendation="Block merge.",
        app_name="Virtual Review Board",
    )
    assert "Virtual Review Board" in md
    assert "43%" in md
    assert "Critical Issues" in md
    assert "Suggested Patches" in md
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
