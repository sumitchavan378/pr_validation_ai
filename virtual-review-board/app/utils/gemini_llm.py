"""Helpers for CrewAI + Google Gemini LLM configuration."""

from __future__ import annotations

import os


def normalize_gemini_model_id(model: str) -> str:
    """
    Ensure model id uses LiteLLM/CrewAI provider prefix so requests hit Gemini, not OpenAI.

    Examples:
        gemini-2.5-flash -> gemini/gemini-2.5-flash
        gemini/gemini-2.5-flash -> unchanged
    """
    m = (model or "").strip()
    if not m:
        return "gemini/gemini-2.5-flash"
    if "/" in m:
        return m
    if m.startswith("gemini-"):
        return f"gemini/{m}"
    return m


def configure_gemini_env(api_key: str) -> None:
    """Expose Google API key to env vars LiteLLM/CrewAI expect for Gemini."""
    if not api_key:
        return
    os.environ.setdefault("GEMINI_API_KEY", api_key)
    os.environ.setdefault("GOOGLE_API_KEY", api_key)
