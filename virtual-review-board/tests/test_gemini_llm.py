"""Tests for Gemini model id normalization."""

from app.utils.gemini_llm import normalize_gemini_model_id


def test_normalize_gemini_model_id_adds_prefix():
    assert normalize_gemini_model_id("gemini-2.5-flash") == "gemini/gemini-2.5-flash"
    assert normalize_gemini_model_id("gemini-3.5-flash") == "gemini/gemini-3.5-flash"


def test_normalize_gemini_model_id_unchanged_when_prefixed():
    assert normalize_gemini_model_id("gemini/gemini-2.5-flash") == "gemini/gemini-2.5-flash"


def test_normalize_gemini_model_id_empty_defaults():
    assert normalize_gemini_model_id("") == "gemini/gemini-3.5-flash"
    assert normalize_gemini_model_id("   ") == "gemini/gemini-3.5-flash"
