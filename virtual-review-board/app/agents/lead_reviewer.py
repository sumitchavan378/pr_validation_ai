"""Lead Reviewer / coordinator agent."""

from __future__ import annotations

from pathlib import Path

from crewai import Agent
from langchain_openai import ChatOpenAI


def _prompt_path() -> Path:
    return Path(__file__).resolve().parents[1] / "prompts" / "lead_prompt.txt"


def load_lead_instructions() -> str:
    return _prompt_path().read_text(encoding="utf-8")


def create_lead_reviewer(llm: ChatOpenAI) -> Agent:
    return Agent(
        role="Lead Reviewer",
        goal=(
            "Merge specialist JSON reports into a single structured JSON suitable for "
            "markdown rendering, with categorized findings and executive summary."
        ),
        backstory=(
            "You coordinate virtual reviewers and never invent file paths or line numbers "
            "not present in specialist reports unless clearly marked as hypothetical."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
