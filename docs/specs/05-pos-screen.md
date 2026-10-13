# POS screen
Status: done
Plan item: 5

## Goal
A signed-in cashier sees categories, taps one to see its items, taps items to build an order,
changes quantities with − / +, removes lines, and sees a running total. Nothing is saved yet.

## Changes
- `frontend/js/api.js`: add `apiCategories()` → `GET /api/categories` and
  `apiCategoryItems(categoryId)` → `GET /api/categories/<id>/items`.
- `frontend/pos.html`: replace the placeholder comment with three columns:
  `#categories` (category buttons), `#items` (item buttons), and an order panel with
  `#order-lines`, `#order-total`, and a `#message` line for errors. No Save button yet (feature 6).
- `frontend/js/pos.js`: replace the placeholder (keep the current-user line and logout):
  - `order = { lines: [] }`, each line `{item_id, name, price, quantity}`. `name`/`price` are for display only.
  - `loadCategories()` on start; clicking a category → `loadItems(categoryId)`, highlights the selected one.
    Auto-select the first category on load.
  - `addItem(item)`: if the item is already a line, quantity + 1; else push a new line with quantity 1.
  - `changeQuantity(itemId, delta)`: − at quantity 1 removes the line; + is capped at 999.
  - `removeLine(itemId)`.
  - One `render()` that redraws order lines (`name  xQty  lineTotal  [−][+][✕]`) and the total,
    using `createElement` / `textContent` only. Empty order shows "No items yet".
  - `formatMoney(amount)`: integer → `"12.50"` (e.g. `(amount / 100).toFixed(2)`, display only).
  - `status: false` from the API → show `message` in `#message`.
- `frontend/css/style.css`: three-column grid layout under the top bar, large touch buttons,
  selected-category highlight; fits 1366×768 without page scrolling (lists scroll inside their column).
  Basic only; the styling pass is feature 7.
- `tests/test_auth.py`: extend `test_pages_when_signed_in` to assert `/pos` contains
  `id="categories"`, `id="items"`, `id="order-lines"`, `id="order-total"`.
- `docs/ARCHITECTURE.md`: no change expected (screen and endpoints already described).

## Test cases
Automated:
- Signed in, `GET /pos` → 200 and the HTML contains the four container ids above.

Manual (browser, after `seed`, signed in as `cashier`):
- Open `/pos` → 3 categories shown; first one selected and its items shown with prices like `1.50`.
- Tap Cola twice → one line `Cola x2 3.00`, total `3.00`. Tap another item → second line, total updates.
- Tap − on a quantity-1 line → line is removed; ✕ removes a line of any quantity; empty order shows "No items yet".
- Switch category → item list changes, order lines stay.
- Stop the server and tap a category → "Cannot reach the server" shown, page doesn't break.

## Out of scope
Saving the order, Save button, `/api/sales` (feature 6); polished styling (feature 7);
typing a quantity, item search, keeping the order after page reload, discounts/taxes,
JS test framework or any new dependency.
