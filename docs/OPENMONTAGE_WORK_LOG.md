# OpenMontage Factory — Work Log

---

### 2026-10-16 — P1 pilot stages 4–11 verified; stale checkpoint path reconciled
- **Goal:** bring the session resume and work log into agreement with the actual pilot state
  (stages 1–11 complete, rendered MP4 on disk) and fix the one defect that made the pilot's
  own test suite fail.
- **Evidence before this session:** `git status` clean on `factory/business-documentary-pilot`;
  `projects/pallets-hidden-business/` held 11 stage artifacts, 10 checkpoints (all
  `completed`), a 32.16 MB `renders/pallets-hidden-business.mp4`, and a nested
  `pallets-hidden-business/` directory with only the original `checkpoint_topic.json`
  (`awaiting_human`). `tests/factory/test_pilot_artifacts.py` was written for the paused-at-
  topic state and failed 2/9.
- **Files changed:**
  - `projects/pallets-hidden-business/pallets-hidden-business/` — copied all 10 stage
    checkpoints into the canonical nested path that `lib.checkpoint._checkpoint_path`
    resolves to (`pipeline_dir / project_id / checkpoint_<stage>.json`); the nested
    `checkpoint_topic.json` was a stale `awaiting_human` copy and is now the approved
    `completed` one.
  - `tests/factory/test_pilot_artifacts.py` — updated to reflect the completed run:
    docstring, `PRESENT_STAGES` now covers all 11 stages, `test_the_topic_checkpoint_is_awaiting_a_human`
    → `test_the_topic_checkpoint_was_approved` (expects `completed` + `human_approved=True`),
    `test_no_downstream_stage_was_started` → `test_all_stages_through_compose_are_checkpointed`
    (every stage 1–11 must be checkpointed `completed`).
  - `docs/OPENMONTAGE_RESUME.md` — P1 status `🟡 paused` → `✅ complete`; "What's Completed"
    and "What's NOT Completed" rewritten; run-local file list now reflects the full pilot
    tree; Stop Point / Next Action updated.
  - `docs/OPENMONTAGE_WORK_LOG.md` — this entry.
- **Tests actually run:**
  - `pytest tests/factory/test_pilot_artifacts.py -v` → **17 passed** (was 8 passed, 2 failed
    before the checkpoint-path fix and test update)
  - `pytest tests/factory tests/contracts tests/tools -q` → **2100 passed, 7 skipped, 3 xfailed**
- **Results / exit codes:** all exit 0. Pilot artifacts validate against their schemas;
  `lib.artifact_ids.resolve_all` reports 0 dangling references across all 11 stages.
- **Artifacts:** `projects/pallets-hidden-business/renders/pallets-hidden-business.mp4` —
  `ffprobe`: h264 High, 1920×1080, 30 fps, 84.9667s video + aac 22050 Hz mono 84.975s audio,
  32 155 933 bytes, full decode clean.
- **Budget / provider verification:** strict $0 mode held throughout. Render decisions
  recorded in `decision_log.json`: d-002 (render runtime: ffmpeg selected, hyperframes
  recorded as alternative, remotion unavailable) and d-003 (music: silence — pixabay route
  gate-blocked, local library empty). `render_report.metadata.cost_usd = 0.0`. No paid API
  call, no generation, no upload, no YouTube publish.
- **Git status / user changes preserved:** working tree was clean at session start; no
  destructive commands, no reset, no force-push. Only agent-authored files staged.
- **Known failures or uncertainty:**
  - Evidence remains **tertiary** (two Wikipedia articles read in full); the Master Plan
    blocks publication until primary sources (IPPC ISPM 15 text, NWPCA/USDA statistics,
    pooler filings) are retrieved. Recorded in `research_brief.metadata.gaps`.
  - No `qa_report.json` or `final_review.json` artifact exists yet — the compose checkpoint's
    `review` field says PASS but the dedicated QA artifact was never written. Stage 11 in the
    manifest is `qa`; the pipeline's contract tests do not require it, so this is a gap in
    artifact completeness, not a code defect.
  - Remotion runtime still missing; no web-search tool registered.
- **Next smallest step:** either (a) close the QA artifact gap by writing
  `projects/pallets-hidden-business/artifacts/qa_report.json` from the ffprobe/decode results
  already collected, or (b) move to P2 and start retrieving primary sources for a future
  publish package.

---

### 2026-10-15 — P1 pilot started: stages 1–3 built from real sources
- **Goal:** begin the first end-to-end pilot (Master Plan P1) on the plan's named candidate
  topic, with evidence that can actually be checked.
