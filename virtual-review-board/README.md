# Virtual Review Board

Multi-agent **Reviewer 0** for GitHub pull requests. On each qualifying event, the job fetches the PR diff (and full changed files when possible), runs **CrewAI** crews backed by **Google Gemini** ([Google AI Studio](https://aistudio.google.com/) API key), merges structured JSON from specialists, applies **severity scoring** and **status thresholds**, posts one markdown PR comment, and optionally records a **GitHub Check Run**.

This project is intended to run **only from GitHub Actions** (no HTTP server in this repo).

## How it works

- **Entry point:** `python -m app.ci_review` (see `.github/workflows/virtual-review-board-qa.yml`).
- **`DiffFetcher`** loads the unified diff, changed-file metadata, and file contents at the PR head (with size caps).
- **Specialists** (one Crew each): Security Auditor, Code Quality Architect — JSON `issues` arrays.
- **Lead Reviewer** merges specialist output into narrative and patch suggestions.
- **`readiness_score`** uses severity weights (Critical=10, High=7, Medium=4, Low=1) against `READINESS_TOTAL_CHECKS`. **`derive_pr_status`:** any Critical → **RED**; High count ≥ threshold → **YELLOW**; else **GREEN**.
- **`GitHubClient`** uses `requests` with retries, backoff on 5xx, and basic rate-limit handling.

## GitHub Actions setup (PRs into `qa`)

### Monorepo (`virtual-review-board/` under repo root)

Workflow: **`.github/workflows/virtual-review-board-qa.yml`**

- Triggers: `pull_request` **opened**, **synchronize**, **reopened** with **base branch** **`qa`**.
- Working directory: **`virtual-review-board/`**; command: **`python -m app.ci_review`**.

**Repository secret (required)**

| Name | Purpose |
|------|---------|
| `GOOGLE_API_KEY` | API key from [Google AI Studio](https://aistudio.google.com/) |

`GITHUB_TOKEN` is provided automatically by Actions — do not add it as a secret.

**Optional:** edit the workflow `env` block for `GEMINI_MODEL`, `GITHUB_APP_NAME`, `ENABLE_GITHUB_CHECK_RUN`, `LOG_LEVEL`, or tuning variables from `.env.example`. You may use `GEMINI_API_KEY` instead of `GOOGLE_API_KEY` in `.env` (same value; see `app/config.py`).

**Branch:** ensure **`qa`** exists; the workflow filter is the PR **base** (merge target).

### Single-package repo (`virtual-review-board` is the repo root)

Copy the workflow into `.github/workflows/`, then:

- Remove `defaults.run.working-directory: virtual-review-board`.
- Set `cache-dependency-path` to `requirements.txt`.
- Run `pip install -r requirements.txt` and `python -m app.ci_review` from the repository root.

### Fork PRs

`GITHUB_TOKEN` from workflows on **forks** has limited permissions on the base repository. For cross-repo PRs you may need a dedicated bot **PAT** stored as a secret and passed as `GITHUB_TOKEN`. Same-repo PRs into `qa` work with the default token.

## Environment variables (Actions `env` or `.env` for manual runs)

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Required for Gemini (or `GEMINI_API_KEY`, equivalent) |
| `GITHUB_TOKEN` | Set automatically in Actions; required if you run `ci_review` manually |
| `GITHUB_APP_NAME` | Check run and comment header label |
| `GEMINI_MODEL` | Use `gemini/<model-id>` (e.g. `gemini/gemini-2.5-flash`). Bare `gemini-2.5-flash` is auto-prefixed. |
| `READINESS_TOTAL_CHECKS` | Score denominator (default 20) |
| `HIGH_ISSUE_YELLOW_THRESHOLD` | High-issue count → YELLOW (default 3) |
| `MAX_DIFF_CHARS` / `MAX_FILE_CONTENT_CHARS` | Prompt size caps |
| `ENABLE_GITHUB_CHECK_RUN` | `true` / `false` |
| `LOG_LEVEL` | e.g. `INFO`, `DEBUG` |

## Permissions

The workflow uses:

```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```

## Example PR comment shape

Posted markdown includes overall status (RED/YELLOW/GREEN), readiness score, sections for critical / high / medium / minor items, suggested patches, and a final recommendation — see `app/utils/formatter.py` (`build_pr_comment`).

## Operational notes

- **Cost & latency:** three Crew runs per trigger; tune `GEMINI_MODEL` and caps for cost (Google AI Studio quotas apply).
- **Gemini auth:** use `GOOGLE_API_KEY` from AI Studio. Do not set `OPENAI_API_KEY` to your Google key — CrewAI would send it to OpenAI and return 401.
- **Failures:** logged as structured JSON to the Actions log. Specialist JSON parse failures degrade to empty `issues` with a note; lead parse failure uses a conservative fallback.
- **Advisory only:** combine with branch protection and human review as you see fit.

## License

Use and modify freely for internal engineering workflows.
