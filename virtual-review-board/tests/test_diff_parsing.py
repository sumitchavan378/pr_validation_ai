"""Tests for GitHub diff parsing helpers."""

from app.github.diff_fetcher import parse_changed_files_from_diff, parse_diff_hunks


SAMPLE_DIFF = """diff --git a/README.md b/README.md
index 111..222 100644
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-Old
+New
diff --git a/src/app.py b/src/app.py
index 333..444 100644
--- a/src/app.py
+++ b/src/app.py
@@ -0,0 +1 @@
+print('hi')
"""


def test_parse_changed_files_from_diff_order():
    files = parse_changed_files_from_diff(SAMPLE_DIFF)
    assert files == ["README.md", "src/app.py"]


def test_parse_diff_hunks_paths():
    hunks = parse_diff_hunks(SAMPLE_DIFF)
    paths = [h["path"] for h in hunks]
    assert paths == ["README.md", "src/app.py"]
    assert "diff --git" in hunks[0]["content"]
