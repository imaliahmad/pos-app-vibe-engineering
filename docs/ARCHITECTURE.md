# Quick POS: Architecture

## Overview
```
Browser (HTML/CSS/JS)  ──fetch JSON──▶  Flask  ──▶  endpoints → handlers → services → repositories  ──▶  SQLite
        ▲                                 │
        └──── serves frontend/ pages ─────┘
```
Login state: Flask session cookie (`user_id`, `role`).
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
| POST | `/api/sales` | login | `{lines: [{item_id, quantity}]}` → `{sale_id, total, created_at}` |

All responses: `{"status", "message", "data", "errors"}`.

## Save sale rules
- At least one line. Quantity is a whole number from 1 to 999.
- Each item must exist and be active.
- The server reads prices from the database and calculates line totals and the sale total.
- Header and lines are saved in one transaction.

## Pages
| URL | File | Access |
|---|---|---|
| `/` | `frontend/login.html` | public; redirects to `/pos` if already signed in |
| `/pos` | `frontend/pos.html` | signed in (admin or cashier) |

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

## Planned backend files
```
app/__init__.py, db.py, schema.sql, seed.py, auth.py, responses.py
app/endpoints/    auth_endpoints.py, catalog_endpoints.py, sale_endpoints.py, page_endpoints.py
app/handlers/     auth_handler.py, catalog_handler.py, sale_handler.py
app/services/     auth_service.py, catalog_service.py, sale_service.py
app/repositories/ user_repository.py, category_repository.py, item_repository.py, sale_repository.py
tests/            conftest.py (temp DB + logged-in client), test_auth.py, test_catalog.py, test_sales.py
```
