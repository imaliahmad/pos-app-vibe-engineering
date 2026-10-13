# Login
Status: done
Plan item: 3

## Goal
A cashier or admin can sign in at `/` with username and password, land on `/pos`, and sign out.
Anyone not signed in who opens `/pos` is sent back to `/`. The API knows who is signed in.

## Changes
- `app/repositories/user_repository.py`: add `get_user_by_username(username: str) -> dict | None`
  and `get_user_by_id(user_id: int) -> dict | None` (parameterized SELECT, plain dict with
  id, username, password_hash, role, active).
- `app/services/__init__.py`, `app/handlers/__init__.py`, `app/endpoints/__init__.py`: empty, make packages.
- `app/services/auth_service.py`:
  - `authenticate_user(username: str, password: str) -> tuple[dict | None, str | None]`: user must
    exist, be active, and `check_password_hash` must pass. Any failure → `(None, "Invalid username or password")`
    (same message for every case). Success → `({id, username, role}, None)`, never the hash.
  - `get_current_user(user_id: int) -> dict | None`: `{id, username, role}` if the user exists and is active.
- `app/handlers/auth_handler.py`:
  - `handle_login()`: read JSON body; `username` and `password` must be non-empty strings, else
    `failure(..., errors=[...], 400)`. Bad credentials → `failure(..., 401)`. Success →
    `session.clear()`, set `session["user_id"]`, `session["role"]`, return `success(user)`.
  - `handle_logout()`: `session.clear()`, `success(None, "Logged out")`.
  - `handle_me()`: `get_current_user(session["user_id"])`; if gone/inactive → clear session, `failure(..., 401)`.
- `app/auth.py`: `login_required` decorator: no `user_id` in session → `failure("Login required", status_code=401)`.
  (`role_required` comes later, when an endpoint needs it.)
- `app/endpoints/auth_endpoints.py`: blueprint `auth`, `POST /api/auth/login` (no auth),
  `POST /api/auth/logout` and `GET /api/auth/me` (both `login_required`).
- `app/endpoints/page_endpoints.py`: blueprint `pages`, serves files from the project's `frontend/` folder
  with `send_from_directory`:
  - `GET /` → `login.html`; if signed in, redirect to `/pos`.
  - `GET /pos` → `pos.html`; if not signed in, redirect to `/`.
  - `GET /css/<path>` and `GET /js/<path>` → files from `frontend/css` and `frontend/js`.
- `app/__init__.py`: register both blueprints.
- `frontend/js/api.js`: `apiLogin(username, password)`, `apiLogout()`, `apiMe()`. One shared helper does the
  `fetch` and returns the parsed JSON body. On 401 it redirects to `/`, except for `apiLogin`
  (wrong password must show a message, not reload).
- `frontend/login.html` + `frontend/js/login.js`: form (username, password, Sign in button, message area).
  On submit call `apiLogin`; success → `location = "/pos"`; failure → show `message` with `textContent`.
- `frontend/pos.html` + `frontend/js/pos.js`: placeholder only: "Signed in as <username> (<role>)" from
  `apiMe()` and a Log out button (`apiLogout()` then go to `/`). The real POS screen is feature 5.
- `frontend/css/style.css`: minimal styles for the login form (centered, readable). Full styling is feature 7.
- `tests/conftest.py`: add `seeded_app`/`auth_client` fixtures: seed the temp DB and return a client
  logged in as `cashier/cashier123`.
- `tests/test_auth.py`: the tests below.
- `docs/ARCHITECTURE.md`: no change expected (endpoints and pages are already listed).

## Test cases
- `POST /api/auth/login` with `cashier/cashier123` → 200, `status: true`, `data == {id, username: "cashier", role: "cashier"}`
  (no `password_hash`); then `GET /api/auth/me` returns the same user.
- Wrong password, and unknown username → both 401, `status: false`, same message "Invalid username or password".
- Missing `password`, empty `username`, or a non-JSON body → 400, `status: false`, `errors` not empty.
- User set to `active = 0` in the DB → login 401; and if already signed in, `GET /api/auth/me` → 401.
- Not signed in: `GET /api/auth/me` and `POST /api/auth/logout` → 401. Signed in, `POST /api/auth/logout` → 200,
  then `GET /api/auth/me` → 401.
- Pages: not signed in, `GET /pos` → 302 to `/`, `GET /` → 200 HTML. Signed in, `GET /` → 302 to `/pos`, `GET /pos` → 200 HTML.

## Out of scope
`role_required` and any admin-only behaviour, user management, password change/reset, "remember me",
login rate limiting or lockout, CSRF tokens, catalog/sale endpoints, the real POS screen, styling beyond
a usable login form, new dependencies.
