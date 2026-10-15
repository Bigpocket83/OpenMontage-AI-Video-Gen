# OpenMontage Factory — Work Log

---

### 2026-10-15 — Business-documentary pipeline implemented (P0.3 / P0.5)
- **Goal:** implement the Master Plan's 12-stage business-documentary pipeline, its 13 director
  skills, the artifact schemas it needs, and the governance gates ($0 mode, ID resolution).
- **Files changed:**
  - `pipeline_defs/business-documentary.yaml` (new, 12 stages, budget 0.0)
  - `skills/pipelines/business-documentary/*` (13 new director skills)
  - `schemas/artifacts/`: 7 new schemas + additive extensions to `script`, `scene_plan`,
    `asset_manifest`, `research_brief`, `render_report`, `publish_log`; registry updated
  - `lib/zero_cost_gate.py` (new) — strict $0 gate, failure taxonomy, search-stats summary
  - `lib/artifact_ids.py` (new) — cross-artifact ID resolution
  - `tests/factory/` (new, 7 files, 135 tests)
  - `AGENTS.md` — factory session reading order
- **Tests actually run:**
  - `pytest tests/factory -q` → **135 passed**
  - `pytest tests/contracts -q` → **1241 passed, 7 skipped**
  - `pytest tests/qa tests/lib -q` → **58 passed, 2 skipped**
  - `pytest tests/styles tests/pipelines -q` → collected before ffmpeg; single test file
- **Results / exit codes:** all green above. Two pre-existing failures
  (`tests/contracts/test_seedance_ark_video.py`) were **environment-caused** (missing
  ffmpeg/ffprobe) and cleared once ffmpeg was installed.
- **Artifacts:** real diagram render proven (8.5 KB PNG written by `DiagramGen`); full
  artifact chain checkpointed through `lib.checkpoint` in `tests/factory/test_dry_run_chain.py`.
- **Budget / provider verification:** strict $0 mode enforced in code and proven by tests
  (unknown cost / unknown route / unapproved paid call / unavailable tool → BLOCKED;
  `reroute_allowed()` always False). Only free operations ran: apt/pip installs, local
  diagram render. No paid API call, no generation, no upload.
- **Git status / user changes preserved:** no destructive commands, no reset/clean, no
  force-push. Only agent-authored files staged.
- **Known failures or uncertainty:**
  - No TTS synthesizer on the machine (`piper_tts` unavailable) — narration stage cannot
    produce audio; must fail closed.
  - Remotion runtime missing (`remotion-composer/node_modules` empty); ffmpeg + hyperframes
    available.
  - No web-search tool registered — research depends on human-supplied sources.
  - Full-suite grouped run was in progress at session end.
- **Next smallest step:** unblock a local narration path (piper install feasibility check on
  Python 3.14), then start the P1 pilot topic: research → evidence → script → fact_check with
  real sources.

---

### 2026-10-14 — Initial Audit & Tracking Setup
- **Goal:** Establish session continuity per Master Plan; audit current repo state; create tracking files
- **Files changed:** 
  - Created `docs/OPENMONTAGE_RESUME.md`
  - Created `docs/OPENMONTAGE_WORK_LOG.md` (this file)
- **Tests actually run:** None (preflight capability check only)
- **Results:** Preflight shows only local tools available; no ffmpeg, no TTS, no video generation APIs configured
- **Artifacts:** RESUME.md, WORK_LOG.md
- **Budget / provider verification:** $0 mode confirmed — only free local providers available
- **Git status:** Clean, on main, up to date with origin/main
- **Known failures/uncertainty:** 
  - No `tests/factory/` directory exists (referenced in Master Plan but not in repo)
  - No `business-documentary` pipeline or skills exist
  - No `--db-path` file found
- **Next smallest step:** Create business-documentary pipeline manifest (12 stages) and 13 director skills

---