# Virtual Review Board

Multi-agent **Reviewer 0** for GitHub pull requests. On each qualifying event, the job fetches the PR diff (and full changed files when possible), runs **CrewAI** crews with **LangChain `ChatOpenAI`**, merges structured JSON from specialists, applies **severity scoring** and **status thresholds**, posts one markdown PR comment, and optionally records a **GitHub Check Run**.

This project is intended to run **only from GitHub Actions** (no HTTP server in this repo).

## How it works

- **Entry point:** `python -m app.ci_review` (see `.github/workflows/virtual-review-board-qa.yml`).
- **`DiffFetcher`** loads the unified diff, changed-file metadata, and file contents at the PR head (with size caps).
- **Specialists** (one Crew each): Security Auditor, Code Quality Architect, Compliance Officer — JSON `issues` arrays.
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
| `OPENAI_API_KEY` | OpenAI API key |

`GITHUB_TOKEN` is provided automatically by Actions — do not add it as a secret.

**Optional:** edit the workflow `env` block for `OPENAI_MODEL`, `GITHUB_APP_NAME`, `ENABLE_GITHUB_CHECK_RUN`, `LOG_LEVEL`, or tuning variables from `.env.example`.

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
| `OPENAI_API_KEY` | Required for model calls |
| `GITHUB_TOKEN` | Set automatically in Actions; required if you run `ci_review` manually |
| `GITHUB_APP_NAME` | Check run and comment header label |
| `OPENAI_MODEL` | e.g. `gpt-4o-mini`, `gpt-4o` |
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

- **Cost & latency:** four Crew runs per trigger; tune `OPENAI_MODEL` and caps for cost.
- **Failures:** logged as structured JSON to the Actions log. Specialist JSON parse failures degrade to empty `issues` with a note; lead parse failure uses a conservative fallback.
- **Advisory only:** combine with branch protection and human review as you see fit.

## License

Use and modify freely for internal engineering workflows.
