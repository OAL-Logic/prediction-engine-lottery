# Glossary — Ubiquitous Language

One canonical term per concept, its definition, and the authoritative source.
Grounded in the validated math (doc 10) and real schema (doc 09). Use these names
consistently in docs and any rebuild.

> **Naming decisions for you to confirm** (I picked a default; change if you prefer):
> 1. **Combination** vs *Line* vs *Ticket* — I use **Combination** for a set of
>    numbers and **Ticket** only for a combination staged to play. ✎
> 2. **Draw** vs *Drawing* — I use **Draw** (noun) / **Drawings** (the history
>    collection), matching the app's toolbar. ✎
> 3. **Recommended pool** for the predictor's output (vs *prediction numbers*). ✎
> 4. **Pool max (M)** for the largest number (vs *From*, the DB column name). ✎

---

## Core objects
| Canonical term | Definition | Source / aliases |
|---|---|---|
| **Game** | A lottery configured by pick size, pool max, and optional bonus. | `Lottery`; DB `Lottery` table |
| **Pick (k)** | How many main numbers are drawn (2–9). | DB `Match`; manual "pick 2…9" |
| **Pool max (M)** | Largest selectable number (pool is `1..M`, up to 90). | DB `From` |
| **Bonus** | Extra/supplementary number(s) drawn from a separate pool of size `PB_Max`. | DB `Bouns`/`PB_Max`; code misspells "Bouns" |
| **Draw** | One dated result: `k` main numbers (+ bonus). | `Drawing`; DB `Draw`/`Draings` (sic) |
| **Drawings** | The historical collection of draws for a game (a `.Txt` file). | `Drawings/*.Txt` |
| **Combination** | An unordered set of `k` numbers from the pool. | *line*, *combo* |
| **Ticket** | A combination staged to play; may carry a **tag**. | `Tickets` table/store |
| **Ticket store** | The working list of tickets (right panel). | `Tickets.Txt` |
| **Tag** | Per-ticket mark (`X` or blank) for bulk keep/delete. | doc 01 F4 |

## Skips & frequency
| Term | Definition |
|---|---|
| **Hit** | A pattern/number occurring in a draw. |
| **Actual Skips** | The sequence of gap lengths between successive hits of a pattern. |
| **Average Skips** | Mean of the Actual-Skips sequence (`Σ gaps / #gaps`). |
| **Now Skips** | Draws since the pattern last hit. `Now > Average` ⇒ "due". |
| **Hot / Cold / Warm number** | Most-hit / least-hit / in-between numbers over a chosen range. |

## Combination metrics (all ✅ validated, doc 10)
| Term | Definition (canonical) |
|---|---|
| **AC** (Arithmetic Complexity) | `#{distinct pairwise differences} − (k−1)`. |
| **Sum** | Σ of the numbers. |
| **Average Value** | `Σ // k` (integer **floor** division). |
| **Root Sum** | **Single** digit-sum pass of the total (e.g. 257 → 14); *not* an iterated digital root. |
| **Odd / Even Count / Sum** | Count/sum of odd (even) numbers. |
| **Low / High** | Split at `⌊M/2⌋`: low = `1..⌊M/2⌋`, high = the rest. |
| **Prime** | Count/sum of prime numbers (2 counts). |
| **Decade** | A block of ten by value: `⌊n/10⌋` (0–9, 10–19, …) — **fixed tens**. |
| **Decade Group Count** | # of adjacency groups among the distinct decades present. |
| **Different Decade Count** | # of distinct decades present. |
| **Divided (remainder)** | Partition of the pool by `n mod D` (D = 3…10); count per remainder. | 
| **Modality** | The concatenated per-group counts (e.g. Odd/Even `00101`, Divided `311`). |
| **Multiple** | Assign each number to the first of 7→5→3→2→1 it divides by (priority); count per bucket. |
| **Distance** | Adjacent **absolute** differences **in draw order**: Max / Average(`//`) / Different(distinct). |
| **First-Last Distance** | `max − min` (sort-invariant). |
| **Successive** | Longest run of **draw-order-adjacent** consecutive integers, `0` if length <2. |
| **Successive Groups** | # of such runs of length ≥2. |
| **Odd / Even Successive** | Longest run of draw-order-adjacent odd (even) numbers, ≥2 else 0. |

