---
title: 'Story 4.4: Intelligence Narrative Obsidian Export'
type: 'feature'
created: '2026-11-12'
status: 'done'
baseline_revision: '71708e59853876ad833a632eb8241bb68f3c7d70'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred:
  - summary: >-
      The exported deep-link has no runtime consumer: nothing in the app handles an incoming lottery:// URL, calls parseEvidenceLink, or starts Forensic Replay.
    evidence: |-
      The app has no engine-to-app replay transport (Story 4.2 added only the store's loadReplay/startReplay, which nothing feeds), so a link cannot resolve to a payload without a new API/gateway path. Obsidian opening a custom scheme also depends on the OS routing it to the installed app. Intent says the link must be "functional"; this delivers the format, parser, matcher and scheme registration only.
    location: >-
      app/utils/evidence-link.ts:1
    severity: medium
  - summary: >-
      No user-facing "Export to Obsidian" trigger exists: export_to_obsidian is a Python function with no CLI command, API endpoint or UI control.
    evidence: |-
      The spec's Never section excluded CLI/API/gateway edits, and no vault output path is configured, so out_dir is caller-supplied. Callers must also supply the v11 narrative text (NarrativeGenerator.generate_story_v11).
    location: >-
      engine/modules/obsidian_export.py:25
    severity: medium
---

<intent-contract>

## Intent

**Problem:** A finalized v11.0 session leaves no durable research record: the narrative lives only in memory and cannot point back at the ledgered Justified Number it explains, so long-term resonance trends cannot be tracked in Obsidian.

**Approach:** Add `engine/modules/obsidian_export.py` with `export_to_obsidian(ledger, seq, narrative, out_dir)` that verifies the ledger chain (via `build_replay`), then writes a fresh `.md` file with 3.2-style frontmatter, the narrative, and a `lottery://evidence/<seq>?...` deep-link carrying the entry's geodesic coordinates. Mirror link parsing in `app/utils/evidence-link.ts` so the link resolves to a replay target, and register the `lottery` scheme in `app/app.json`.

## Boundaries & Constraints

**Always:** Export reads the ledger only; it refuses (raises `ObsidianExportError`) when the chain fails verification, the seq is unknown, or the narrative is blank. One fresh file per export, named `evidence-<seq>-<hash12>.md`, overwritten if re-exported. Link format: `lottery://evidence/<seq>?hash=<entry_hash>&coords=<c1,c2,...>` with coords as `repr`-exact floats (round-trip equal to the ledger's `state_vector`). Frontmatter keeps the 3.2 keys (`source-strategy`, `confidence-rating`, tags incl. `#lottery/analysis`) plus `ledger-seq`, `entry-hash`, `evidence-link`. TS parser returns null for any malformed link. `matchesReplay(link, replay)` is true only when seq, hash and every coord equal the replay payload.

**Never:** No edits to `ledger.py`, `replay.py`, `narrative.py`, the Go gateway, the API or its response schema, or the CLI; no new dependencies; no writes to `docs/analysis-index.md`; no writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | valid seq, non-blank narrative | file written; contains narrative, ticket, hash, deep-link; returns Path | — |
| Link round trip | exported link parsed by TS `parseEvidenceLink` | `{seq, hash, coords}` equal to ledger entry | — |
| Unknown seq | seq not in ledger | nothing written | `ObsidianExportError` |
| Tampered chain | any entry altered | nothing written | `ObsidianExportError` |
| Blank narrative | `""` / whitespace | nothing written | `ObsidianExportError` |
| Malformed link | wrong scheme, seq < 1, non-finite coord, missing hash | — | TS returns null |
| Re-export | same seq twice | same filename, overwritten | — |

</intent-contract>

## Code Map

- `engine/modules/ledger.py` -- `ForensicLedger`, `LedgerEntry`; read-only.
- `engine/modules/replay.py` -- `build_replay(ledger, seq)` verifies chain and returns payload; reuse it, wrap `ReplayError`.
- `engine/modules/narrative.py` -- `NarrativeGenerator.generate_story_v11` produces the narrative text passed in; read-only.
- `engine/cli/commands/daily.py:474` -- `_write_md`: frontmatter style to follow (3.2 contract).
- `app/utils/ghost.ts` -- `ReplayPayload`, `parseReplayPayload`; style and types to reuse.
- `app/utils/__tests__/*.test.ts` -- `bun:test` style. `tests/test_forensic_replay.py` -- pytest style (`.venv/bin/python -m pytest`).
- `app/app.json` -- Expo config; add `"scheme": "lottery"`.

## Tasks & Acceptance

**Execution:**
- `engine/modules/obsidian_export.py` -- `ObsidianExportError`, `build_evidence_link`, `export_to_obsidian` -- pure file export over a verified payload
- `tests/test_obsidian_export.py` -- every matrix row; link coords round-trip exactly
- `app/utils/evidence-link.ts` -- `parseEvidenceLink(url)` and `matchesReplay(link, replay)`
- `app/utils/__tests__/evidence-link.test.ts` -- matrix rows plus a literal link produced by the Python exporter
- `app/app.json` -- register the `lottery` scheme

**Acceptance Criteria:**
- Given a finalized session with a ledgered Justified Number, when the user triggers export, then a `.md` file with the narrative is produced.
- Given the exported file, when its deep-link is opened, then it resolves to that entry's seq, hash and geodesic coordinates, usable to start Forensic Replay.

## Spec Change Log

## Review Triage Log

### 2026-11-12 — Review pass
- verdicts: 29 findings — high 0, medium 3, low 12, false 14, maybe-false 0
- findings:
  - `[medium]` `[defer]` Deep-link has no runtime consumer / scheme registered but unused / link may not open the panel (blind, edge, gap, alignment) — needs an engine-to-app replay transport absent since 4.2; recorded in deferred.
  - `[medium]` `[defer]` No user-facing "Export to Obsidian" trigger, caller-supplied narrative and out_dir (alignment, 2 rows) — CLI/API wiring excluded by Never; recorded in deferred.
  - `[medium]` `[patch]` Python/TS link contract pinned only by hand-copied TS literal (gap) — added a Python test asserting the exact link string equal to the TS literal.
  - `[false]` `[reject]` Non-finite coords can be exported (blind) — ledger.capture rejects non-finite state vectors.
  - `[false]` `[reject]` Empty ticket yields `ticket: [none]` (blind, edge, 2 rows) — ledger.capture rejects empty tickets.
  - `[false]` `[reject]` captured_at/link unescaped in frontmatter (blind) — values are ISO timestamp and a URL of hex and numbers only.
  - `[false]` `[reject]` Narrative `---`/heading corrupts note (blind, edge, 2 rows) — narrative is in the body after frontmatter closes; a `---` there is a horizontal rule.
  - `[false]` `[reject]` qpu_fidelity unquoted can be nan/inf (blind) — ledger validates it finite in [0,1].
  - `[false]` `[reject]` -0 vs 0 compare equal in matchesReplay (blind) — harmless for coordinate identity.
  - `[false]` `[reject]` Duplicate query params untested (blind) — behavior exists and is trivial.
  - `[false]` `[reject]` No test of "Obsidian opens custom scheme" (blind) — covered by the deferred consumer item.
  - `[false]` `[reject]` Python test never exercises TS parser (gap, other) — same root cause as the patched row.
  - `[false]` `[reject]` Concurrency guard missing on export (blind) — read-only over ledger, one file per entry.
  - `[false]` `[reject]` seq bool/float non-int outside error type (edge) — build_replay raises ReplayError, wrapped.
  - `[low]` `[reject]` source-strategy hardcoded "synapse" (blind) — matches 3.2 convention; payload has no strategy.
  - `[low]` `[reject]` OSError not wrapped in ObsidianExportError (edge, blind) — fix adds guards; unlikely.
  - `[low]` `[reject]` Non-atomic write, silent overwrite (blind) — overwrite is the 3.2 fresh-file contract.
  - `[low]` `[reject]` out_dir None raises TypeError (edge) — unlikely misuse.
  - `[low]` `[reject]` Hash not required 64 hex, seq leading zeros, extra params accepted (blind, edge, 3 rows) — matchesReplay gives strict check; adds guards.
  - `[low]` `[reject]` NUM regex looser than producer (blind) — still finite numbers only.
  - `[low]` `[reject]` Untested encoded input / non-int ticket (blind, 2 rows) — unlikely.
  - `[low]` `[reject]` Narrative re-using `## Evidence` heading (edge) — cosmetic.
  - `[low]` `[reject]` Intent readings A–E, no v11 session concept (alignment, 2 rows) — spec's single stated reading; see deferred items.

## Design Notes

"Geodesic Evidence Panel coordinates" is read as the ledger seq plus the entry's `state_vector`, the same data Forensic Replay (4.2) renders. The file is the export surface; no UI or API trigger exists, so the user trigger is calling `export_to_obsidian`.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_obsidian_export.py -q` -- expected: all pass
- `cd app && bun test utils/__tests__/evidence-link.test.ts` -- expected: all pass

## Auto Run Result

Status: done

**Summary:** Story 4.4 adds `export_to_obsidian`, which verifies the ledger chain and writes a fresh Obsidian note (3.2-style frontmatter, narrative, Justified Number, `lottery://evidence/<seq>?hash=&coords=` deep-link), plus a TS link parser/matcher and the `lottery` scheme in `app.json`.

**Files changed:**
- `engine/modules/obsidian_export.py` -- export function, link builder, error type.
- `tests/test_obsidian_export.py` -- matrix rows plus exact link-format pin (7 tests).
- `app/utils/evidence-link.ts` -- `parseEvidenceLink`, `matchesReplay`.
- `app/utils/__tests__/evidence-link.test.ts` -- matrix rows and Python-produced literal (16 tests).
- `app/app.json` -- `scheme: lottery`.

**Review:** 29 findings. Patched 1 (medium: link format pinned across Python/TS). Deferred 2 items (medium): no runtime consumer of the deep-link in the app, and no user-facing export trigger. Rejected the rest, each with its reason in the triage log.

**Follow-up review recommended:** false (1 medium patched, no high).

**Verification:** `pytest tests/test_obsidian_export.py` passed (7). `bun test utils/__tests__/evidence-link.test.ts` passed (16).

**Residual risks:** The AC's "functional" deep-link and "user triggers" export are only partly met: the link is well-formed and parseable but nothing in the app opens it, and export is callable only as a function (see deferred). The test run deletes `data/.last_fetch_megasena`; it was restored and is not part of this change. No operator actions are owed.
