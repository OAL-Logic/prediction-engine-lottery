# 06 — User Flows (end-to-end, with concrete examples)

Each flow lists screens touched (`[Form]`), user actions, and system effects.
Evidence: `[CHM Quick Start]` + per-topic manual pages.

> Sequence diagrams for the play pipeline and predict/verify are in
> [`12-Diagrams.md`](12-Diagrams.md).

---

## Flow 0 — The canonical "play a lottery" pipeline
The whole app is one funnel: **choose game → refresh results → generate a large
candidate pool → cut it with filters → reduce cost with wheels/optimize → verify/
predict → check winnings.**

```
Lottery ─▶ Drawings ─▶ Generate ─▶ Filter ─▶ Wheel/Optimize ─▶ (Predict) ─▶ Play ─▶ Check Win
  A          A/ B          C          D            E/F              E                    F
```

---

## Flow 1 — Open a game & update results
1. Toolbar **Lottery** → `[TLotteryForm]` → select "Brazil Mega Sena" → OK.
   - System loads `Drawings/BrazilMegaSenaBR660.Txt` (pick 6, 1–60), writes `Lottery_Set.ini`.
2. Toolbar **Drawings** → `[TDrawingsForm]`.
3. **Update** → `[TupdateForm]` → fetch latest draws online.
   - Or **Add** a draw manually: date `07/09/2026`, numbers `04 05 30 33 41 52`.
4. Optional **Split** → `[TSplitForm]` → keep only Thursday draws.

**Example draw file line**: `3/11/1996 04 05 30 33 41 52` (date + 6 zero-padded numbers).

---

## Flow 2 — Statistical analysis to inform filters
1. Toolbar **Statistics** → `[TstatisticForm]`.
2. Set **range** = previous 30, **positions** = all.
3. Open **Odd-Even** tab: observe last-30 odd-count distribution (e.g. 1→5, 2→5, 3→4, 4→2, 5→2).
4. Open **Sum** tab: note sum clusters around 150–210.
5. Click a column value → read **Actual/Average/Now Skips** to see what's "due".
6. Open **Hot-Cold** → note hot set {…} and cold set {…} over last 30.

Outcome: you now have data-backed target ranges for the next step.

---

## Flow 3 — Generate a candidate pool
**Option A — Full generate from a chosen pool**
1. Numbers grid: select 12 numbers you like (turn red).
2. Radio **Full Generator** → **Generate Tickets** → `C(12,6) = 924` lines land in the ticket store.

**Option B — Wheel a pool (cost-controlled from the start)**
1. Select 10 numbers.
2. Radio **Wheels Generator** → formula "pick6, wheel10, if-5-match-4".
3. **Generate Tickets** → ~17–20 lines with a match-4 guarantee.

**Option C — Quick pick** hot numbers → generate N random-from-hot lines.

---

## Flow 4 — Filter the pool down  (the core)
1. Setup panel → **Base Filters** `[TbasefiltersForm]`.
2. Select filters: Odd Count, Sum, AC, Successive, Low-High, Prime Count.
3. Click **Generate Default Condition** (range = previous 20) → auto-fills:
   - Odd Count `1–5`, Sum `120–210`, AC `4–8`, Successive `0–2`, Low `2–4`, Prime `1–3`.
4. Tune with **Assistant** (frequency/trend chart) where desired.
5. Set **Logical Condition** = `AND` (strict) — or `4-6` to keep a fault margin.
6. **Start Filtering** → 924 lines cut to, say, ~60.
7. **Filtering Report** `[TfilterrepForm]` → see how many each filter removed.

**Worked example of one predicate**: line `05 11 14 15 22 39` → Sum 106.
If Sum filter = `120–210`, this line is **removed** (106 < 120).

---

## Flow 5 — Reduce cost further
- **Advanced filter** "Delete History Drawings" → drop any line equal to a past draw.
- **Optimization** `[TopForm]`: "each of 10 combinations reserve 3" → 60 lines → ~18.
- Or "convert tickets → wheel" to re-express as a compact wheel.

---

## Flow 6 — Predict & verify (Pro)
1. Toolbar **Prediction** → `[TPredictionForm]` → **Predictor** tab.
2. Choose **Formula-3**, algorithm 0, depth 30 → **Predict Now**.
   - Output: `Prediction Numbers: 07 19 23 34 41 52` (+ bonus if any).
3. Switch to **Verification** tab → same formula → **Verification** over last 100 draws.
   - See per-draw hit counts + overall accuracy + Actual Skips.
4. If the formula verifies well, push its numbers into the pick panel and wheel them.

---

## Flow 7 — Edit, print, play
1. Ticket store menu `[Editing Tickets]`: **Sort low→high**, **remove duplicates**, **Numbers Hits** (see which numbers dominate your set).
2. **Add Bonus Number** to each line if required.
3. **Print Tickets** `[TprintForm]`: columns=5, print title + date.
4. Or **Save To Txt / Formate Export** for a betting service.

---

## Flow 8 — After the draw: check winnings
1. **Drawings → Update** to load the official result.
2. Toolbar **Check Win** → `[TcheckForm]`.
3. Choose the draw, operator `>=`, match count `4`, (Bonus checkbox if wanted).
4. **Check Now** → all lines matching ≥4 shown.
5. Right-click → **Save To Excel/HTML/Txt**.

---

## Flow 9 — Search hot/cold combinations
1. Toolbar **Search** → `[Search Past Drawings]`.
2. Range = past 260, generate all **2-number** combinations.
3. **Search** → sort by Appear Count desc.
4. Top row → right panel lists every draw containing that pair; read its Now Skips
   to judge if the hot pair is "due" again.

---

## Flow 10 — Add a brand-new game
1. Toolbar **Lottery → New** → `[TNewLotteryForm]`.
2. Enter name, pick size (e.g. 5), max number (e.g. 50), bonus count/name.
3. OK → new empty drawing file created; use Import or Add to populate history.
