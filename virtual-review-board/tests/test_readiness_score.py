"""Unit tests for readiness_score module."""

from app.scoring.readiness_score import (
    count_by_severity,
    derive_pr_status,
    penalty_points_for_issues,
    readiness_score_from_penalty,
)


def test_penalty_weights_sum():
    issues = [
        {"severity": "Critical"},
        {"severity": "High"},
        {"severity": "Medium"},
        {"severity": "Low"},
    ]
    assert penalty_points_for_issues(issues) == 10 + 7 + 4 + 1


def test_readiness_score_decreases_with_penalty():
    s0 = readiness_score_from_penalty(total_checks=20, penalty_points=0.0)
    s1 = readiness_score_from_penalty(total_checks=20, penalty_points=50.0)
    assert s0 > s1
    assert 0 <= s1 <= 100


def test_derive_pr_status_red_on_critical():
    issues = [{"severity": "Critical", "title": "x"}]
    r = derive_pr_status(issues, total_checks=10, high_issue_yellow_threshold=3)
    assert r.label == "RED"


def test_derive_pr_status_yellow_on_high_threshold():
    issues = [{"severity": "High"} for _ in range(3)]
    r = derive_pr_status(issues, total_checks=10, high_issue_yellow_threshold=3)
    assert r.label == "YELLOW"


def test_derive_pr_status_green():
    issues = [{"severity": "Low"}]
    r = derive_pr_status(issues, total_checks=10, high_issue_yellow_threshold=3)
    assert r.label == "GREEN"


def test_count_by_severity():
    issues = [{"severity": "high"}, {"severity": "HIGH"}, {"severity": "critical"}]
    c = count_by_severity(issues)
    assert c["high"] == 2
    assert c["critical"] == 1
