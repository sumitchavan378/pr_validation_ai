"""CrewAI Security Auditor agent factory."""

from __future__ import annotations

from pathlib import Path

from crewai import Agent
from langchain_openai import ChatOpenAI


def _prompt_path() -> Path:
    return Path(__file__).resolve().parents[1] / "prompts" / "security_prompt.txt"


def load_security_instructions() -> str:
    return _prompt_path().read_text(encoding="utf-8")


def create_security_auditor(llm: ChatOpenAI) -> Agent:
    return Agent(
        role="Security Auditor",
        goal=(
            "Analyze the pull request for OWASP Top 10 style risks, hardcoded secrets, "
            "injection, auth flaws, unsafe validation, dependency risks, and insecure file handling."
        ),
        backstory=(
            "You are a principal application security engineer who has led threat modeling "
            "for regulated industries. You prioritize exploitable findings with crisp evidence."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
