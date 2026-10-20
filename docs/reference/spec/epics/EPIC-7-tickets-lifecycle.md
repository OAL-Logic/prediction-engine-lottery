# EPIC 7 — Tickets Lifecycle · Optimize · Search · Check-Win

**Goal:** the ticket store and everything downstream of it — edit/sort/dedupe/tag,
optimization, combo search, win-checking, and export/print. **Verified source:**
Doc 01 §F, Doc 05 §C/D/E. **Depends on:** EPIC 1–4 (a filtered set). **Phase:** 7.

**Features:** F7.1 TicketSet ops · F7.2 Optimizer · F7.3 Searcher · F7.4 WinChecker ·
F7.5 Export & print · F7.6 Tickets UI.

---

## F7.1 — TicketSet operations
**User stories** — *As a player,* I sort each line low→high, remove duplicates, tag
lines (`X`/blank) and bulk-delete by tag, see a numbers-hit histogram, and 2-/3-combo
frequency across my tickets.
**Acceptance:** AC-T1, AC-T2. **Module:** `core/tickets/set`.

**Chain**
- **S1:** `TicketSet { lines; sortEachLine(); dedupe(); tag(i,t); deleteByTag(t); histogram(): Map<number,number>; comboFreq(size:2|3): Map<combo,count> }`.
- **S2:** sort orders ascending; dedupe leaves a set; histogram sums to `k×#tickets`; comboFreq counts pair/triple occurrences.
- **S3:** immutable ops.
- **S4:** ticket-store menu (screen S02).
- **S5:** load a generated set; sort/dedupe/histogram in the app.
- **Gate:** `{{ACCEPTANCE}}`=AC-T1/T2.

---

## F7.2 — Optimizer (2 strategies)
**User stories** — *As a cost-conscious player,* I reduce a large ticket set by
"reserve X per 10" or "collapse lines sharing X numbers."
**Acceptance:** AC-T3, AC-T4. **Module:** `core/tickets/optimizer`.

**Chain**
- **S1:** `optimize(set, strategy: {kind:'reservePerBlock'; x:1..9} | {kind:'sameNumber'; x:number; positions?:number[]}): TicketSet`.
- **S2:** reservePerBlock x=3 → each block of 10 → 3 lines; sameNumber x collapses lines sharing X numbers to one representative.
- **S3:** implement both per Doc 05 §C.
- **S4:** screen S31.
- **S5:** optimize a 60-line set to ~18; verify counts.
- **Gate:** `{{ACCEPTANCE}}`=AC-T3/T4.

---

## F7.3 — Searcher (1/2/3-number combos)
**User stories** — *As an analyst,* I search how often 1/2/3-number combinations
appeared over a range, with appear-count and skips, and the exact draws.
**Acceptance:** AC-T5. **Module:** `core/tickets/searcher` (+ SkipsEngine).

**Chain**
- **S1:** `search(combos, {range, positions}): { combo; appearCount; nowSkips; avgSkips; actualSkips:number[]; hitDraws:string[] }[]`.
- **S2:** reproduce `nsSearch`/`nsStat` semantics (Doc 09 §2.3); auto-generate all 1/2/3 combos; sort by appearCount or nowSkips.
- **S3:** scan history; count + skips per combo (reuse F2.1).
- **S4:** screen S32.
- **S5:** search all 2-number combos over past-260; top pair's hit-draws correct.
- **Gate:** `{{ACCEPTANCE}}`=AC-T5.

---

## F7.4 — WinChecker
**User stories** — *As a player,* after the draw I find all my tickets matching
`=,>,<,≥,≤` a count, bonus-aware.
**Acceptance:** AC-T6. **Module:** `core/tickets/winchecker`.

**Chain**
- **S1:** `check(set, draw, op: '='|'>'|'<'|'>='|'<=', n: number, bonus?: boolean): Ticket[]`.
- **S2:** given draw D and `>=4`, exactly lines sharing ≥4 mains returned; bonus flag also requires bonus match; result annotated `"m + b"` like `CheckWinning` (Doc 09).
- **S3:** intersect + compare; bonus handling.
- **S4:** screen S33.
- **S5:** check a set against a known draw; assert the ≥4 set.
- **Gate:** `{{ACCEPTANCE}}`=AC-T6.

---

## F7.5 — Export & print
**User stories** — *As a player,* I export matches/tickets to TXT/HTML/XLSX and print
tickets (columns, title, date).
**Acceptance:** AC-T7. **Module:** `Exporter` port (`data/export`) + screen S40/S41.

**Chain**
- **S1:** port `Exporter { export(rows, format: 'txt'|'html'|'xlsx'): Blob|string }`; print layout `{columns, title?, dateTime?}`.
- **S2:** each format contains identical logical content; TXT round-trips the ticket format (`k`-joined … `tw`, Doc 07 §4.4) if using native format.
- **S3:** implement adapters; print via the shell.
- **S4:** ticket-store + check-win menus.
- **S5:** export a set to all three; open each.
- **Gate:** `{{ACCEPTANCE}}`=AC-T7; formats content-equivalent.

---

## F7.6 — Tickets UI
**User stories** — *As a player,* the ticket store shows my lines with a right-click
menu (sort/dedupe/tag/hits/convert-to-wheel/optimize/save/print/export).
**Acceptance:** AC-T1..T7. **Module:** `apps/desktop` screen S02 (+ S31/S32/S33 links).

**Chain** — S1 `<TicketStore/>` grid + context menu wired to F7.1–F7.5 + F5.4 convert; S2 (E2E) Flow-7/8 (Doc 06); S3 build; S4 wire use-cases; S5 drive Flow-7/8. Gate: all AC-T*.

### Epic 7 exit criteria
Store ops, both optimizers, search, win-check, and 3 export formats verified;
Flow-7 and Flow-8 pass end-to-end.