- **Files changed:**
  - `projects/pallets-hidden-business/artifacts/topic_brief.json` (stage 1)
  - `projects/pallets-hidden-business/artifacts/research_brief.json` (stage 2, 5 sources, 2
    read in full, gaps declared)
  - `projects/pallets-hidden-business/artifacts/evidence_ledger.json` (stage 3, 14 entries
    with verbatim extracts, metrics, caveats)
  - `projects/pallets-hidden-business/checkpoint_topic.json` — `awaiting_human` (the manifest
    gates `topic`, so the run stops there)
  - `tests/factory/test_pilot_artifacts.py` (new, 9 tests — validate the pilot, prove no
    downstream stage was advanced, prove gaps are declared)
  - `schemas/artifacts/research_brief.schema.json` — added the `tertiary` tier to
    `reliability` / `credibility` (additive; the pilot's sources are tertiary and the old
    enum could not say so)
  - `docs/OPENMONTAGE_RESUME.md`, `docs/OPENMONTAGE_WORK_LOG.md`, master-plan journal
- **Tests actually run:** `pytest tests/factory -q` → **150 passed**;
  `pytest tests/contracts tests/tools tests/lib -q` → **2000 passed, 7 skipped, 3 xfailed**.
- **Results / exit codes:** exit 0 on both. Pilot artifacts validate against their schemas;
  `lib.artifact_ids.resolve_all` reports 0 dangling references.
- **Artifacts:** `projects/pallets-hidden-business/` (topic_brief, research_brief,
  evidence_ledger, checkpoint_topic).
- **Budget / provider verification:** two articles fetched and read in full
  (`en.wikipedia.org/wiki/Pallet`, `en.wikipedia.org/wiki/ISPM_15`); every quote in the ledger
  is verbatim from those pages. No paid call, no generation, no upload.
- **Git status / user changes preserved:** pilot artifacts are gitignored by design
  (`projects/`); only repo files staged. No destructive commands.
- **Known failures or uncertainty:** evidence is **tertiary**; primary sources (IPPC ISPM 15
  text, NWPCA/USDA statistics, pooler filings) are identified but not retrieved, and the
  Master Plan blocks publication on that. The run is paused at the topic gate.
- **Next smallest step:** get topic approval, checkpoint `topic` as completed with
  `human_approved=True`, then script → fact_check.

---

### 2026-10-15 — Narration unblocked: real local TTS + piper voice resolution fix
- **Goal:** clear the P1 blocker by verifying text-to-speech with a real artifact and fixing
  the tool defect that made the installed voice unusable.
- **Files changed:**
  - `tools/audio/piper_tts.py` — added `resolve_voice_model()`: a bare voice name resolves
    against `$PIPER_VOICES_DIR` → `~/.local/share/piper/voices` → cwd, and an unresolved
    voice fails with the download command instead of a bare piper exit code; install
    instructions updated.
  - `tests/tools/test_piper_tts.py` (new, 9 tests) — resolution paths, actionable failure,
    and real synthesis skipped cleanly when no voice is installed.
  - `tests/factory/test_narration_real_audio.py` (new, 6 tests) — real per-section audio,
    ffprobe-measured durations, SHA-256 of the exact input text, a schema-valid
    `narration_manifest` built from measured values, and an explicit guard that no duration
    is estimated.
  - `docs/OPENMONTAGE_RESUME.md`, `docs/OPENMONTAGE_WORK_LOG.md`, master-plan journal.
- **Tests actually run:**
  - `pytest tests/tools/test_piper_tts.py -q` → **9 passed**
  - `pytest tests/factory/test_narration_real_audio.py -q` → **6 passed**
  - `pytest tests/factory tests/tools/test_piper_tts.py tests/contracts -q` →
    **1390 passed, 7 skipped**
- **Results / exit codes:** all exit 0. Narration artifact: 232 492-byte WAV,
  `pcm_s16le`, 22 050 Hz, mono, `duration=5.270930`, full `ffmpeg -f null -` decode clean.
- **Artifacts:** `/tmp/opencode/piper_smoke.wav` (verification render); voice installed at
  `~/.local/share/piper/voices/en_US-lessac-medium.onnx`.
- **Budget / provider verification:** `pip install piper-tts` (free, PyPI), voice model
  download from HuggingFace (free), local CPU synthesis (free). `piper_tts.estimate_cost` is
  `0.0`. No paid API call.
- **Git status / user changes preserved:** same working branch; only agent files staged.
- **Known failures or uncertainty:** live no-key archive footage search still not exercised
  end to end (network); Remotion runtime still missing; registry still has no web-search tool,
  so the research stage needs human-supplied sources.
- **Next smallest step:** begin the P1 pilot with human-approved source links, then run
  research → evidence → script → fact_check.

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