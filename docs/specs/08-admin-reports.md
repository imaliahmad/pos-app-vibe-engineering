# Admin reports
Status: done
Plan item: 8
Branch: feature/08-admin-reports

## Goal
An admin signs in and lands on `/admin`, where they see all-time sales per category and per item,
and the orders of today / the last 7 / the last 30 days with each order's lines in a modal.
Admins can no longer use the POS, and cashiers cannot reach anything under admin.

## Changes
- `app/auth.py`: add `role_required(role)` decorator (403 + `status: false` when the session role differs).
  Used together with `login_required`, which still returns 401 when signed out.
- `app/endpoints/page_endpoints.py`: `/` redirects a signed-in user by role (admin → `/admin`,
  cashier → `/pos`); `/pos` redirects admin to `/admin`; new `/admin` page (signed out → `/`, cashier → `/pos`).
- `app/endpoints/sale_endpoints.py`: `POST /api/sales` gets `role_required("cashier")` (admin → 403).
- `app/endpoints/admin_endpoints.py` (new): blueprint `/api/admin`, every route `login_required` + `role_required("admin")`.
- `app/handlers/report_handler.py` (new): validate `period` and order id, call service, respond.
- `app/services/report_service.py` (new): category/item reports, orders by period, one order with its lines.
- `app/repositories/report_repository.py` (new): SQL for quantity sold and revenue per category and per item.
- `app/repositories/sale_repository.py`: add `list_sales_since(days_back)`, `get_sale(sale_id)`, `list_sale_lines(sale_id)`.
- `app/__init__.py`: register the admin blueprint.
- `frontend/admin.html` (new): top bar (brand, user, Log out), three sections, `<dialog>` for order details.
- `frontend/js/admin.js` (new): load and render the three sections, period filter, open/close the dialog.
- `frontend/js/api.js`: add `apiCategoryReport()`, `apiItemReport()`, `apiOrders(period)`, `apiOrder(id)`.
- `frontend/js/login.js`: after login go to `/admin` for admin, `/pos` for cashier.
- `frontend/css/style.css`: new "Admin" section: page layout, report tables, filter buttons (selected state), dialog.
- `frontend/CLAUDE.md`: add `admin.html` + `js/admin.js` to the Files list.
- `app/CLAUDE.md`: add rule "Admin-only endpoints live under /api/admin/ and use role_required('admin')".
- `.claude/agents/code-reviewer.md`: add checklist item "admin endpoints and /admin page reject cashiers; POS rejects admin".
- `tests/test_access.py` (new): role redirects and 403s.
- `tests/test_reports.py` (new): report and order endpoints.
- `tests/test_auth.py`, `tests/test_pages.py`: adjust if needed for the role-based redirect.
  (No existing test uses the admin user on the POS; the only admin test is the seed check.)
- `docs/PLAN.md`: item 8 added, "Admin reports" removed from "Later" (done with this spec).
- `docs/ARCHITECTURE.md` (at finish): new endpoints, `/admin` page, access rules, admin screen layout.

### API shapes (all admin only)
| Method | Path | Data |
|---|---|---|
| GET | `/api/admin/reports/categories` | `[{id, name, quantity, revenue}]`, every category (0 if never sold), revenue desc then name |
| GET | `/api/admin/reports/items` | `[{id, name, category, quantity, revenue}]`, every item (0 if never sold), revenue desc then name |
| GET | `/api/admin/orders?period=today\|7d\|30d` | `[{id, created_at, cashier, total}]`, newest first. Missing/invalid period → 400 |
| GET | `/api/admin/orders/<id>` | `{id, created_at, cashier, total, lines: [{item_name, quantity, unit_price, line_total}]}`. Unknown → 404 |

Revenue = `SUM(sale_items.line_total)` (price at time of sale). Periods compare `date(created_at)`
with SQLite `date('now')`, the same clock that wrote `created_at`: today = same date,
7d = today and the 6 days before, 30d = today and the 29 days before. No time zone handling.

