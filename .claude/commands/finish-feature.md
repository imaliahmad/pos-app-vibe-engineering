---
description: Close out the current feature on its branch and prepare the pull request
---

1. Run `git branch --show-current`. If it is `main`, stop and tell me. Features are never committed to `main`.
2. Run `uv run pytest -q`. Stop if anything fails.
3. Tick the feature in `docs/PLAN.md`.
4. Set the spec in `docs/specs/` to `Status: done`.
5. Update `docs/ARCHITECTURE.md` if tables, endpoints or screens changed.
6. Show me `git status` and a proposed commit message. Commit only after I confirm.
7. After the commit, push the branch: `git push -u origin <branch>`.
8. Give me a pull request title and description (markdown) I can paste into GitHub:
   what changed, how to test it manually, and the review summary from `/review` if we ran it.