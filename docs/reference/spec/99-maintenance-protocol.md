# 99 — Weekly Maintenance Protocol

Keeps the rebuilt system current, correct, and buildable. Run the **weekly cycle**
every week; run the **triggered** procedures when their event fires. Each step has an
owner action and, where useful, an **exact prompt** to hand an AI agent.

---

## Weekly cycle (fixed cadence)

### Monday — Data freshness
- **Pull latest draws** for all active games via `UpdateClient`; append (dedupe).
  > Prompt: *"Run the updateDrawings use-case for every active game. Report per game: draws added, any fetch failures, and any game whose newest draw is older than its expected cadence (flag as stale)."*
- **Re-seed the game catalog** if any game's rules changed (pick/max/bonus) — update `fixtures/games-catalog.csv` and the catalog store.
- **Verify parity did not drift:** re-run the statistics golden tests against the newest data slice.
  > Prompt: *"Run the statistics parity suite (fixtures/stats-golden). If any metric drops below its threshold (Units 100%, others ≥98.7%), open a bug with the failing rows and the computed-vs-expected diff. Do not weaken the test."*

### Tuesday — Dependency & security
- `pnpm outdated` + `pnpm audit`; bump patch/minor behind CI; hold majors for a scheduled upgrade.
  > Prompt: *"Update all patch/minor dependencies, run typecheck/lint/test, and open a PR only if green. List held major upgrades with their changelog risk."*
- Rotate any adapter secrets/URLs (update sources) if used.

### Wednesday — Quality sweep
- Run the full gate across all modules: `pnpm typecheck && pnpm lint && pnpm test && pnpm test:e2e`.
- **Coverage watch:** fail the week if any core module drops below 90%.
- **Purity check:** grep `packages/core` for forbidden imports (`data|ui|node:|@tauri`).
  > Prompt: *"Run the quality gate template (spec/02-conventions.md) across the repo. Report the checklist with command output; open issues for any red item."*

### Thursday — Correctness & flows
- Re-run the E2E flows (Doc 06 Flow-0…Flow-10) headless; screenshot-diff key screens.
- **Wheel integrity:** re-run the abbreviated-wheel cover check for the shipped tables (no uncovered X-subset).
- **Predictor sanity:** re-run verification for each formula over the newest range; record hit-rates in a trend log (detect regressions, not to imply the lottery is predictable).

### Friday — Docs & drift
- **Spec/code drift:** for each feature merged this week, confirm its epic entry + acceptance criteria still match the code; update the epic file if behavior changed.
- **Glossary drift:** if any new domain term appeared in code, add it to `CONTEXT.md` (per `/domain-modeling`); challenge any term that conflicts.
- **ADR check:** if a hard-to-reverse, surprising, trade-off decision was made, write an ADR in `docs/adr/`.
- Update `Documentation/` if a *behavior* (not just code) changed; keep doc 10 (validation) authoritative.

---

## Triggered procedures

| Trigger | Procedure |
|---|---|
| **A game's rules change** (operator changes pick/max/bonus) | Update catalog + `games-catalog.csv`; re-run that game's parity slice; migrate saved settings/filters if ranges shifted. |
| **A statistics parity test fails** | Treat as P1. Reproduce with the exact draw; diff computed vs golden; the *golden is truth* — fix the code, never the fixture. Cross-check the corrected rule against Doc 10. |
| **New game to add** | Run F1.3 create-game; import history (F1.5); add to catalog fixture; smoke-test analysis + generation. |
| **A new filter/metric requested** | New feature: run its 5-stage chain; register the tag; add golden fixtures; extend `filters-catalog.csv`. |
| **New wheel spec `(k,n,guarantee)`** | Generate the covering design (F5.2); run the cover check; store the JSON table; **never import proprietary `.Wheels`**. |
| **Adapter/source breaks** (update fetch 404s) | Swap the `UpdateClient` adapter; core/app untouched (the seam pays off). Add a contract test for the new source. |
| **Dependency major upgrade** | Branch; upgrade; run full gate + all E2E flows; hold if any flow regresses. |
| **Release** | Tag; run global exit criteria (`90-build-order.md`); build desktop artifacts; smoke Flow-0 on each OS. |

---

## Health dashboard (track weekly)
Keep a one-row-per-week log:

| Week | Draws added | Stale games | Parity (min %) | Coverage (min %) | E2E flows pass | Open P1 | Deps held |
|---|---|---|---|---|---|---|---|

- **Parity < threshold** or **any E2E flow red** ⇒ the week is not green; fix before shipping.
- **Purity broken** (core imports I/O) ⇒ stop-the-line; the architecture guarantee is the product's foundation.

## Standing invariants (never violate)
1. The golden fixtures are ground truth — fix code, not tests.
2. `packages/core` stays pure (no I/O/UI/clock/rng).
3. Abbreviated wheels must pass the brute-force cover check before shipping.
4. Prediction is presented as pool-hit-rate analysis, never as a guarantee — the
   lottery is negative-expectation; the tools organize play, not the odds.
5. No proprietary assets copied (`.Wheels`, `.mdb`); regenerate/own everything.
