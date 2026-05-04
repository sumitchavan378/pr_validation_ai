"""Pull request event types handled by the review runner (e.g. GitHub Actions)."""

ALLOWED_ACTIONS = frozenset({"opened", "synchronize", "reopened"})
