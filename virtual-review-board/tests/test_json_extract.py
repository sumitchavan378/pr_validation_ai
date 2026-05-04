"""JSON extraction tests."""

import pytest

from app.utils.json_extract import parse_json_blob


def test_parse_json_plain():
    assert parse_json_blob('{"a": 1}') == {"a": 1}


def test_parse_json_with_fence():
    text = 'Here:\n```json\n{"x": true}\n```'
    assert parse_json_blob(text) == {"x": True}


def test_parse_json_no_object_raises():
    with pytest.raises(ValueError):
        parse_json_blob("no json here")