## Digit / unit terms (✅ validated, doc 10)
| Term | Definition |
|---|---|
| **First digit** | Tens digit `⌊n/10⌋` (0 for `n<10`). |
| **Second / End unit** | Ones digit `n % 10`. |
| **Unit Number Sum** | Σ of second digits. |
| **Successive End Units** | Longest run of consecutive **distinct second digits**, 0 if <2. |
| **Same End Units with Last Drawn** | Size of the **distinct** second-digit intersection with the prior draw. |
| **InterChangeable Units Count** | Numbers whose digit-swap is `≤ M` and not a palindrome. |
| **Unit Number Group Count** | # adjacency groups among the distinct second digits. |

## Filtering
| Term | Definition |
|---|---|
| **Filter** | A predicate over a combination; failing lines are removed. |
| **Filter tag** | Stable filter id 1–69 (`Condition_Tag`). |
| **Filter engine type** | 1 = base (scalar range), 2–4 = advanced (bundle / set / special). |
| **Condition (parameter)** | A filter's allowed range/set (e.g. `1-5`). |
| **Auto-generate default condition** | Fill a filter's range from history (prev 2/3/5/10/20/30/50/current). |
| **Logical condition** | How selected filters combine: **AND** / **OR** / **N-of-M** (fault-tolerant). |
| **Fault tolerance** | The N-of-M mode; pass if N…M of the filters match (guards the jackpot line). |
| **Filter assistant** | Per-filter frequency + trend charts for setting parameters. |
| **Filtering report** | Per-filter count of lines removed. |

## Wheeling
| Term | Definition |
|---|---|
| **Wheel** | A covering design turning `n` chosen numbers into multiple `k`-lines. |
| **Full wheel** | All `C(n,k)` lines. |
| **Abbreviated wheel** | Minimal line set meeting a stated match **guarantee**. |
| **Guarantee** | "If X of the `k` winners are among your `n`, ≥1 line matches Y." |
| **Wheel size (n)** | How many numbers are wheeled (≤ 36). |
| **Letter map** | The wheel formula expressed as letter-combos, instantiated by substituting numbers. |

## Prediction
| Term | Definition |
|---|---|
| **Formula** | One of `Formula-1 … Formula-6`, a prediction strategy (+ algorithm/offset/depth). |
| **Recommended pool** | The predictor's output set of numbers (~17–27); play/wheel from it. |
| **Eliminated** | Numbers the predictor rules out. |
| **Verification** | Replay a formula over history; measure winners falling in the recommended pool. |
| **Hit-rate** | `Σ correctCount / Σ winning numbers` over a verification range. |
| **Drawings Trend** | Manual, chart-driven next-draw prediction. |

## Generation, optimization, search, checking
| Term | Definition |
|---|---|
| **Full generator** | Produce all `C(pool, k)` combinations. |
| **Wheel generator** | Produce a wheel's lines from the selected pool. |
| **Positional** | Cross-product of a chosen number set per position. |
| **Random / Smart** | Random lines / analysis-depth-weighted random lines. |
| **Quick pick** | One-click hot / cold / last-N number selection. |
| **Optimization** | Cost-reduction of the ticket set: same-number reduction, or reserve-X-per-10. |
| **Search (past drawings)** | Frequency/skips of 1/2/3-number combinations across history. |
| **Check winning** | Match tickets against a draw by `=,>,<,≥,≤` a match count (bonus-aware). |

---

## Spelling normalizations (app/code → canonical)
`Bouns` → **Bonus** · `Draings`/`Draings` → **Draw/Drawings** · `perdiction`/`Perdiction`
→ **Prediction** · `Successiv` → **Successive** · `BigSmall` (table) → **Low/High** ·
`Residue` (table) → **Divided** · `BeforeDrawings`/`Before` → **Previous/Prior Draw** ·
`ComprehensiveAnalyze` → **Base analysis** · `ns…` tables → **Search**.
