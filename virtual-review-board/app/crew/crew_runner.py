"""CrewAI orchestration: specialists produce JSON; lead merges into final structure."""

from __future__ import annotations

import json
from typing import Any

from crewai import Crew, Task
from crewai.llm import LLM

from app.agents.compliance_officer import create_compliance_officer, load_compliance_instructions
from app.agents.lead_reviewer import create_lead_reviewer, load_lead_instructions
from app.agents.quality_architect import create_quality_architect, load_quality_instructions
from app.agents.security_auditor import create_security_auditor, load_security_instructions
from app.config import Settings
from app.scoring.readiness_score import derive_pr_status
from app.utils.json_extract import parse_json_blob
from app.utils.logger import get_logger

logger = get_logger(__name__)

SPECIALIST_JSON_CONTRACT = """
Return ONLY JSON with this shape:
{
  "issues": [
    {
      "severity": "Low|Medium|High|Critical",
      "title": "short label",
      "location": "path/to/file.py",
      "line": 12,
      "why": "rationale",
      "fix": "actionable remediation",
      "exploit_scenario": "optional for security",
      "rule": "optional policy name",
      "patch": "optional unified diff snippet",
      "example_refactor": "optional code snippet"
    }
  ],
  "notes": ["optional bullet strings"]
}
"""


def _build_pr_context(bundle: dict[str, Any]) -> str:
    lines: list[str] = [
        f"PR Title: {bundle.get('title', '')}",
        f"PR Description:\n{bundle.get('body', '')}",
        f"Head ref (branch): {bundle.get('head_ref', '')}",
        f"Base ref (branch): {bundle.get('base_ref', '')}",
        "",
        "## Unified Diff",
        str(bundle.get("diff", "")),
    ]
    full_files = bundle.get("full_files") or {}
    if isinstance(full_files, dict) and full_files:
        lines.extend(["", "## Full files at PR head (truncation may apply)"])
        for path, content in full_files.items():
            lines.extend([f"### {path}", str(content), ""])
    changed = bundle.get("changed_files") or []
    if isinstance(changed, list) and changed:
        lines.append("## Changed files metadata (from GitHub API)")
        lines.append(json.dumps(changed, indent=2)[:8000])
    return "\n".join(lines)


def _kickoff_json(agent, instructions: str, context: str) -> dict[str, Any]:
    description = f"{instructions.strip()}\n\n{SPECIALIST_JSON_CONTRACT.strip()}\n\n## DATA\n{context}"
    task = Task(
        description=description,
        expected_output="Raw JSON object matching the contract. No markdown.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    raw = str(crew.kickoff())
    try:
        return parse_json_blob(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.exception(
            "crew_json_parse_failed",
            extra={"component": "crew_runner", "preview": raw[:500]},
        )
        return {
            "issues": [],
            "notes": [f"Reviewer output was not valid JSON ({exc})."],
        }


def _merge_issues(*reports: dict[str, Any]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for rep in reports:
        issues = rep.get("issues")
        if isinstance(issues, list):
            for item in issues:
                if isinstance(item, dict):
                    merged.append(item)
    return merged


def run_virtual_review_board(bundle: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """
    Execute specialist crews sequentially, then lead reviewer.

    Returns dict with keys: specialist_reports, lead_report, markdown_comment, status_result
    """
    llm = LLM(
        model=settings.gemini_model,
        temperature=0.1,
        api_key=settings.google_api_key,
    )

    context = _build_pr_context(bundle)

    security = _kickoff_json(
        create_security_auditor(llm),
        load_security_instructions(),
        context,
    )
    quality = _kickoff_json(
        create_quality_architect(llm),
        load_quality_instructions(),
        context,
    )
    compliance = _kickoff_json(
        create_compliance_officer(llm),
        load_compliance_instructions(),
        context,
    )

    lead_blob = {
        "security": security,
        "quality": quality,
        "compliance": compliance,
    }
    lead_instructions = load_lead_instructions().strip()
    lead_description = f"""{lead_instructions}

Specialist JSON (verbatim, do not discard findings):
{json.dumps(lead_blob, ensure_ascii=False)[:120000]}

Return JSON ONLY with this shape:
{{
  "overall_status": "RED|YELLOW|GREEN",
  "readiness_score": 0-100 number,
  "critical": [issue...],
  "high": [issue...],
  "medium": [issue...],
  "minor": [issue...],
  "suggested_patches": ["diff snippets strings"],
  "final_recommendation": "markdown string"
}}
Issue objects must include severity, title, location, line, why, fix, and optional patch fields.
"""

    lead_agent = create_lead_reviewer(llm)
    lead_task = Task(
        description=lead_description,
        expected_output="Raw JSON as specified. No markdown fences.",
        agent=lead_agent,
    )
    lead_crew = Crew(agents=[lead_agent], tasks=[lead_task], verbose=False)
    lead_raw = str(lead_crew.kickoff())
    try:
        lead_report = parse_json_blob(lead_raw)
    except (json.JSONDecodeError, ValueError):
        logger.exception(
            "lead_json_parse_failed",
            extra={"component": "crew_runner", "preview": lead_raw[:500]},
        )
        lead_report = {
            "overall_status": "YELLOW",
            "readiness_score": 50.0,
            "critical": [],
            "high": [],
            "medium": [],
            "minor": [],
            "suggested_patches": [],
            "final_recommendation": (
                "Lead reviewer could not parse model output; treat this run as **needs human review**."
            ),
        }

    merged_issues = _merge_issues(security, quality, compliance)
    status = derive_pr_status(
        merged_issues,
        total_checks=settings.readiness_total_checks,
        high_issue_yellow_threshold=settings.high_issue_yellow_threshold,
    )

    # Deterministic policy overrides model-reported status/score for thresholds
    lead_report["overall_status"] = status.label
    lead_report["readiness_score"] = status.readiness_score

    return {
        "specialist_reports": lead_blob,
        "lead_report": lead_report,
        "merged_issues": merged_issues,
        "status_result": status,
    }
