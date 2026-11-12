---
title: 'Story 4.3: Swarm-based Kelly Optimizer'
type: 'feature'
created: '2026-11-12'
status: 'done'
baseline_revision: 'b21bd8d97b7b0c25255c0571fa1cde52042a7106'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred:
  - summary: >-
      The Python sizer in engine/swarm/kelly.py is not consumed by any engine or API path; the dashboard uses the TS mirror.
    evidence: |-
      Exposing it to the app needs an API/gateway response change, excluded by the intent's Never section. TS and Python parity is pinned only by duplicated literals in two suites.
    location: >-
      engine/swarm/kelly.py:1
    severity: medium
  - summary: >-
      Confidence Leverage panel branches (UNAVAILABLE, active, BELOW BASELINE) have no render test.
    evidence: |-
      No component test harness exists in the repo; the sizing logic is unit tested.
    location: >-
      app/App.tsx:358
    severity: low
---

<intent-contract>

## Intent

**Problem:** The swarm produces a consensus confidence (FR14) but nothing turns it into a bet size, so the user cannot leverage that confidence without guessing how much of the vault to expose.

**Approach:** Add `engine/swarm/kelly.py` with a pure fractional-Kelly sizer driven by swarm confidence and vault balance. Mirror it in `app/utils/kelly.ts`, keep `vaultBalance` in the store, and show a "Confidence Leverage" panel in the dashboard result section.

## Boundaries & Constraints

**Always:** Sizing applies only when confidence is strictly above the baseline threshold (`BASELINE_CONFIDENCE`, 0.5 default); otherwise fraction and stake are 0. Binary Kelly `f* = (b*p - (1-p)) / b` with `p` = confidence, `b` = net payout odds (default 1.0). Result fraction = `f* * KELLY_FRACTION` (default 0.25), clamped to `MAX_FRACTION` 0.10 (same ceiling as `kelly_bankroll.py`). Stake = fraction * vault balance. Invalid input (non-finite, confidence outside [0,1], `b <= 0`, balance < 0) is rejected: Python raises `ValueError`, TS returns null. Python and TS agree on the same inputs.

