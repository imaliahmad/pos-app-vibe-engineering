# Quick POS: Plan

## Goal
A cashier can log in, build an order by tapping category → item, adjust quantities,
remove lines, and save the order. Cash only, no cart persistence, no receipts printed.

## Features (build in this order, one per session)
- [x] 1. Skeleton: app factory, `responses.py`, `db.py`, `schema.sql`, `flask init-db`, one passing test
- [x] 2. Seed: `flask seed` adds 3 categories, ~10 items, users `admin/admin123` and `cashier/cashier123` (local dev only)
- [x] 3. Login: login/logout/me API, `login.html`, `/pos` redirects to login when not signed in
- [ ] 4. Catalog API: list active categories, list active items of a category
- [ ] 5. POS screen: categories → items → order lines (add, change quantity, remove, running total). Frontend only, no saving yet
- [ ] 6. Save sale: `POST /api/sales`, server recalculates total, Save button, on-screen confirmation (order no., total), clear screen
- [ ] 7. Styling pass: clean, readable, touch-friendly

## Later (not now)
- Admin reports (daily sales, sales by item, sales by cashier)

## Out of scope
Discounts, taxes, card or other payment methods, cash received/change, printed receipts,
stock tracking, returns/voids, editing saved sales, customers, multiple shops,
admin CRUD screens, JavaScript frameworks, Docker, deployment.
