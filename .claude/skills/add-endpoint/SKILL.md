---
name: add-endpoint
description: Use when adding or changing an API endpoint in the Quick POS backend (app/).
---

# Add an API endpoint

1. Read `docs/ARCHITECTURE.md` (API table, data model) and `app/CLAUDE.md`.
2. If a similar endpoint exists, read all four of its layer files first and copy the pattern.
3. Build from the bottom up:
   1. Repository (`app/repositories/{entity}_repository.py`): SQL with `?` placeholders, returns dicts
   2. Service (`app/services/{entity}_service.py`): business rules, returns `(data, error)`
   3. Handler (`app/handlers/{entity}_handler.py`): validate input, call service, respond via `responses.py`
   4. Endpoint (`app/endpoints/{entity}_endpoints.py`): route + `login_required`, call handler;
      register the blueprint in `app/__init__.py` if it is new
4. Tests in `tests/test_{entity}.py`:
   - happy path
   - one invalid input (expects `status: false`)
   - not logged in (expects 401)
5. Run `python -m pytest -q` until it passes.
6. Add or update the row in the API table in `docs/ARCHITECTURE.md`.
