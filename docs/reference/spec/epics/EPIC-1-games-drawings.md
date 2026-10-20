# EPIC 1 — Games & Drawings (data foundation)

> **Navigation**: [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [🌐 Dynamic Portal](../../dynamic-portal.html) · [⬅️ 99 — Weekly Maintenance Protocol](../99-maintenance-protocol.md) · [EPIC 2 — Statistical Analysis Engine ➡️](EPIC-2-statistics.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [F1.8 — Results file format (parse/serialize `.Txt`)](#f1-8-results-file-format-parse-serialize-txt)
- [F1.1 — Game model & catalog](#f1-1-game-model-catalog)
- [F1.2 — Open / choose game](#f1-2-open-choose-game)
- [F1.3 — Create a new game (custom rules)](#f1-3-create-a-new-game-custom-rules)
- [F1.4 — Draw history CRUD (add / insert / modify / delete)](#f1-4-draw-history-crud-add-insert-modify-delete)
- [F1.5 — Import / export drawings](#f1-5-import-export-drawings)
- [F1.6 — Split drawings by weekday](#f1-6-split-drawings-by-weekday)
- [F1.7 — Online update drawings](#f1-7-online-update-drawings)
  - [Epic 1 exit criteria](#epic-1-exit-criteria)

</details>
<!-- TOC_BLOCK_END -->

**Goal:** a rebuild can open any of 200+ games, know its rules, and manage its draw
history end-to-end (add/insert/modify/delete/import/export/split/online-update).
**Verified source:** Doc 01 §A, Doc 07 §4, Doc 09 §2.1. **Depends on:** nothing
(build first). **Phase:** 1.

**Features:** F1.1 Game model & catalog · F1.2 Open game · F1.3 Create game ·
F1.4 Draw CRUD · F1.5 Import/export · F1.6 Split by weekday · F1.7 Online update ·
F1.8 Results file format.

Every feature runs the 5-stage chain from `../02-conventions.md`; prompts below are
pre-filled and ready to paste. Each ends with the quality gate.

---

## F1.8 — Results file format (parse/serialize `.Txt`)
> Build this first: everything else needs it. Format (Doc 07 §4.1):
> `M/D/YYYY  NN NN … [BB]` — space-delimited, non-padded date, 2-digit numbers,
> optional trailing bonus column(s).

**User stories**
- *As the system,* I parse a `Drawings/*.Txt` file into `Draw[]` so history loads.
- *As the system,* I serialize `Draw[]` back to the same format so export round-trips.
- *As a maintainer,* malformed lines are reported, not silently dropped.

**Acceptance:** AC-D5. **Module:** `core/game` (`parseDrawings`, `serializeDrawings`).

**Chain**
- **S1 Design:** `parseDrawings(text: string, game: Pick<Game,'pick'|'bonus'>): {draws: Draw[]; errors: {line:number; reason:string}[]}` and `serializeDrawings(draws: Draw[]): string`. Pure.
- **S2 Test:** fixtures = `fixtures/drawings/BrazilMegaSenaBR660.Txt` first 6 lines (Doc 07 §4.1 shows `3/11/1996 04 05 30 33 41 52`) and a Powerball line with trailing bonus. Assert count, first/last draw, bonus split, round-trip `serialize(parse(x)) ≡ x` (modulo whitespace), and that a malformed line yields an error entry not a throw.
- **S3 Implement:** split on whitespace; first token = date; next `pick` tokens = mains; remaining = bonus. Validate counts against the game rules.
- **S4 Integrate:** used by `ResultsRepository` (F1.1/data).
- **S5 Verify:** parse the real Mega-Sena file; print draw count and first/last rows.
- **Quality gate:** template in `../02-conventions.md` with `{{FIXTURES}}`=the two files above, `{{ACCEPTANCE}}`=AC-D5, `{{INTERFACE}}`=the two functions.

---

## F1.1 — Game model & catalog
**User stories**
- *As a player,* I see all available games grouped by region so I can pick one.
- *As a player,* I open a game and the app knows its pick size, pool max, and bonus.
- *As the system,* I seed 222 games from `fixtures/games-catalog.csv`.

**Acceptance:** AC-D1. **Module:** `core/game` (`Game` type) + `data/catalog` (`GameCatalog` port).

**Chain**
- **S1 Design:** port `GameCatalog { list(): Game[]; get(id): Game; create(rules): Game }`; `Game` per `01-project-structure.md`. `From`→`maxNumber`, `Match`→`pick`, `Bouns`/`PB_Max`→`bonus`.
- **S2 Test:** fixture = `games-catalog.csv`. Assert 222 games load; `get('brazil-mega-sena')` = `{pick:6, maxNumber:60, bonus:undefined}`; a bonus game (Powerball) has `bonus.maxNumber`.
- **S3 Implement:** CSV loader in `data/catalog`; in-memory fake for tests.
- **S4 Integrate:** `openGame` use-case loads catalog + results via `ResultsRepository`.
- **S5 Verify:** list games; open Mega-Sena; print rules + draw count.
- **Quality gate:** `{{FIXTURES}}`=games-catalog.csv; `{{ACCEPTANCE}}`=AC-D1.

---

## F1.2 — Open / choose game
**User stories**
- *As a player,* I open the game list, pick one, and it becomes the active game.
- *As a player,* the active game's rules + latest draws drive every other screen.

**Acceptance:** AC-D1. **Module:** `app/usecases/openGame` + `SettingsStore` (persist last game).

**Chain**
- **S1 Design:** `openGame(id): {game: Game; history: DrawHistory}`.
- **S2 Test:** opening sets active game; `DrawHistory.all().length` matches file.
- **S3 Implement:** orchestrate GameCatalog + ResultsRepository + build `Ctx` defaults.
- **S4 Integrate:** screen **S10** (game list) → sets app state; persists via SettingsStore.
- **S5 Verify:** launch app, open two games, confirm the workspace re-scopes.
- **Quality gate:** `{{ACCEPTANCE}}`=AC-D1.

---

## F1.3 — Create a new game (custom rules)
**User stories**
- *As a power user,* I define a new game (name, pick, pool max, bonus count/max) and it appears in the catalog with an empty history.

**Acceptance:** AC-D6. **Module:** `GameCatalog.create` + `data/catalog` persist + screen **S11**.

**Chain**
- **S1 Design:** `create({name, pick, maxNumber, bonus?}): Game` with validation (2≤pick≤9, 1<maxNumber≤90).
- **S2 Test:** create pick=5/max=50/bonus=1×12 → present in `list()`; invalid rules rejected.
- **S3 Implement:** append to catalog store; create empty results file.
- **S4 Integrate:** screen **S11** form → use-case.
- **S5 Verify:** create a game in the UI; reopen app; it persists.
- **Quality gate:** `{{ACCEPTANCE}}`=AC-D6.

---

## F1.4 — Draw history CRUD (add / insert / modify / delete)
**User stories**
- *As a player,* I add the latest draw by date + numbers.
- *As a maintainer,* I insert a missed draw at the right position, modify a wrong one, or delete a duplicate — with confirmation.

**Acceptance:** AC-D2, AC-D3. **Module:** `DrawHistory` (mutation methods) + `ResultsRepository` persist + screens **S12/S13**.

**Chain**
- **S1 Design:** `add(draw)`, `insertAt(index, draw)`, `modify(index, draw)`, `delete(index)`; each validates numbers against game rules; returns a new `DrawHistory` (immutable) + persists via port.
- **S2 Test:** add `07/09/2026=04 05 30 33 41 52` → count+1, present; modify/delete reflect exactly; invalid (dup number, out of range) rejected.
- **S3 Implement:** immutable ops + repository write-through.
- **S4 Integrate:** screens S12 (list) / S13 (add-insert form); confirm dialog on delete.
- **S5 Verify:** round-trip add→modify→delete in the UI; reopen; state correct.
- **Quality gate:** `{{ACCEPTANCE}}`=AC-D2, AC-D3.

---

## F1.5 — Import / export drawings
**User stories**
- *As a player,* I import a `.Txt` of results and they all load.
- *As a player,* I export/back up my history to a `.Txt` that round-trips.

**Acceptance:** AC-D5. **Module:** `app/usecases/importDrawings|exportDrawings` + F1.8 format + `Exporter`.

**Chain** — S1 `importDrawings(file)`, `exportDrawings(): string`; S2 round-trip a real file byte-equivalently (modulo ordering/whitespace); S3 use F1.8; S4 screen S12 Import/Export buttons + Tauri file dialog; S5 import then export, diff the files. Gate: AC-D5.

---

## F1.6 — Split drawings by weekday
**User stories**
- *As a player of a multi-draw game,* I keep only (e.g.) Thursday draws.

**Acceptance:** AC-D4. **Module:** `DrawHistory.splitByWeekday(weekday)` + screen **S14**.

**Chain** — S1 `splitByWeekday(day: 0..6): DrawHistory`; S2 fixture with mixed weekdays → only chosen remain; S3 filter by parsed date's weekday; S4 screen S14 with weekday picker + confirm; S5 verify in UI. Gate: AC-D4.

---

## F1.7 — Online update drawings
**User stories**
- *As a player,* I click Update and the latest official draws are fetched and appended (no duplicates).

**Acceptance:** AC-D2 (append semantics). **Module:** `UpdateClient` port + `app/usecases/updateDrawings` + screen **S15**.

**Chain**
- **S1 Design:** port `UpdateClient { fetch(game): Promise<Draw[]> }`; use-case merges, dropping draws already present (by date+numbers).
- **S2 Test:** given a fake client returning 3 draws (1 already present) → 2 appended; ordering preserved.
- **S3 Implement:** merge/dedupe in the use-case (pure), I/O in the adapter.
- **S4 Integrate:** screen S15; real adapter is a per-game source (configurable URL; leave a stub adapter + interface — the *contract* is what matters, not any specific site).
- **S5 Verify:** run with the fake client end-to-end; show appended count.
- **Quality gate:** `{{ACCEPTANCE}}`=AC-D2; note: the network adapter is swappable and must not leak into core/app.

---

### Epic 1 exit criteria
All F1.* quality gates green; `openGame` → analyze/generate screens have real data;
importing the Mega-Sena fixture and splitting to one weekday both verified in the UI.

---
> **Next Steps**: [⬅️ 99 — Weekly Maintenance Protocol](../99-maintenance-protocol.md) · [🏠 Reference Hub](../../INDEX.md) · [📂 04. Clean-Room Engineering Epics](../INDEX.md) · [EPIC 2 — Statistical Analysis Engine ➡️](EPIC-2-statistics.md)
