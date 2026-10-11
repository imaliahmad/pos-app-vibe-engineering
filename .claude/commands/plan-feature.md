---
description: Write a spec for the next feature (or the one named) before any code
argument-hint: "[feature number or name]"
---

Plan a feature. Do not write or change any code.

1. Feature: $ARGUMENTS. If empty, use the first unticked item in `docs/PLAN.md`.
2. Read `docs/ARCHITECTURE.md` and only the existing files this feature touches.
3. Create `docs/specs/NN-short-name.md` from `docs/specs/_TEMPLATE.md`
   (NN = plan item number), with `Status: planned`.
4. Keep it small: list every file to change, 3–6 concrete test cases, and an out-of-scope line.
5. Stop and show me the spec. Wait for my approval before implementing.
