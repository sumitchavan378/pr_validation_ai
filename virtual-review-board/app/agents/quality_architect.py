"""CrewAI Code Quality Architect agent factory."""

from __future__ import annotations

from pathlib import Path

from crewai import Agent
from langchain_openai import ChatOpenAI


def _prompt_path() -> Path:
    return Path(__file__).resolve().parents[1] / "prompts" / "quality_prompt.txt"


def load_quality_instructions() -> str:
    return _prompt_path().read_text(encoding="utf-8")


def create_quality_architect(llm: ChatOpenAI) -> Agent:
    return Agent(
        role="Code Quality Architect",
        goal=(
            "Evaluate maintainability: complexity, modularity, naming, DRY/SOLID signals, "
            "error handling, and code smells grounded in the provided diff and files."
        ),
        backstory=(
            "You are a staff software engineer focused on long-term codebase health and "
            "reviewer empathy. You give actionable refactors, not vague opinions."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
