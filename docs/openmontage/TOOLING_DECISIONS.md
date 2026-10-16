# Tooling Decisions — Milestone S (2026-10-16)

Scope: audit which tools the last pilot actually used (from CODE/artifacts, not
memory) + minimal skill install. No paid routes, no model downloads, no
process/lock changes. Kilo CLI installed version: **7.8.12**. Project skill
path per official Kilo docs (`kilo.ai/docs/customize/skills`, "Project Skills
(Workspace-Level)"): **`.kilo/skills/<name>/SKILL.md`** (folder name = skill name).

## 1. What the last pilot actually used (evidence)

Run: `projects/pallets-hidden-business/` (run-2026-10-15-pallets).
Sources: `artifacts/{narration_manifest,render_report,asset_manifest}.json`.

| Stage | Tool (exact) | Version / path | $0 check |
|-------|--------------|----------------|----------|
| narration (TTS) | `piper_tts`, engine **piper**, voice/model `en_US-lessac-medium` | piper-tts **1.8.0** (`pip show`); weights `~/.local/share/piper/voices/en_US-lessac-medium.onnx` (+`.json`); 18 segments, 84.975 s measured, 22050 Hz | local synthesis, `estimate_cost()==0.0`, no network |
| subtitles | `subtitle_gen` segment-level fallback from ffprobe-measured boundaries (word timestamps unavailable — recorded as skipped, not passed) | `assets/subtitles/captions.srt`, 16 cues, burned | local |
| compose (render) | `render_runtime: ffmpeg` (decision d-002; hyperframes recorded available-not-selected; remotion unavailable — empty `node_modules`) | **ffmpeg 6.1.1-3ubuntu5** (`ffmpeg -version`); MP4 h264 1920×1080 30fps + aac 22050 Hz mono, 84.975 s | local |
| footage | `direct_clip_search`, 4 search generations; providers: Wikimedia Commons (5), Wikimedia Commons (Open Beelden) (1); licenses CC BY 4.0 / CC BY-SA 4.0 / CC BY-SA 3.0 nl / CC0 1.0 / CC BY 2.0 / CC BY 3.0 | 6 assets (`AST-SCN-*`) | keyless, $0 |
| music | silence (decision d-003; `pixabay_music` gate-blocked, library empty) | `path: null` | $0 |
| diagram | `DiagramGen` Pillow PNG (P0.4 artifact, 8.5 KB) | local | $0 |

## 2. License check (repo's own LICENSE/README files only)

- Repo itself: **GNU AGPL-3.0** (root `LICENSE`).
- Piper voice `en_US-lessac-medium`: pilot manifest asserts
  `"voice_license": "CC-BY-4.0 (lessac dataset voice)"` — but **no license text
  exists in the repo, README, `tools/audio/piper_tts.py`, or the voice sidecar
  `.onnx.json`** (config keys only). → **UNKNOWN** (manifest assertion only;
  verify against a license text before any commercial use).
- `piper-tts` engine 1.8.0 → **UNKNOWN** from repo files (nothing stated).
- `ffmpeg` 6.1.1 (Ubuntu build) → **UNKNOWN** from repo files (nothing stated).
- Voice model weights (`.onnx`) → **UNKNOWN** (no license in sidecar).
- Installed skills below: **MIT** both repos (LICENSE file headers read).

## 3. Explicitly NOT installed

81-skill OpenMontage pack, `everything-kilo-code`, any ElevenLabs/HeyGen skill,
any YouTube-video downloader. Only the 7 skills in §4 were copied. Upstream
`hooks/`, `index.js`, root scripts of superpowers were NOT installed.

## 4. Installed skills (project level, `.kilo/skills/`)

| Skill (folder = name) | Source URL | Pinned commit | License | Pre-install audit (every SKILL.md + script read) |
|---|---|---|---|---|
| test-driven-development | https://github.com/obra/superpowers | `bb92a77` (v7.0.0, 2026-10-09; matches `ls-remote` HEAD) | MIT | SKILL.md + writing-good-tests.md: guidance only. No network, writes, env, secrets. |
| systematic-debugging | same | same | MIT | SKILL.md + 6 companion .md + .ts example: guidance only. `find-polluter.sh` runs local `npm test` per file (no network/secrets/env; `bash -n` clean). Prose mentions of "token/secrets" are fictional dialogue/diagnostic examples, not code. |
| verification-before-completion | same | same | MIT | SKILL.md only: guidance only. No code at all. |
| yt-script | https://github.com/Jakeschincariol/youtube-agent-skill | `a2feb21` (2026-09-16; matches `ls-remote` HEAD) | MIT | SKILL.md + `hookscore.py` (pure local heuristic scorer, reads `hooks.json`, prints stdout) + `hooks.json` (data). No network/writes/env/secrets. Verified: `py_compile` exit 0; `--hook` run scored locally (output observed). |
| yt-package | same | same | MIT | SKILL.md + `title.py` (local string lint, stdout only). No network/writes/env/secrets. `py_compile` exit 0 (observed). |
| yt-chapters | same | same | MIT | SKILL.md + `chapters.py` (local transcript parser). **Dependency found:** imports `load, parse_ts` from sibling `../yt-edit` (not installed). Fix: vendored `yt-edit/deadair.py` **verbatim** as `yt-chapters/deadair.py` + 4-line try/except import fallback (exact diff in §5). `deadair.py` audited: reads transcript file, prints EDL; no network/writes/env/secrets. Verified end-to-end on a /tmp SRT: 3 valid chapters, exit 0 (observed). |
| yt-seo | same | same | MIT | SKILL.md only, no tools. Guidance only. |

## 5. Local modifications to vendored files (exact)

1. `.kilo/skills/yt-chapters/chapters.py` — import fallback for standalone install:
```diff
-sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "yt-edit"))
-from deadair import load, parse_ts  # noqa: E402  (same parser, one implementation)
+try:
+    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "yt-edit"))
+    from deadair import load, parse_ts  # noqa: E402  (same parser, one implementation)
+except ImportError:  # OpenMontage local adaptation: standalone install, use vendored copy
+    from deadair import load, parse_ts  # noqa: E402  (vendored from yt-edit/deadair.py, verbatim)
```
2. `.kilo/skills/yt-chapters/deadair.py` — NEW, byte-identical copy of upstream
   `skills/yt-edit/deadair.py` at `a2feb21` (yt-edit skill itself NOT installed).
3. `.kilo/skills/yt-script/ADAPTATION.openmontage.md` — NEW, binding local rules:
   every factual sentence needs a resolving ledger `claim_id`; hook scores are
   heuristics, never forecasts; narration voice comes from `narration_manifest`,
   not `~/.claude/youtube/voice.md`.

## 6. Unknowns

- Voice/engine/ffmpeg/weights licenses (see §2) — must resolve before commercial use.
- Whether Kilo auto-discovers `.kilo/skills/` in THIS repo layout was not
  end-to-end verified (no Kilo session run in this milestone; path taken from
  Kilo's official skills doc, not assumed).
- `yt-script` voice-profile path (`~/.claude/youtube/voice.md`) does not exist
  here — covered by the adaptation (§5.3), not a blocker.

## 7. Rollback

Delete `.kilo/skills/<name>/` (single `rm -rf`; skills are leaf copies, nothing
else references them). Upstream repos untouched (cloned to /tmp, since removed).
`git revert <commit>` restores pre-install state exactly.
