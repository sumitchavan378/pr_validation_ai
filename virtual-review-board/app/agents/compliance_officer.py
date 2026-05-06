"""CrewAI Compliance Officer agent factory."""

from __future__ import annotations

from pathlib import Path

from crewai import Agent
from crewai.llm import LLM


def _prompt_path() -> Path:
    return Path(__file__).resolve().parents[1] / "prompts" / "compliance_prompt.txt"


def load_compliance_instructions() -> str:
    return _prompt_path().read_text(encoding="utf-8")


def create_compliance_officer(llm: LLM) -> Agent:
    return Agent(
        role="Compliance Officer",
        goal=(
            "Check repository hygiene: docs/tests/changelog, typing, formatting, linting, "
            "and branch naming against stated policies."
        ),
        backstory=(
            "You are a release engineer ensuring changes meet team standards before human review."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
