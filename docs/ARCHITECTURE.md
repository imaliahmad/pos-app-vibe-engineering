# Quick POS: Architecture

## Overview
```
Browser (HTML/CSS/JS)  ──fetch JSON──▶  Flask  ──▶  endpoints → handlers → services → repositories  ──▶  SQLite
        ▲                                 │
        └──── serves frontend/ pages ─────┘
```
Login state: Flask session cookie (`user_id`, `role`).
Roles: a cashier uses the POS only; an admin uses the reports page only (`/admin`, `/api/admin/*`).
The order is built in browser memory and sent once, on Save.

## Data model
| Table | Columns |
|---|---|
| `users` | id, username (unique), password_hash, role (`admin` \| `cashier`), active (0/1), created_at |
| `categories` | id, name (unique), active (0/1) |
| `items` | id, category_id → categories, name, price (INTEGER, smallest unit), active (0/1) |
| `sales` | id, user_id → users, total (INTEGER), created_at |
| `sale_items` | id, sale_id → sales, item_id → items, item_name, unit_price, quantity, line_total |

`sale_items` copies `item_name` and `unit_price` at the time of sale, so old sales stay
correct if an item's name or price changes later.

CHECK constraints in `schema.sql`:
| Table | Constraint |
|---|---|
| `users` | `role IN ('admin', 'cashier')`, `active IN (0, 1)` |
| `categories` | `active IN (0, 1)` |
| `items` | `price >= 0`, `active IN (0, 1)` |
| `sales` | `total >= 0` |
| `sale_items` | `unit_price >= 0`, `quantity BETWEEN 1 AND 999`, `line_total >= 0` |

## API
| Method | Path | Auth | Body → Data |
|---|---|---|---|
| POST | `/api/auth/login` | none | `{username, password}` → `{id, username, role}` |
| POST | `/api/auth/logout` | login | — |
| GET | `/api/auth/me` | login | → `{id, username, role}` |
| GET | `/api/categories` | login | → `[{id, name}]` |
| GET | `/api/categories/<id>/items` | login | → `[{id, name, price}]` |
| POST | `/api/sales` | cashier | `{lines: [{item_id, quantity}]}` → `{sale_id, total, created_at}` |
| GET | `/api/admin/reports/categories` | admin | → `[{id, name, quantity, revenue}]` all categories, all time, revenue desc |
| GET | `/api/admin/reports/items` | admin | → `[{id, name, category, quantity, revenue}]` all items, all time, revenue desc |
| GET | `/api/admin/orders?period=today\|7d\|30d` | admin | → `[{id, created_at, cashier, total}]` newest first; bad period → 400 |
| GET | `/api/admin/orders/<id>` | admin | → `{id, created_at, cashier, total, lines: [{item_name, quantity, unit_price, line_total}]}`; unknown → 404 |

All responses: `{"status", "message", "data", "errors"}`.
Auth `cashier` / `admin`: `login_required` + `role_required(role)`; signed out → 401, wrong role → 403.

## Report rules
- Quantity and revenue come from `sale_items` (`SUM(line_total)`, the price at the time of sale).
- Periods use dates as stored (SQLite `date('now')`, no time zones): `today` = today,
  `7d` = today and the 6 days before, `30d` = today and the 29 days before.

## Save sale rules
- At least one line. Quantity is a whole number from 1 to 999.
- Each item must exist and be active.
- The server reads prices from the database and calculates line totals and the sale total.
- Header and lines are saved in one transaction.

## Pages
| URL | File | Access |
|---|---|---|
| `/` | `frontend/login.html` | public; a signed-in user is redirected to their page (admin → `/admin`, cashier → `/pos`) |
| `/pos` | `frontend/pos.html` | cashier; signed out → `/`, admin → `/admin` |
| `/admin` | `frontend/admin.html` | admin; signed out → `/`, cashier → `/pos` |
| `/css/*`, `/js/*` | `frontend/css/`, `frontend/js/` | public static files (served by `page_endpoints.py`) |

## POS screen layout
```
┌──────────────┬────────────────────────┬──────────────────────┐
│ Categories   │ Items of category      │ Order                │
│ [Drinks]     │ [Cola 1.50] [Water ..] │ Cola   x2   3.00  [−][+][✕]
│ [Snacks]     │ ...                    │ ...                  │
│ [Bakery]     │                        │ TOTAL        12.50   │
│              │                        │ [   SAVE ORDER   ]   │
└──────────────┴────────────────────────┴──────────────────────┘
```

## Admin reports page
```
┌ Quick POS ─────────────────────────── Signed in as admin  [Log out] ┐
│ Reports                                                              │
│ CATEGORIES   Category | Quantity | Revenue                           │
│ ITEMS        Item | Category | Quantity | Revenue                    │
│ ORDERS       [Today] [Last 7 days] [Last 30 days]                    │
│              Order no. | Date/time | Cashier | Total   (click a row) │
└──────────────────────────────────────────────────────────────────────┘
Clicking an order opens a <dialog>: Item | Quantity | Unit price | Line total, then TOTAL. [Close]
```

## Planned backend files
```
app/__init__.py, db.py, schema.sql, seed.py, auth.py, responses.py
app/endpoints/    admin_endpoints.py, auth_endpoints.py, catalog_endpoints.py, sale_endpoints.py, page_endpoints.py
app/handlers/     auth_handler.py, catalog_handler.py, report_handler.py, sale_handler.py
app/services/     auth_service.py, catalog_service.py, report_service.py, sale_service.py
app/repositories/ user_repository.py, category_repository.py, item_repository.py, report_repository.py, sale_repository.py
tests/            conftest.py (temp DB + logged-in client), test_access.py, test_auth.py, test_catalog.py, test_reports.py, test_sales.py
```
