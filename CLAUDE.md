# Quick POS

A simple point of sale for a small retail shop. A cashier logs in, picks a category,
picks items, adjusts quantities, and saves the order. Cash only. Learning project:
keep everything simple.

## Stack
- Backend: Python 3.11+, Flask, SQLite via the built-in `sqlite3` module (no ORM)
- Frontend: plain HTML, CSS and JavaScript served by Flask (no frameworks, no build step)
- Tests: pytest. Formatting: ruff.
- Package manager: uv. Dependencies live in `pyproject.toml` (locked in `uv.lock`).

## Commands (run from the project root)
- Install:  `uv sync`
- Init DB:  `uv run flask --app app init-db`
- Seed:     `uv run flask --app app seed`
- Run:      `uv run flask --app app run --debug`  → http://127.0.0.1:5000
- Test:     `uv run pytest -q`
- Format:   `uv run ruff format .`
- Reset DB after a schema change: delete `instance/` database file, then run init-db and seed again

Always prefix Python tools with `uv run`. Never use `pip install`.

## Layout
- `app/`        Python backend: endpoints → handlers → services → repositories (rules in `app/CLAUDE.md`)
- `frontend/`   HTML pages, CSS, JS (rules in `frontend/CLAUDE.md`)
- `tests/`      pytest tests, one file per area
- `instance/`   SQLite database file (git-ignored)

## Docs
- `docs/PLAN.md`          features in build order + out of scope. Read before starting a feature.
- `docs/ARCHITECTURE.md`  data model, API endpoints, screens. Read before adding endpoints or tables.
- `docs/specs/`           one spec per feature, created with `/plan-feature`.

## Conventions
- Every API response: `{"status": true|false, "message": "...", "data": ..., "errors": []}`
- Money is an INTEGER in the smallest unit (e.g. 1250 = 12.50). Never use floats for money.
- The server calculates all totals from database prices. Never trust prices from the browser.
- Files `{entity}_{layer}.py` (e.g. `sale_service.py`). Functions `verb_noun`. Type hints everywhere.
- Use `logging`, not `print()`.
- Secrets and config come from environment variables with a dev-only fallback (e.g. SECRET_KEY).

## Rules
- Build only what the current spec asks for. Check "Out of scope" in `docs/PLAN.md`.
- Do not add dependencies or JavaScript libraries without asking. If approved, add with `uv add`.
- Only change files needed for the task.
- Never read or edit `.env`. Never run `git clean`.
- When a feature is done: tick it in `docs/PLAN.md`, set its spec to `Status: done`,
  and update `docs/ARCHITECTURE.md` if tables, endpoints or screens changed.

## Git
- Never commit to `main`. Each feature gets its own branch: `feature/NN-short-name` (NN = plan item).
- Start every branch from an up-to-date `main`.
- Commit only on the feature branch, after I confirm the message.