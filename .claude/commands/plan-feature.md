---
description: Create the feature branch and write a spec for the next feature (or the one named) before any code
argument-hint: "[feature number or name]"
---

Plan a feature. Do not write or change any code.

1. Feature: $ARGUMENTS. If empty, use the first unticked item in `docs/PLAN.md`.
2. Branch:
   - Run `git status`. If there are uncommitted changes, stop and tell me.
   - If I'm on `main`: run `git pull`, then create and switch to `feature/NN-short-name`
     (NN = plan item number, e.g. `feature/06-save-sale`).
   - If I'm already on a feature branch, tell me which one and ask before continuing.
3. Read `docs/ARCHITECTURE.md` and only the existing files this feature touches.
4. Create `docs/specs/NN-short-name.md` from `docs/specs/_TEMPLATE.md`, with `Status: planned`.
5. Keep it small: list every file to change, 3–6 concrete test cases, and an out-of-scope line.
6. Stop and show me the branch name and the spec. Wait for my approval before implementing.