## Steps
1. ✅ Roles and access
   - Build: `role_required`; role-based redirects for `/`, `/pos`, `/admin`; placeholder `admin.html`
     (top bar with user + Log out, heading "Reports"); `POST /api/sales` cashier only; login.js redirects
     by role; the `app/CLAUDE.md` rule, `frontend/CLAUDE.md` file entry and code-reviewer checklist item.
     Tests in `tests/test_access.py`.
   - Check: `uv run flask --app app run --debug`. Sign in as `admin` / `admin123` → lands on
     http://127.0.0.1:5000/admin with the top bar. Type `/pos` in the address bar → back on `/admin`.
     Log out, sign in as `cashier` / `cashier123` → `/pos`; type `/admin` → back on `/pos`; saving an order still works.
2. ✅ Category and item reports API
   - Build: `report_repository`, `report_service`, `report_handler`, `admin_endpoints` with
     `GET /api/admin/reports/categories` and `GET /api/admin/reports/items`. Tests.
   - Check: as cashier save Cola ×2 + Water ×1. Sign in as admin, open
     http://127.0.0.1:5000/api/admin/reports/categories → Drinks has quantity 3 and revenue 400;
     open `/api/admin/reports/items` → Cola 2 / 300, category Drinks. As cashier the same URLs → 403 JSON.
3. ✅ Orders API
   - Build: `GET /api/admin/orders?period=...` and `GET /api/admin/orders/<id>` (sale repository
     additions, service, handler, routes). Tests.
   - Check: as admin open `/api/admin/orders?period=today` → your orders, newest first, with cashier
     and total; `?period=year` → 400 `status: false`; `/api/admin/orders/<id from the list>` → its lines;
     `/api/admin/orders/9999` → 404.
4. ✅ Admin page: Categories and Items
   - Build: api.js functions, `admin.js` renders the Categories table (category, quantity, revenue)
     and the Items table (item, category, quantity, revenue), money via `formatMoney`; table styles.
   - Check: sign in as admin → `/admin` shows both tables with the numbers from step 2;
     never-sold items show 0 and 0.00.
5. ✅ Admin page: Orders and order modal
   - Build: Today / Last 7 days / Last 30 days buttons (Today selected by default) and the orders table
     (order no., date/time, cashier, total; "No orders in this period" when empty). Clicking a row
     (or Enter on a focused row) opens a `<dialog>` with the lines (item, quantity, unit price,
     line total) and the order total; Close button and Esc close it. Dialog styles.
   - Check: on `/admin` the Today button is highlighted and today's orders are listed; click "Last 30 days"
     → highlight moves, list reloads; click an order → modal with its lines and total; Close / Esc closes it.

## Test cases
- Admin `POST /api/sales` with a valid order → 403, `status: false`, no sale saved; cashier → 201 (unchanged).
- Cashier `GET` each `/api/admin/*` endpoint → 403 `status: false`; signed out → 401.
- Pages: admin `GET /pos` → 302 `/admin`; admin `GET /` → 302 `/admin`; cashier `GET /admin` → 302 `/pos`;
  signed out `GET /admin` → 302 `/`; admin `GET /admin` → 200 with `<dialog`.
- Reports: sales Cola ×2 + Water ×1 and Cola ×1 → category Drinks quantity 4 / revenue 550,
  Snacks 0 / 0; item Cola quantity 3 / revenue 450 / category Drinks.
- Orders: one sale now and one with `created_at` 10 days ago → `today` 1, `7d` 1, `30d` 2, newest first;
  `period=year` or missing (bad input) → 400 `status: false`.
- `GET /api/admin/orders/<id>` → header + lines with prices as saved; `/api/admin/orders/9999` → 404.

## Out of scope
Editing categories/items (admin CRUD), CSV export, charts, pagination, time zones, custom date ranges,
sales-by-cashier report, admin making sales. Everything in `docs/PLAN.md` "Out of scope".
