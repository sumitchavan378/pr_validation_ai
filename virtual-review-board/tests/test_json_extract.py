"""JSON extraction tests."""

import pytest

from app.utils.json_extract import parse_json_blob


def test_parse_json_plain():
    assert parse_json_blob('{"a": 1}') == {"a": 1}


def test_parse_json_with_fence():
    text = 'Here:\n```json\n{"x": true}\n```'
    assert parse_json_blob(text) == {"x": True}


def test_parse_json_fence_without_closing_fence():
    text = '```json\n{"issues": [{"severity": "High"}]}'
    data = parse_json_blob(text)
    assert len(data["issues"]) == 1


def test_parse_json_fence_with_embedded_backticks_in_string():
    text = """```json
{
  "issues": [
    {
      "severity": "High",
      "patch": "```diff\\n+line\\n```"
    }
  ]
}
```"""
    data = parse_json_blob(text)
    assert "```diff" in data["issues"][0]["patch"]


def test_parse_json_prose_before_fence():
    text = "Analysis complete.\n```json\n{\"ok\": true}\n```\nDone."
    assert parse_json_blob(text) == {"ok": True}


def test_parse_json_no_object_raises():
    with pytest.raises(ValueError):
        parse_json_blob("no json here")