**Never:** No edits to `kelly_bankroll.py`, the ledger, the Go gateway, the API or its response schema, new dependencies, wiring into ticket generation or any real-money action, and no writes to `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Above baseline | p=0.6, b=1, balance=1000 | f*=0.2, fraction=0.05, stake=50 | — |
| At/below baseline | p=0.5 or 0.4 | fraction 0, stake 0, `active` false | — |
| Cap | p=0.99, b=1 | fraction 0.10 (f*=0.98 -> 0.245 clamped) | — |
| Zero balance | p=0.9, balance=0 | fraction > 0, stake 0 | — |
| Bad input | NaN / p=1.2 / b<=0 / balance<0 | no result | `ValueError` (Py), null (TS) |

</intent-contract>

## Code Map

- `engine/modules/kelly_bankroll.py` -- existing lottery-odds Kelly; read-only. Source of the 0.10 safety ceiling to reuse as a constant.
- `engine/swarm/` -- swarm package (`cluster.py`, `hibernation.py`); add `kelly.py` here.
- `app/utils/ghost.ts`, `app/utils/equalizer.ts` -- pure-helper style to follow.
- `app/utils/__tests__/*.test.ts` -- `bun:test` tests.
- `app/stores/useResonanceStore.ts` -- Zustand store; add `vaultBalance` + setter.
- `app/App.tsx` -- result section (~line 342) already renders `result.confidence`; add the panel there. Styles use `metaBox`/`metaText`.
- `tests/test_forensic_replay.py` -- pytest style; run with `.venv/bin/python -m pytest`.

## Tasks & Acceptance

**Execution:**
- `engine/swarm/kelly.py` -- constants, frozen `KellyLeverage` dataclass, `confidence_leverage(confidence, vault_balance, odds=1.0, baseline=..., kelly_fraction=..., max_fraction=...)` -- pure sizing
- `tests/test_swarm_kelly.py` -- every matrix row
- `app/utils/kelly.ts` -- same constants and `confidenceLeverage(...)` returning object or null
- `app/utils/__tests__/kelly.test.ts` -- every matrix row plus Python parity values
- `app/stores/useResonanceStore.ts` -- `vaultBalance` (default 1000) and `setVaultBalance` (ignores non-finite or negative)
- `app/App.tsx` -- "CONFIDENCE LEVERAGE" panel: vault balance input, leverage % and stake, or "BELOW BASELINE" when inactive

**Acceptance Criteria:**
- Given a swarm consensus with confidence above the baseline, when the dashboard shows the result, then it displays a Confidence Leverage signal with the fractional bet size as a share of, and amount from, the user's vault balance.
- Given confidence at or below the baseline, when the dashboard shows the result, then the leverage is shown as inactive with zero stake.

## Spec Change Log

## Review Triage Log

### 2026-11-12 — Review pass
- verdicts: 29 findings — high 0, medium 2, low 18, false 9, maybe-false 0
- findings:
  - `[medium]` `[patch]` Balance field and stake can disagree: invalid text left the stale stored balance driving the panel (blind, edge, gap) — App.tsx now sizes only from the parsed field text and shows UNAVAILABLE when it is invalid.
  - `[medium]` `[patch]` setVaultBalance guard untested (gap, blind) — added app/utils/__tests__/vault-balance-store.test.ts (3 tests).
  - `[medium]` `[defer]` Python sizer unwired, vault balance manual, baseline fixed (intent alignment) — wiring needs excluded API change; recorded in deferred.
  - `[low]` `[defer]` Panel render branches untested (gap) — no render harness; recorded in deferred.
  - `[low]` `[defer]` TS/Python parity only via duplicated literals (blind, gap) — recorded with the Python-unwired item.
  - `[low]` `[reject]` Same stale-text / balanceText not re-synced from store (blind, edge, gap, 4 rows) — store changes only through this field; covered by the patch.
  - `[low]` `[reject]` leverage declared between hooks / no useMemo (blind, gap) — now after result state, cheap pure call.
  - `[low]` `[reject]` No risk disclaimer; odds fixed at 1.0 (blind) — Design Notes fix this reading.
  - `[low]` `[reject]` Custom baseline/fraction options and boundary cases untested (blind, gap) — defaults pinned, options are plain arithmetic.
  - `[low]` `[reject]` baseline not range-checked; maxFraction > 1 allowed (blind, edge) — caller-supplied tuning, adds guards, unlikely.
  - `[low]` `[reject]` Default balance 1000 is a placeholder, not persisted (blind, alignment) — fixed by the spec's Design Notes.
  - `[low]` `[reject]` Python OverflowError for huge ints (edge) — unreachable from callers.
  - `[low]` `[reject]` Near-zero fraction shows active with 0.00% (edge) — cosmetic.
  - `[low]` `[reject]` Number() accepts 1e3/0x10, comma decimals (edge, gap) — harmless, still non-negative finite.
  - `[low]` `[reject]` Intent readings R1-R4 / baseline constant / swarm input is result.confidence (alignment, 3 rows) — spec's single stated reading; no observably different alternative in repo.
  - `[false]` `[reject]` TextInput import missing (blind) — TextInput is already imported and used in App.tsx.
  - `[false]` `[reject]` Confidence may be 0-100 scale (blind, edge, 2 rows) — App already renders confidence*100, so it is 0-1.
  - `[false]` `[reject]` BELOW BASELINE mislabels non-baseline zero fractions (edge) — with odds 1.0 any confidence above 0.5 yields a positive fraction.
  - `[false]` `[reject]` Inconsistent display when balance invalid and confidence at baseline (edge) — resolved by the patch.
  - `[false]` `[reject]` Python module unconnected is a defect (alignment) — see deferred item; not a new fault.
  - `[false]` `[reject]` Hooks order violation (blind) — useState order is stable; no conditional hooks.
  - `[false]` `[reject]` Tests missing for bool rejection (blind) — covered in the extra bad-input cases.
  - `[false]` `[reject]` Intent expects dashboard test only at UI surface (alignment) — descriptive; same as the render-test deferral.
  - `[false]` `[reject]` Nothing tests store-to-render path (alignment) — same as render-test deferral.

## Design Notes

"Consensus confidence" is the `result.confidence` already shown in the dashboard; `vaultBalance` is a local store value the user edits (no vault balance source exists yet). Confidence is treated as the win probability of one even-money-style bet; this is a leverage signal, not a lottery-odds model (that stays in `kelly_bankroll.py`). Golden: p=0.6,b=1 -> f*=0.2 -> *0.25 = 0.05 -> 50 on 1000.

## Verification

**Commands:**
- `.venv/bin/python -m pytest tests/test_swarm_kelly.py -q` -- expected: all pass
- `cd app && bun test utils/__tests__/kelly.test.ts` -- expected: all pass

## Auto Run Result

Status: done

**Summary:** Story 4.3 adds a pure fractional-Kelly sizer driven by swarm confidence and vault balance (Python and TS mirror), a `vaultBalance` store value, and a "Confidence Leverage" panel in the dashboard result view.

**Files changed:**
- `engine/swarm/kelly.py` -- `confidence_leverage`, constants, `KellyLeverage`.
- `tests/test_swarm_kelly.py` -- matrix rows plus extra cases.
- `app/utils/kelly.ts` -- TS mirror, returns null on invalid input.
- `app/utils/__tests__/kelly.test.ts` -- matrix rows and parity values.
- `app/utils/__tests__/vault-balance-store.test.ts` -- store balance tests (review patch).
- `app/stores/useResonanceStore.ts` -- `vaultBalance`, `setVaultBalance`.
- `app/App.tsx` -- Confidence Leverage panel with balance input.
- `_bmad-output/implementation-artifacts/epic-4-context.md` -- compiled epic context.

**Review:** 29 findings. Patched 2 (medium: stale balance display, store tests). Deferred 3 findings in 2 items (medium: Python sizer not wired to the app, including parity via duplicated literals; low: panel render untested). Rejected the rest, each with its reason in the triage log.

**Follow-up review recommended:** false (2 medium patched, no high).

**Verification:** `pytest tests/test_swarm_kelly.py` passed (16). `bun test` on kelly, vault-balance-store and replay-store tests passed (12).

**Residual risks:** The panel was not rendered in a live app. A pre-existing test run deletes `data/.last_fetch_megasena`; it was restored and is not part of this change. No operator actions are owed.
