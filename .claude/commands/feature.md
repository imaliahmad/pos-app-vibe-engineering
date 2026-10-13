---
description: Run the full feature loop (branch → spec → 5-step build → review → finish) with approval gates
argument-hint: "[feature number or name]"
---

# Feature loop

Feature: $ARGUMENTS. If empty, use the first unticked item in `docs/PLAN.md`.

Work through Phases 0–4 in order. At every **GATE**, stop completely and wait for my reply.
Never skip a gate, never combine two gates in one message, even if everything looks fine.

## How to read my replies at a gate
- `ok`, `yes`, `continue`, `approved` → go on to the next step.
- `stop` → stop work, summarize where we are (phase, step, branch, uncommitted files), and wait.
- Anything else → treat it as a change request or bug report. Fix it, run the tests,
  then show the same gate again. Do not move on until I reply `ok`.

---

## Phase 0: Check the starting state
1. Run `git status` and `git branch --show-current`.
2. If there are uncommitted changes: stop and list them. Do not continue until I decide.
3. If I'm on a `feature/...` branch and `docs/specs/` has a spec with `Status: in progress`
   for this feature: tell me which step it reached and ask whether to **resume** or **start over**.
4. Otherwise continue to Phase 1.

---

## Phase 1: Branch and spec

### 1.1 Create the branch
1. Switch to `main` and run `git pull`.
2. Create and switch to `feature/NN-short-name`
   (NN = the plan item number with two digits, e.g. `feature/06-save-sale`).

### 1.2 Write the spec
1. Read `docs/PLAN.md`, `docs/ARCHITECTURE.md`, and only the existing files this feature touches.
2. Create `docs/specs/NN-short-name.md` from `docs/specs/_TEMPLATE.md` with `Status: planned`.
3. Fill in every section:
   - **Goal:** 1–2 sentences.
   - **Changes:** every file to create or change, one line each.
   - **Steps:** split the work into **5 steps**. Each step must be small, build on the previous one,
     and leave the app runnable. For each step write:
     - `Build:` what gets implemented
     - `Check:` exact manual test (URL, what to click or run, expected result)
     If 5 steps would be artificial for this feature, propose fewer and say why.
   - **Test cases:** 3–6 concrete automated test cases (input → expected result), including one bad input.
   - **Out of scope:** what this feature will not do (check `docs/PLAN.md` "Out of scope").

### GATE 1: Spec approval
Show me:
- the branch name
- the full spec
Then ask: **"Approve this spec? Reply `approved` or tell me what to change."**
If I request changes, update the spec and show GATE 1 again.

---

## Phase 2: Build in steps

### 2.1 Prepare
1. Open the approved spec at `docs/specs/NN-short-name.md`. If it doesn't exist or is not approved, stop.
2. Set `Status: in progress` in the spec.

### 2.2 For each step in the spec's `## Steps` section, in order:
1. Announce: **"Step X of N: <step name>"**.
2. Implement only what that step's `Build:` line says. Do not start the next step.
3. Follow the project rules (`CLAUDE.md`, `app/CLAUDE.md`, `frontend/CLAUDE.md`) and the
   `add-endpoint` skill for any API endpoint.
4. Add or update automated tests for anything testable in this step.
5. Run `uv run pytest -q`. If tests fail, fix the code (not the tests, unless a test is wrong)
   and run them again. If the same failure survives 3 attempts, stop and report.
6. In the spec, mark the step as done (e.g. `1. ✅ ...`).

#### GATE 2 (after every step): Manual test
Show me:
- **Done:** what was built in this step (2–4 bullets)
- **Files changed:** list
- **Tests:** result of `uv run pytest -q` (e.g. "24 passed")
- **Please test:** the step's `Check:` instructions as numbered actions, including the command
  to start the app if needed (`uv run flask --app app run --debug`) and the URL
Then ask: **"Step X works? Reply `ok` to continue, or describe the problem."**
- If I describe a problem: reproduce it from my description, fix it, run the tests,
  and show GATE 2 for the same step again.
- If I reply `ok`: move to the next step.

---

## Phase 3: Review

### 3.1 Run the review
Follow `.claude/commands/review.md` exactly: use the **code-reviewer** agent to review all
changes on this branch compared with `main` (`git diff main...HEAD` plus uncommitted changes)
against the project rules and this feature's spec.

### 3.2 Handle "Must fix"
1. Fix every **Must fix** item yourself.
2. Run `uv run pytest -q` again.
3. If a Must fix item needs a change outside the approved spec, do not fix it; list it for GATE 3.

### GATE 3: Review decisions
Show me:
- **Must fix:** each item and what you changed (or "none")
- **Should fix:** a numbered list; for each item: file and line, the problem in one line,
  your recommendation (**fix** or **skip**) and why in one line
- **Looks good:** short list
Then ask: **"Which Should fix items should I apply? Reply with numbers (e.g. `1, 3`), `all`, or `none`."**
Apply only what I choose, run the tests, and show me a short summary of what changed.

---

## Phase 4: Finish

### 4.1 Final checks
1. Run `git branch --show-current`. If it is `main`, stop. Features are never committed to `main`.
2. Run `uv run pytest -q`. Stop if anything fails.

### 4.2 Update the docs
1. Tick the feature in `docs/PLAN.md`.
2. Set the spec to `Status: done`.
3. Update `docs/ARCHITECTURE.md` if tables, endpoints, pages or screens changed. If nothing changed, say so.

### GATE 4: Commit
Show me:
- `git status`
- the proposed commit message: a short title (`Feature NN: <name>`) and 3–5 bullet points
Then ask: **"Commit and push this? Reply `yes`, or tell me what to change."**

### 4.3 After I reply `yes`
1. Commit on the feature branch.
2. Push: `git push -u origin feature/NN-short-name`.
3. Give me, ready to paste into GitHub:
   - **PR title**
   - **PR description** in markdown: what changed, how to test it manually (from the spec's Check lines),
     automated test result, and the review summary from Phase 3
4. End with these reminders:
   - Open the PR on GitHub (base `main` ← compare `feature/NN-short-name`), review, and merge it yourself.
   - After merging: `git switch main`, `git pull`, `git branch -d feature/NN-short-name`.
   - Then `/clear` before the next `/feature`.

---

## Stop immediately and report if
- The same test failure survives 3 fix attempts
- The work needs a file or change that is not in the approved spec
- Any action would commit to `main`, merge, force-push, reset, or delete a branch
- My reply is unclear: ask, don't guess

## Never
Merge pull requests, push to `main`, force-push, skip a gate, or start the next step without my `ok`.