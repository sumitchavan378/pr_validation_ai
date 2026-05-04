"""Extract JSON payloads from LLM / Crew outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def parse_json_blob(text: str) -> dict[str, Any]:
    """
    Parse JSON from model output that may include fences or prose.
    """
    if text is None:
        raise ValueError("empty output")
    s = str(text).strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", s, re.IGNORECASE)
    if fence:
        s = fence.group(1).strip()
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no json object found")
    blob = s[start : end + 1]
    return json.loads(blob)
