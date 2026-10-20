# EPIC 3 — Ticket Generation

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ EPIC 2 — Statistical Analysis Engine](EPIC-2-statistics.md) · [EPIC 4 — Filtering Engine (the core value) ➡️](EPIC-4-filtering.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [F3.1 — Full generator](#f3-1-full-generator)
- [F3.2 — Positional generator](#f3-2-positional-generator)
- [F3.3 — Random & Smart](#f3-3-random-smart)
- [F3.4 — Wheel generator](#f3-4-wheel-generator)
- [F3.5 — Quick-pick & favorites](#f3-5-quick-pick-favorites)
- [F3.6 — Generation UI (number grid, modes, bonus)](#f3-6-generation-ui-number-grid-modes-bonus)
  - [Epic 3 exit criteria](#epic-3-exit-criteria)

</details>
<!-- TOC_BLOCK_END -->

**Goal:** produce a candidate pool of combinations by any of the four modes plus
quick-pick and favorites. **Verified source:** Doc 05 §A, Doc 01 §C. **Depends on:**
EPIC 1 (Game/Ctx), EPIC 5 (WheelLibrary, for F3.4), EPIC 2 (Hot-Cold, for F3.5).
**Phase:** 3.

**Features:** F3.1 Full · F3.2 Positional · F3.3 Random & Smart · F3.4 Wheel ·
F3.5 Quick-pick & favorites · F3.6 Generation UI.

> **Determinism rule:** randomness is injected (`rng: () => number`), never called
> inside pure code, so Random/Smart are testable. Free-edition cap: pool ≤ 10 (EPIC 8).

---

## F3.1 — Full generator
**User stories** — *As a player,* I select a pool of numbers and generate **all**
`C(n,k)` combinations.
**Acceptance:** AC-G1. **Module:** `core/generation/full`.

**Chain**
- **S1:** `full(pool: number[], k: number): Combination[]`.
- **S2:** property test — `full(pool,6).length === C(pool.length,6)`; `pool` of 12 → 924; all lines unique, sorted, subset of pool.
- **S3:** standard k-combination enumeration.
- **S4:** GenerationEngine dispatch (`generate('full', pool)`).
- **S5:** generate 924 from 12 numbers; assert count + uniqueness.
- **Gate:** `{{ACCEPTANCE}}`=AC-G1; property `= C(n,k)` holds for several (n,k).

---

## F3.2 — Positional generator
**User stories** — *As a player,* I set a candidate number set per position and get
the cross-product respecting each slot.
**Acceptance:** AC-G2. **Module:** `core/generation/positional`.

**Chain**
- **S1:** `positional(slots: number[][], opts?): Combination[]` (slot i = allowed numbers for position i).
- **S2:** small slots → exact cross-product; each line respects slot membership; dedupe equal sets if required by config.
- **S3:** cartesian product with validity filter (no repeated number within a line).
- **S4:** `generate('positional', slots)`; screen S01 per-position Pick.
- **S5:** verify cross-product size + slot adherence.
- **Gate:** `{{ACCEPTANCE}}`=AC-G2.

---

## F3.3 — Random & Smart
**User stories** — *As a player,* I generate N random lines; or N "smart" lines
weighted by a chosen analysis depth (previous-N window).
**Acceptance:** AC-G5. **Module:** `core/generation/random`.

**Chain**
- **S1:** `random(pool,k,count,rng)`, `smart(pool,k,count,depth,history,rng)`.
- **S2:** with a seeded `rng`, output is deterministic; count + validity correct; smart biases toward frequent numbers in the window (assert distribution over many draws with a fixed seed).
- **S3:** random sampling without replacement per line; smart weights by Hot-Cold over the window (reuse F2.10).
- **S4:** `generate('random'|'smart', …)`; screen S01 mode + depth dropdown.
- **S5:** generate with a seed; show reproducible output.
- **Gate:** `{{ACCEPTANCE}}`=AC-G5; determinism under fixed seed.

---

## F3.4 — Wheel generator
**User stories** — *As a player,* I select a pool and a wheel formula and generate
the wheel's lines with its guarantee.
**Acceptance:** AC-G3. **Module:** `core/generation/wheel` (delegates to EPIC 5 WheelLibrary).

**Chain**
- **S1:** `wheel(pool, formula): { lines: Combination[]; guarantee: GuaranteeReport }`.
- **S2:** 8-number pool, "pick-6 if-4" → 7 lines (see EPIC 5 F5.2); instantiation matches the letter map.
- **S3:** call `WheelLibrary.instantiate(wheel, pool)`.
- **S4:** `generate('wheel', pool, {formula})`; screen S01 Wheels radio + formula picker.
- **S5:** generate the 7-line wheel; assert coverage guarantee holds by brute force.
- **Gate:** `{{ACCEPTANCE}}`=AC-G3.

---

## F3.5 — Quick-pick & favorites
**User stories** — *As a player,* one click picks Hot / Cold / Last-N numbers; I
save and reload favorite number sets.
**Acceptance:** AC-G4. **Module:** `core/generation/quickpick` + `SettingsStore` (favorites).

**Chain**
- **S1:** `quickPick(kind: 'hot'|'cold'|'lastN', history, params): number[]`; `saveFavorite(name, set)`, `loadFavorite(name)`.
- **S2:** hot/cold picks equal the Hot-Cold analysis (F2.10) over the same range; favorites round-trip.
- **S3:** thin wrapper over F2.10; favorites via SettingsStore.
- **S4:** screen S43 quick-pick dropdown; Save/Load Selected.
- **S5:** pick hot numbers; confirm they match the Hot-Cold tab.
- **Gate:** `{{ACCEPTANCE}}`=AC-G4.

---

## F3.6 — Generation UI (number grid, modes, bonus)
**User stories** — *As a player,* I select numbers on a grid (selected = highlighted),
choose a mode (Full/Wheels/Positional/Random), toggle bonus, and click Generate to
fill the ticket store.
**Acceptance:** AC-G1..G6. **Module:** `apps/desktop` route S01 + `ui/NumberGrid`.

**Chain**
- **S1:** `<GenerationPanel game />` with NumberGrid, mode radios, bonus toggles, Generate button → `generateTickets` use-case → TicketSet.
- **S2 (E2E):** select 12, Full → store has 924; switch to Wheels → fewer lines.
- **S3:** implement panel + NumberGrid (F8.4); enforce free-edition ≤10 (EPIC 8).
- **S4:** wire to `app/usecases/generateTickets`; result lands in the ticket store (EPIC 7).
- **S5:** drive Flow-3 (Doc 06) in the app.
- **Gate:** all AC-G*; the ≥10 cap shows the entitlement message.

### Epic 3 exit criteria
All four modes + quick-pick verified; generation fills the ticket store; free-edition
cap enforced.

---
> **Next Steps**: [⬅️ EPIC 2 — Statistical Analysis Engine](EPIC-2-statistics.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [EPIC 4 — Filtering Engine (the core value) ➡️](EPIC-4-filtering.md)
