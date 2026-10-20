# 04 — Wheeling Systems (covering designs)

> **Navigation**: [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [🌐 Dynamic Portal](../dynamic-portal.html) · [⬅️ 03 — Filters Reference (68 filters: 50 base + 18 advanced)](03-Filters-Reference.md) · [05 — Prediction, Generation, Optimization & Search ➡️](05-Prediction-Generation-Optimization-Search.md)

<!-- TOC_BLOCK_START -->
<details open>
<summary><strong>📑 On This Page (Table of Contents)</strong></summary>

- [The two wheel types](#the-two-wheel-types)
  - [Full wheel](#full-wheel)
  - [Abbreviated wheel](#abbreviated-wheel)
- [Letter-map mechanic (how a wheel is expressed)](#letter-map-mechanic-how-a-wheel-is-expressed)
- [Wheel file format on disk  `Formula/*.Wheels`  `[DATA]`](#wheel-file-format-on-disk-formula-wheels-data)
- [Custom & advanced wheeling](#custom-advanced-wheeling)
- [Rebuild contract](#rebuild-contract)

</details>
<!-- TOC_BLOCK_END -->

A **wheeling system** takes a set of `n` numbers you choose ("the pool") and
arranges them into multiple k-number lines that **guarantee** a minimum win if a
certain number of the drawn numbers are within your pool. It is applied
mathematics (covering designs), not prediction.

Library size: **2200+ wheel formulas**, covering pick-2 … pick-7, wheel size up
to **36** numbers, pool numbers 1–90. (Free edition: wheels locked.)

---

## The two wheel types

### Full wheel
All `C(n, k)` combinations of your `n` numbers. Maximum coverage, maximum cost.

| n (pick-6) | Lines = C(n,6) |
|---|---|
| 8 | 28 |
| 9 | 84 |
| 10 | 210 |
| 11 | 462 |
| 12 | 924 |
| 13 | 1716 |
| 14 | 3003 |
| 15 | 5005 |

**Guarantee**: if all k winning numbers are in your n, you win the jackpot
**plus** many lower-tier prizes. Even a partial hit yields multiple wins.

### Abbreviated wheel
A **minimal** subset of combinations that still guarantees a specified lower-tier
match. Example (pick-6, n=8, "if 4 of 6 are in your 8 → guaranteed ≥1 line
matching 4"): only **7 lines** instead of 28.

**Guarantee wording** the app reports (n=8 full-wheel example):
- If all 6 winners ∈ your 8 → 1 jackpot line, 11 lines match-5, 16 lines match-4.
- If any 5 of 6 ∈ your 8 → 2 lines match-5, 15 match-4, 11 match-3.
- If any 4 of 6 → 5 lines match-4, 15 match-3.
- If any 3 of 6 → 9 lines match-3.

Marketing example (Powerball, n=10, "if 5 matches 4"): **17 tickets** instead of
252, guaranteeing a 4-number prize (plus several 3s/4s) when the 5 winners are in
your 10; jackpot odds within the wheel ≈ 6.75%.

---

## Letter-map mechanic (how a wheel is expressed)

Numbers are mapped to letters A, B, C… in ascending order; the wheel formula is a
fixed list of letter-combinations, independent of the actual numbers:

```
Pool (pick-6, n=8):  A=05 B=09 C=16 D=23 E=26 F=31 G=37 H=45
Full wheel = all 28 six-letter combos: ABCDEF, ABCDEG, ABCDEH, … , CDEFGH
Abbrev "if-4" wheel = 7 combos: ABCDEG, ABCFGH, ABDEFH, ACDEFH, ADEFGH, BCDEFG, BCDEGH
```

To generate lines: substitute each letter with its number. This separation
(formula = letters; instance = numbers) is why one formula file serves any pool.

---

## Wheel file format on disk  `Formula/*.Wheels`  `[DATA]`

**Naming convention** (observed):  `PICK-WHEELSIZE-GUARANTEE-VARIANT.Wheels`

| Field | Meaning | Range observed |
|---|---|---|
| PICK | game pick size | 02–07+ |
| WHEELSIZE | how many numbers wheeled (n) | ≥ PICK, up to 36 |
| GUARANTEE | guaranteed match tier | 1..PICK |
| VARIANT | alternative formula for same spec | 1, 2, … |

Examples: `02-06-2-2` = pick-2, wheel 6, guarantee 2, variant 2 ·
`06-08-4-2` = pick-6, wheel 8 numbers, guarantee match-4, variant 2 ·
`06-07-2-1` = pick-6, wheel 7, guarantee 2.

File **contents are a proprietary binary/packed encoding** (not plain text) — the
letter-combination table. For a rebuild, do **not** copy these files; regenerate
equivalent covering designs:
- Full wheels: enumerate `C(n,k)` directly.
- Abbreviated wheels: use published covering-design tables or a greedy/ILP
  covering solver to hit the guarantee with minimal lines. Store as your own
  letter-index tables (JSON), keyed by `(k, n, guarantee)`.

---

## Custom & advanced wheeling
- `TcustomwheelForm` — user-defined wheels ("advanced wheeling and custom wheeling", `[CHM Welcome]`).
- **Convert tickets → wheel** — turn an existing ticket set back into a wheel structure (`[CHM Editing Tickets]`).

## Rebuild contract
```
Wheel = { k, n, guarantee, variant, letterCombos: number[][] }   // 1-indexed letters
generate(wheel, pool /*n numbers ascending*/) =
  wheel.letterCombos.map(lc => lc.map(i => pool[i-1]))
guaranteeReport(wheel) = precomputed "if X of k in pool → Y lines match Z"
```

---
> **Next Steps**: [⬅️ 03 — Filters Reference (68 filters: 50 base + 18 advanced)](03-Filters-Reference.md) · [🏠 Reference Hub](../INDEX.md) · [📂 01. Architecture & Data Structures](INDEX.md) · [05 — Prediction, Generation, Optimization & Search ➡️](05-Prediction-Generation-Optimization-Search.md)
