# OpenMontage Factory — Session Resume State

**Last Updated:** 2026-10-15
**Git Branch:** `factory/business-documentary-pilot` (working branch; `main` untouched)
**Last Commit:** `40f1910` — feat(business-documentary): 12-stage evidence-first factory pipeline
**Remote:** pushed and confirmed to `origin/factory/business-documentary-pilot`
**Master Plan:** docs/OPENMONTAGE_FACTORY_MASTER_PLAN_RU (1).md v1.0

---

## Current Goal

Implement the **business-documentary pipeline** (12 stages, 13 director skills) declared by
the Master Plan, together with the governance it demands — strict $0 gate, cross-artifact ID
resolution, fail-closed QA — and prove the chain with a real test suite.

---

## Master Plan Stage Status

| Stage | Status | Evidence |
|-------|--------|----------|
| **P0.1 Re-verify git state / `--db-path`** | ✅ Complete | `git status --short` clean; no `--db-path` file exists in the repo; the modified files listed in the Kilo screenshot are not present. Nothing was deleted or reset. |
| **P0.2 Diagnose the pytest timeout** | ✅ Complete | Root cause: **pytest was not installed** in this environment (`No module named pytest`) and `tests/factory/` did not exist. Installed `pytest 9.1.1` + `pytest-asyncio` (dev deps from `requirements-dev.txt`, $0). Test groups then run **separately with exit codes** — see the table below. |
| **P0.3 Verify 12 stages + 13 skills** | ✅ Implemented | They did **not** exist. Now created: `pipeline_defs/business-documentary.yaml` (12 stages) + `skills/pipelines/business-documentary/` (13 skills) + 7 new artifact schemas. Contract tests assert stage order, gates, tool names and skill files. |
| **P0.4 Verify TTS / diagram / stock render** | 🟡 Partial | **Diagram: verified with a real artifact** (Pillow render writes a 8.5 KB PNG). **Stock adapters: error taxonomy verified** with fakes. **TTS: BLOCKED — no synthesizer installed** (`piper_tts` status `unavailable`, `cmd:piper` missing; no cloud TTS keys). Narration stage must fail closed. |
| **P0.5 Verify $0 gate + stock adapter errors** | ✅ Implemented | New `lib/zero_cost_gate.py`: unknown cost / unknown route / unapproved paid call / unavailable tool → **BLOCKED**. Failure taxonomy (auth / billing / rate_limit / transport / no_results) kept distinct; `reroute_allowed()` is always `False`. |
| **P1 First E2E pilot (60–90s)** | ⛔ Blocked by environment | Requires a TTS synthesizer (narration) and real footage download (network + licenses). Not attempted — no paid or unlicensed calls made. |

---

## What's Completed

- ✅ `pipeline_defs/business-documentary.yaml` — 12 stages (`topic → research → evidence →
  script → fact_check → storyboard → narration → footage → editorial → compose → qa →
  publish`), `budget_default_usd: 0.0`, gated stages per Master Plan.
- ✅ 13 director skills in `skills/pipelines/business-documentary/` (executive-producer +
  one director per stage).
- ✅ 7 new artifact schemas: `topic_brief`, `evidence_ledger`, `fact_check_report`,
  `narration_manifest`, `alignment_report`, `qa_report`, `publish_package` — registered in
  `schemas/artifacts/__init__.py`.
- ✅ Additive schema extensions the pipeline needs: `script.sections[].evidence_ids`,
  `scene_plan.scenes[]` (`search_queries`, `visual_class`, `diagram_spec`, …),
  `asset_manifest.assets[]` (`author`, `attribution`, `license_url`, `sha256`,
  `search_query`, `selection_reason`, `qa_verdict`, …), `research_brief.sources[]`
  (`source_id`, `publisher`, `source_type`, …), and optional `run_id`/`created_at` on the
  six artifacts the pipeline produces.
- ✅ `lib/zero_cost_gate.py` — strict $0 gate, failure taxonomy, search-stats summary,
  run ledger.
- ✅ `lib/artifact_ids.py` — cross-artifact ID resolution (evidence / source / scene /
  asset / QA gate) with precise dangling-reference reporting.
- ✅ `tests/factory/` — 135 tests, all passing.
- ✅ Environment fix (free, no repo change): installed **ffmpeg 6.1.1** via apt. This
  flipped `video_post` 0/10 → 9/10, `audio_processing` 0/2 → 2/2 and cleared two
  pre-existing environment-caused test failures.

---

## What's NOT Completed

- ❌ End-to-end rendered pilot MP4 (needs TTS + footage downloads — see blockers).
- ❌ `piper_tts` usable: `piper` binary and voice model are not installed.
- ❌ Remotion runtime: `remotion-composer/node_modules` is empty (`npx hyperframes` 0.8.159
  **is** available; ffmpeg is available; Remotion is not).
- ❌ No web-search tool exists in the registry — the research stage depends on
  human-supplied sources or `video_downloader` / `transcript_fetcher` (both `unavailable`
  without `yt_dlp` / `youtube_transcript_api`).
