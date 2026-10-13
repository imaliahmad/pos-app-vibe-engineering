# Save sale
Status: done
Plan item: 6
Branch: feature/06-save-sale

## Goal
The cashier taps Save on the POS screen; the server prices the order from the database,
stores the sale and its lines in one transaction, and the screen shows the order number
and total, then clears for the next customer.

## Changes
- `app/db.py`: add `transaction()` context manager (`BEGIN IMMEDIATE`, commit or roll back). (Added in review.)
- `app/repositories/item_repository.py`: add `get_active_items(item_ids)` → `{id: {id, name, price}}`
  in one query (`json_each(?)` keeps the SQL static).
- `app/repositories/sale_repository.py` (new): `insert_sale(user_id, total, lines)` inserts the
  `sales` row and all `sale_items` rows, returns `{sale_id, total, created_at}`. Caller runs it in `transaction()`.
- `app/services/sale_service.py` (new): `create_sale(user_id, lines)` → `(data, error)`.
  Rejects duplicate `item_id`s and unknown/inactive items; inside one `transaction()` reads the prices from the DB,
  calculates `line_total = price * quantity` and the sale total; copies `item_name`/`unit_price`.
- `app/handlers/sale_handler.py` (new): `handle_create_sale()` validates the body
  (JSON object, `lines` a non-empty list, each line an object with integer `item_id` and integer
  `quantity` 1–999; booleans rejected; any extra fields such as `price` ignored), calls the service,
  responds with `success(..., "Sale saved", 201)` or `failure(...)` (400).
- `app/endpoints/sale_endpoints.py` (new): `POST /api/sales` with `login_required`; user id from the session.
- `app/__init__.py`: register the sales blueprint.
- `frontend/js/api.js`: add `apiSaveSale(lines)` → `POST /api/sales`; on a 401 redirect return an empty message (no error flash).
- `frontend/pos.html`: add `#save-button` ("SAVE ORDER") under the total and a `#sale-confirmation` line.
- `frontend/js/pos.js`: `saveOrder()` sends only `{item_id, quantity}` per line; on success shows
  "Order #N saved, total X.XX" and clears the order; on failure shows `message` and keeps the order.
  Save is disabled when the order is empty and while a save is in progress. Adding an item
  clears the old confirmation.
- `frontend/css/style.css`: basic Save button (large, full width) and confirmation text style.
- `tests/test_sales.py` (new): API tests below.
- `tests/test_auth.py`: assert `/pos` contains `id="save-button"`.
- `docs/ARCHITECTURE.md`: `POST /api/sales` row already exists; update only if the response differs.

## Steps
4 steps instead of 5: the backend splits naturally into "rules + storage" and "HTTP endpoint",
and the frontend into "save works" and "screen resets / error handling". A fifth step would be filler.

1. ✅ Sale repository and service
   - Build: `get_active_item`, `sale_repository.insert_sale` (one transaction), `sale_service.create_sale`
     with all pricing and item rules. No endpoint yet.
   - Check: `uv run pytest -q tests/test_sales.py` → all pass; app still starts and `/pos` works as before.
2. ✅ `POST /api/sales` endpoint
   - Build: `sale_handler.py` (input validation), `sale_endpoints.py`, register blueprint.
   - Check: start the app, sign in as `cashier` at http://127.0.0.1:5000, open the browser console on `/pos` and run
     `await apiRequest("POST", "/api/sales", {lines: [{item_id: 1, quantity: 2, price: 1}]})`
     → `status: true`, `data.sale_id` is a number, `data.total` = 2 × the item's real DB price (the `price: 1` is ignored).
     Then `await apiRequest("POST", "/api/sales", {lines: []})` → `status: false` with a message.
3. ✅ Save button sends the order
   - Build: `apiSaveSale`, `#save-button` and `#sale-confirmation` in `pos.html`, `saveOrder()` in `pos.js`,
     basic CSS. On success show "Order #N saved, total X.XX" (total from the server).
   - Check: on `/pos` add Cola ×2 and one other item, tap SAVE ORDER → "Order #N saved, total …"
     matches the on-screen total. Saving again creates the next order number.
4. ✅ Clear screen and handle errors
   - Build: clear the order after a successful save; disable Save when the order is empty and while saving;
     on failure show the message and keep the order; adding an item clears the old confirmation.
   - Check: after saving, order shows "No items yet" and Save is disabled; add an item → confirmation
     disappears and Save is enabled. Stop the server, tap Save → "Cannot reach the server", order lines stay.

## Test cases
- Cola ×2 + Water ×1 → 201, `status: true`, `total` = 2×150 + water price; one `sales` row, two
  `sale_items` rows with `item_name`, `unit_price`, `line_total` copied correctly, `user_id` = cashier.
- Line with `price: 1` in the body → total still uses the DB price.
- `{"lines": []}`, `quantity: 0`, `quantity: 1000`, `quantity: "2"`, missing body → 400, `status: false`, no sale stored.
- Inactive item or unknown `item_id` → 400 "Item not found or inactive", no sale stored.
- Same `item_id` twice → 400, no sale stored.
- Not logged in → 401.
- Repository: a line that breaks a CHECK constraint mid-insert → exception, and no `sales` row remains (rollback).

## Out of scope
Discounts, taxes, payment methods, cash received/change, printed receipts, stock tracking,
returns/voids, editing or listing saved sales, reports (later), keeping the order after page reload,
polished styling (feature 7), new dependencies.
