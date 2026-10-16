# OpenMontage

**MANDATORY: Read `AGENT_GUIDE.md` before responding to ANY user message.**

Do not act on the user's request until you have read AGENT_GUIDE.md.
It contains routing rules that determine your first action based on what the user asked.
Skipping it WILL cause you to take the wrong action.

There are no instructions in this file. All instructions are in AGENT_GUIDE.md.

## Factory Sessions (OpenMontage Factory)

Permanent-work sessions follow the master plan at
`docs/OPENMONTAGE_FACTORY_MASTER_PLAN_RU (1).md`. At the start of every such
session, in this order:

1. `docs/OPENMONTAGE_FACTORY_MASTER_PLAN_RU (1).md` — the task source.
2. `docs/OPENMONTAGE_RESUME.md` — current state and the exact next action.
3. `docs/OPENMONTAGE_WORK_LOG.md` — history of completed work.
4. Repository reality (git status, code, tests) outranks stale notes.

After every verified step: update `OPENMONTAGE_RESUME.md`, append a dated
entry to `OPENMONTAGE_WORK_LOG.md`, and commit on a working branch (never
`main`, never force-push). Strict zero-cost mode is the default: an unpriced
or un-named route is BLOCKED, not free (`lib/zero_cost_gate.py`).
