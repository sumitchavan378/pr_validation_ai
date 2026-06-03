"""Extract JSON payloads from LLM / Crew outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def _strip_leading_code_fence(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*", "", text.strip(), count=1, flags=re.IGNORECASE).strip()


def _strip_trailing_code_fence(text: str) -> str:
    return re.sub(r"```\s*$", "", text.strip()).strip()


def _extract_balanced_object(text: str) -> str:
    """Return the first top-level {...} span, respecting JSON string boundaries."""
    start = text.find("{")
    if start < 0:
        raise ValueError("no json object found")

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise ValueError("no json object found")


def parse_json_blob(text: str) -> dict[str, Any]:
    """
    Parse JSON from model output that may include markdown fences or prose.

    Uses brace-balanced extraction so embedded ``` inside JSON string values
    (e.g. patch diffs) does not break parsing.
    """
    if text is None:
        raise ValueError("empty output")

    raw = str(text).strip()
    candidates = [
        raw,
        _strip_leading_code_fence(raw),
        _strip_trailing_code_fence(_strip_leading_code_fence(raw)),
    ]
    seen: set[str] = set()
    last_error: Exception | None = None

    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            blob = _extract_balanced_object(candidate)
            data = json.loads(blob)
            if not isinstance(data, dict):
                raise ValueError("expected JSON object")
            return data
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc

    raise ValueError("no json object found") from last_error
