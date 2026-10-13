# Styling pass
Status: done
Plan item: 7
Branch: feature/07-styling

## Goal
The login page and POS screen look clean, consistent and easy to read, with large touch-friendly
buttons and clear feedback (selected, pressed, disabled, success, error). No behaviour changes.

## Changes
- `frontend/css/style.css`: rewrite into sections: design tokens (CSS variables on `:root` for
  colours, spacing, radius, font sizes), base, buttons, login, top bar, POS layout, category/item
  buttons, order panel, messages.
- `frontend/login.html`: add a short subtitle under the title ("Sign in to start selling"); no other changes.
- `frontend/pos.html`: top bar gets the app name (`<span class="brand">Quick POS</span>`) on the left,
  user and Log out on the right; error `#message` gets `role="alert"`.
- `frontend/js/pos.js`: class names only, no logic changes: quantity span gets
  `order-line-qty`; item name gets `item-name`; the − / + / ✕ buttons get `aria-label`s
  ("Decrease", "Increase", "Remove") because they show only a symbol.
- `tests/test_pages.py` (new): checks that pages and the stylesheet are served and wired up.

## Steps
1. ✅ Design tokens and base styles
   - Build: `:root` variables (colours: primary blue, success green, danger red, text, muted, border,
     page and panel backgrounds; spacing scale; radius; font sizes). Base `body`, headings, inputs and
     one shared button style (border, radius, background, hover, `:active` press effect,
     `:focus-visible` ring, `:disabled`). Existing rules switched to use the variables.
     Add `tests/test_pages.py` with the stylesheet tests.
   - Check: `uv run flask --app app run --debug`, open http://127.0.0.1:5000. Both pages still work;
     all buttons share one look; Tab through the login form shows a clear focus ring; pressing a
     button gives a visible press effect.
2. ✅ Login page
   - Build: centred card with shadow, title + subtitle, full-width inputs and a full-width primary
     Sign in button, error text styled in the danger colour.
   - Check: open http://127.0.0.1:5000. Card is centred; sign in with `cashier` / `wrong` → red
     error under the button; sign in with `cashier` / `cashier123` → goes to `/pos`.
3. ✅ Top bar and POS layout
   - Build: top bar with "Quick POS" brand left, "Signed in as …" and an outlined Log out button right.
     Three column panels with consistent padding, rounded corners, light border, and small uppercase
     column headings. Columns keep `1fr 2fr 2fr`; lists scroll inside their column.
   - Check: sign in as `cashier` / `cashier123`. Top bar shows the brand on the left and the user and
     Log out on the right; three tidy panels; at 1366×768 (browser dev tools → responsive) the page
     itself does not scroll. Log out still returns to the login page.
4. ✅ Category and item buttons
   - Build: category buttons full width, left aligned, clear selected state (primary background,
     white text). Items shown as a 2-column grid of large tiles (min 72px tall) with the name on top
     and the price in bold below.
   - Check: on `/pos`, the first category is highlighted; click another → highlight moves and items
     change; items appear as 2-column tiles; tapping a tile adds it to the order.
5. ✅ Order panel
   - Build: order lines with name, `x2` quantity, right-aligned line total and three 48px round-ish
     buttons (✕ in danger colour), light separators between lines. Big TOTAL row, full-width green
     SAVE ORDER (64px) with a clear disabled look; success confirmation as a green box, error message
     as a red box (both hidden when empty).
   - Check: add Cola ×2 and one other item; − / + / ✕ work and look aligned; SAVE ORDER is faded when
     the order is empty; save → green box "Order #N saved, total …" and the order clears; stop the
     server and click save with items → red box with the error. At 1366×768 with 8+ lines, only the
     order list scrolls.

## Test cases
- `GET /css/style.css` → 200, content type `text/css`, body contains `:root` and `--color-primary`.
- `GET /` (signed out) → 200 and contains `href="/css/style.css"` and `class="login"`.
- `GET /pos` (signed in) → 200 and contains `href="/css/style.css"`, `class="brand"`
  and `role="alert"`.
- `GET /css/missing.css` (bad input) → 404.

## Out of scope
Dark mode, phone/portrait layouts (target is 1366×768 and larger), animations beyond a simple press
effect, icons or web fonts, CSS or JS libraries, any change to behaviour, API or data. Everything in
`docs/PLAN.md` "Out of scope".