- ❌ `music_library/` does not exist yet; music decisions stay open.

---

## Changed Files (This Session)

New:
- `pipeline_defs/business-documentary.yaml`
- `skills/pipelines/business-documentary/{executive-producer,topic,research,evidence,script,
  factcheck,storyboard,narration,footage,editorial,compose,qa,publish}-director.md` (13)
- `schemas/artifacts/{topic_brief,evidence_ledger,fact_check_report,narration_manifest,
  alignment_report,qa_report,publish_package}.schema.json`
- `lib/zero_cost_gate.py`, `lib/artifact_ids.py`
- `tests/factory/{__init__,test_pipeline_contract,test_artifact_schemas,
  test_artifact_id_resolution,test_zero_cost_gate,test_dry_run_chain,
  test_factory_environment}.py`
- `docs/OPENMONTAGE_RESUME.md`, `docs/OPENMONTAGE_WORK_LOG.md`

Modified (additive only):
- `schemas/artifacts/__init__.py` (7 new artifact names)
- `schemas/artifacts/{script,scene_plan,asset_manifest,research_brief,render_report,
  publish_log}.schema.json` (new optional/provenance fields)
- `AGENTS.md` (Factory session reading order)

---

## Commands Run & Results

```bash
# P0.2 — test infrastructure
pip install "pytest>=8.0" "pytest-asyncio>=0.23"     # pytest 9.1.1

# P0.2 — per-group runs (no tail, exit codes collected; after ffmpeg install)
python -m pytest tests/contracts -q   # 1244 passed, 7 skipped, exit 0
python -m pytest tests/lib -q         #   58 passed,             exit 0
python -m pytest tests/qa -q         #    2 skipped,           exit 0
python -m pytest tests/styles -q     #   15 passed,           exit 0
python -m pytest tests/backlot -q    #   37 passed, 1 skipped, exit 0
python -m pytest tests/tools -q      #  687 passed, 3 xfailed, exit 0
python -m pytest tests/factory -q    #  135 passed,           exit 0
# tests/pipelines and tests/eval collect no tests (exit 5) — pre-existing:
# both directories hold harness code/fixtures only.

# Environment fix (free)
sudo apt-get install -y ffmpeg          # ffmpeg 6.1.1, exit 0

# Registry preflight after ffmpeg
registry.provider_menu_summary()
# composition_runtimes: {'ffmpeg': True, 'remotion': False, 'hyperframes': True}
# tts 0/13, video_generation 0/31, image_generation 0/23, video_post 9/10

# P0.4 — real diagram artifact
DiagramGen().execute({'diagram_type':'boxes', ..., 'output_path': tmp})
# success=True, 8590-byte PNG written, PNG magic bytes verified
```

---

## Stop Point & Next Action

**Stop Point:** Pipeline contract, schemas, governance modules and the factory test suite are
implemented and green. Baseline suite verified.

**Next Action (exact):** P1 first E2E pilot — blocked until narration exists. The smallest
unblocking step is a local TTS path:

```bash
python -c "import piper" 2>&1        # expected: not installed
pip install piper-tts                # if a Python 3.14-compatible wheel exists
# or: report the TTS gap to the human as an administrator setup request
```

Then: one 60–90s topic (candidate: "Why Pallets Matter to Global Shipping"), research →
evidence → script → fact_check with real sources, storyboard, and a footage pass through
`direct_clip_search` with per-query result classes.

---

## Blockers & Risks

1. **No TTS synthesizer** — `piper_tts` needs the `piper` binary + voice model; no cloud TTS
   keys; strict $0 mode blocks unpriced routes. The narration stage must fail closed (never
   fake audio/durations).
2. **No video_generation / image_generation** (0/31, 0/23 configured) — the pipeline is
   designed around real footage, so this is acceptable, but it leaves no fallback B-roll.
3. **`clip_retrieval` (CLIP) and `corpus_population` unavailable** — only `direct_clip_search`
   is usable, so visual alignment relies on frame inspection rather than embedding ranking.
4. **Remotion runtime missing** (`node_modules` empty) — `render_runtime` must be chosen from
   ffmpeg + hyperframes only, with both recorded in the `render_runtime_selection` decision.
5. **Research has no web tool** — sources must come from the human or from installed
   downloaders.
6. **No force-push / destructive commands used.** All work is on a working branch.

---

## Budget / $0 Mode Verification

- **Mode:** strict_zero_cost=true (Master Plan); `orchestration.budget_default_usd: 0.0`.
- **Gate:** `lib/zero_cost_gate.evaluate_call()` — `cost_usd=None` → BLOCKED; `route=None` →
  BLOCKED; non-zero cost → BLOCKED without explicit user approval; tool not `available` →
  BLOCKED (surface as setup request, never reroute).
- **Calls made this session:** ffmpeg install (apt, free), pip install of dev dependencies
  (free), local diagram render (local CPU, free), `apt-get update`. **No paid API call, no
  video generation, no upload, no YouTube publish.**
