# Frontend rules (frontend/)

Plain HTML, CSS and JavaScript. No frameworks, no CDN libraries, no build step.

## Files
- `login.html` + `js/login.js`   login form
- `pos.html` + `js/pos.js`       the POS screen
- `admin.html` + `js/admin.js`   the admin reports page
- `js/api.js`                    the ONLY file that calls `fetch()`; one function per endpoint
- `css/style.css`                all styles

## Rules
- Every backend call goes through `js/api.js`. Pages never call `fetch()` directly.
- The current order lives in one JS object in `pos.js` (e.g. `order = { lines: [] }`).
  Every change (add, quantity, remove) updates that object, then calls one `render()` function.
- Show data with `textContent` or `createElement`, never `innerHTML` with server data.
- Money arrives as integers. Format it in one helper (`formatMoney`) for display only.
- If an API call returns `status: false`, show `message` to the user. If it returns 401, go to login.
- Big, touch-friendly buttons. The POS screen must work without scrolling on a 1366×768 screen.
- Show a total as a convenience, but the saved total always comes from the server.
