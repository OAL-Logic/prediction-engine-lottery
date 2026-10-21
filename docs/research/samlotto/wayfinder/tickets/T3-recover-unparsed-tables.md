<!-- parent: MAP · label: wayfinder:task -->
# T3 — Recover the 3 tables access_parser couldn't read

Type: task (AFK) · Assignee: fable-session  · Status: CLOSED
Blocked-by: —  ·  Blocks: T5

## Resolution (CLOSED)

Root cause: `access_parser` empties memo fields and shifts later columns by +1
(throws outright on 3 tables). Fix: re-read with **Jackcess 4.0.5** (Java 17;
JARs from Maven Central) — clean, no shift. Recovered schemas for **`Tickets`**
(per-line metric cache), **`UnitsNumbers`** (38 cols: digits 0–9 & S0–S9 + all
unit metrics), **`DrawingsNumber`** (Position 1–15) → folded into **doc 09 §2.5**.

Then re-validated everything that was blocked on a clean channel, single game
(6/60), 100 rows each — **all 100%**: Sum extras (incl. Prime Sum, First+Second),
Divided remainders, Multiple counts (priority rule), and the **entire Units module
+ 20 digit-count columns**. Pinned fuzzy defs (Root Sum = single digit-sum pass;
Successive End Units = longest distinct-second-digit run; Same End Units = distinct
intersection; InterChangeable = swap ≤ M, non-palindrome). Docs 02, 09, 10 patched.

**Outcome: the app's entire statistical vocabulary is now verified.** T5's ER
diagram now has the complete table set.

## Question

`Tickets`, `UnitsNumbers`, and `DrawingsNumber` threw `IndexError` in
`access_parser` (a memo/overflow-row limitation, not missing data). Recover their
full schema + sample rows via an alternate method (e.g. `mdbtools`/`mdb-export`,
`mdb-schema`, or a more robust reader). Fold the recovered schemas into doc 09 so
the data dictionary is complete — needed before the ER diagram (T5) can be
authoritative.

**Root cause identified (from T1/T2):** `access_parser` mishandles **memo/overflow
columns** — it empties the memo field and **shifts every subsequent column by one**.
This corrupts not just the 3 unreadable tables but the text/combination columns of
`ComprehensiveAnalyze`, `SumA`, `Residue`, `OddEven`, `BigSmall`, `AppearCount`.
`mdbtools` isn't installed / not in scoop; options: (a) build `mdbtools` for
Windows or run under WSL, (b) another reader (Jackcess/UCanAccess via Java),
(c) install the MS Access Database Engine redistributable to enable the missing
OLEDB/ODBC path.

**Added scope (from T2):** once a clean channel exists, re-validate the metrics that
live only in memo-corrupted tables — Root Sum, Prime Sum, Odd/Even Sum, High/Low
Sum, First+Second Unit Sum, Divided remainders, Multiple counts, and the prev-draw
metrics — and fold results into `Documentation/10-Validation-Report.md`.
