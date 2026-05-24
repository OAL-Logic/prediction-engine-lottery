---
title: Idea-by-Idea Evaluation — Three Experts
sources: smartluck.com (3 articles)
project: Prediction Engine
date: 2026-04-25
---

# Idea-by-Idea Evaluation

Three experts evaluate each major idea:

- **A** — Statistician / Mathematician (validity of the math)
- **B** — Software Architect (fit with `lottery-engine/` codebase)
- **C** — Product / OSS Strategist (user value + OSS-magnet effect)

Verdict legend: ✅ adopt · 🔧 refactor existing · 🧪 already covered ·
❌ reject · ⚠️ adopt with guardrails

---

## 1. Game Selection — choose smaller number fields

**Article claim.** Pick lotto games with smaller `n` (number field), or
pick-5 instead of pick-6, because odds are dramatically lower.

- **A** — True by combinatorics. `C(60,6) = 50,063,860` for Mega-Sena vs
  `C(39,5) = 575,757` for Fantasy 5. Trivially correct.
- **B** — A `cross-game odds comparator` is a 50-line module. Iterate
  every registered adapter, compute `C(n,k) * (bonus_pool)`, expose as
  CLI + FastAPI endpoint.
- **C** — Perfect onboarding feature for the Expo app: "Which game
  should I play?" → ranked table with friction (price, draw frequency,
  jurisdiction). Strong Nerd-mode hook.

**Verdict: ✅ adopt** as `engine/odds/comparator.py` + Expo onboarding step.

---

## 2. Number Selection (Handicapping)

**Article claim.** Past draw frequencies predict future draws (loosely).

- **A** — In a perfectly fair lottery, draws are independent → past has
  zero predictive value. In practice, mechanical bias has been
  documented (Pennsylvania Daily Number 1980; some bingo machines).
  The chi-squared goodness-of-fit test is the right gate: only
  surface "hot" recommendations when the test rejects uniformity.
- **B** — `frequency.py` already implements this exactly: counts,
  chi2_statistic, chi2_p_value. We just need to *use* the p-value at
  the API/UX layer to disable hot-number recs when the game looks fair.
- **C** — Frame as "the engine literally tells you whether handicapping
  works for THIS game." That's defensible and educational.

**Verdict: ⚠️ adopt with guardrails** — surface chi² gate in API + UI.

---

## 3. Balanced Wheels

**Article claim.** Pick a larger group of numbers, generate a set of
tickets that "wheels" them so that hitting K of them guarantees a prize
of tier T.

- **A** — Real combinatorial mathematics (covering designs). A `C(n,k,t)`
  covering ensures any t-subset of an n-set is contained in at least one
  of the listed k-blocks. The math is well-studied (La Jolla Covering
  Repository, Stinson's textbook). No statistical magic — just guaranteed
  coverage of the loss-redistribution surface.
- **B** — New top-level module: `engine/wheels/`. Components:
  - `full_wheel.py` — full coverage (`C(n,pick)` tickets, expensive but
    100% guaranteed).
  - `abbreviated.py` — load published covering designs from a static
    table (we ship a JSON of LJCR best-known sizes for k≤12, t≤5).
  - `key_wheel.py` — fix one number, wheel the rest. Cheap, popular.
- **C** — **Strongest single OSS magnet in the article.** Smart Luck
  charges $100+ for "Wheel Five Gold". An MIT-licensed Python
  implementation could go viral. Companion blog post: "What lottery
  wheel software actually does, and why we open-sourced it."

**Verdict: ✅ adopt — new module, prioritize.**

---

## 4. Most Probable Range of Sums (the 70% rule)

**Article claim.** ~70% of jackpots are produced by ~27–28% of all
possible sums. They publish lookup tables for many `(n,k)` formats.

- **A** — Genuinely true and derivable analytically. The sum of `k`
  draws-without-replacement from `{1..n}` has approximately a truncated
  normal distribution with mean `μ = k(n+1)/2` and variance
  `σ² = k(n+1)(n-k)/12`. The "70% range" is roughly `μ ± 1.04σ` (covers
  ~70% of probability mass under normal). For 6/49: μ=150, σ≈32.8 →
  range ≈ 116–184. Article's published range is 115–185. Match.
  → We can **compute the table from rules**, not hardcode it.
- **B** — Two changes:
  1. New `engine/modules/sum_range.py` exposing `most_probable_range(rules, coverage=0.70)`.
  2. Refactor `pattern.py` to use this module instead of empirical
     percentile sampling. Removes the `n_samples=5000` cost.
- **C** — Killer Nerd-mode visualization: bell curve overlaid with the
  user's chosen combo's sum, color-coded inside / outside the 70% band.

**Verdict: ✅ adopt + 🔧 refactor** existing pattern.py.

---

## 5. Avoid never-drawn / out-of-envelope combos (e.g. 1-2-3-4-5-6)

**Article claim.** Combos like `1-2-3-4-5-6` "never come up." Don't bet
them.

- **A** — Half-truth. ANY specific 6-tuple has the same P. What's true
  is that the *block* of all-consecutive combos occupies a vanishingly
  small slice of the sum/spread distribution, so the *category* is rare.
  But the real reason to avoid 1-2-3-4-5-6 is that ~10,000 *other people*
  bet it every NY drawing → guaranteed prize-sharing if it ever hit.
  This is an EV argument, not a P(win) argument.
- **B** — `pattern.py` already filters for consecutive-pair count
  percentiles. New surface: a `combo_audit(numbers)` function that
  returns `{ in_envelope: bool, sum_bucket, consecutive_pairs,
  popularity_score, ... }`.
- **C** — Combo Audit is a viral-shareable feature: "Paste your
  numbers — we score them." Works as a free hook for the paid tier.

**Verdict: ✅ adopt** as a new `combo_audit` API surface.

---

## 6. The "due numbers" fallacy (article contradicts itself)

**Article claim (paragraph 1).** Don't play "due" numbers — that's a
fallacy. **Article claim (paragraph 2).** But here's our overdue/skip-hit
analysis tool…

- **A** — The contradiction is real. Our `deviation.py` docstring
  already gets it right: *"in a truly fair lottery every draw is
  independent — overdue is a statistical observation, not a prediction
  guarantee."* Keep that disclaimer, surface it in the API + UI.
- **B** — `deviation.py` is fine. The fix is at the layer above —
  the API response should always include `is_predictive: bool` derived
  from the chi² gate from idea 2.
- **C** — This is **our integrity moat**. Smart Luck won't publish
  this caveat because it would undermine their sales. We will. That's
  defensible content.

**Verdict: 🧪 already covered** in code; promote disclaimer to API + UX.

---

## 7. Avoid calendar-only numbers (1–31)

**Article claim.** Most casual players bet birthdays → numbers 1–31 are
over-picked. If you avoid them, you share less when you win.

- **A** — True and important. There's published research on this
  (Cook & Clotfelter, "Selling Hope: State Lotteries"). It changes
  *expected payout*, not P(win). Real value, real math.
- **B** — New strategy: `engine/strategies/popularity.py` (or
  `anti_popular.py`). We don't have player-pick data, but we can use
  documented heuristics:
  - Calendar bias: weight numbers ≤31 as more popular
  - "Lucky" numbers: 7, 11, 13, 17, 21, 23, 33, 77, etc.
  - Diagonal-on-betslip patterns
  - Repeating digits / sequences (11, 22, 33; 7, 17, 27)
  - Round groupings (multiples of 5 or 10)
  Output: an **inverse-popularity score** per combo.
- **C** — Powerful product framing: "Don't try to win MORE — try to
  share LESS." Repositions lottery as *win-bigger* rather than
  *win-impossible*.

**Verdict: ✅ adopt — high-value new strategy.**

---

## 8. Play the higher half of the probable range

**Article claim.** Within the 70% sum range, prefer sums above the
midpoint — fewer players go there.

- **A** — Same insight as #7, packaged differently. Higher sums imply
  higher numbers, which are under-played by the calendar-biased crowd.
- **B** — Falls out naturally as a parameter of the popularity module.
  No new module.
- **C** — Combine with #7 into a single "Anti-Popular" UX feature.

**Verdict: 🔧 subsume** into the popularity module.

---

## 9. Bell-curve / sum-frequency visualization

**Article claim.** Show users a bell-curve of historical winning sums
to motivate the 70% rule.

- **A** — Standard histogram + analytical truncated-normal overlay.
  Easy and pedagogically valuable.
- **B** — FastAPI endpoint `/sum-distribution` returning the curve;
  Expo Nerd-mode chart consumes it.
- **C** — **Must-have** Nerd-mode flagship visual. Sells the
  credibility in 2 seconds.

**Verdict: ✅ adopt** — endpoint + chart.

---

## 10. Skip-and-Hit / gap analysis

**Article claim.** Number 45 in NY Lotto sat out 100 drawings.

- **A** — Gap distributions are already in `deviation.py` (`gap_stats`
  per number). The visualization is what's missing.
- **B** — Add `/gap-distribution/{number}` endpoint + Nerd-mode chart.
- **C** — Nerd-mode chart, low priority but easy.

**Verdict: 🧪 already in code;** add viz.

---

## 11. Handicapping framing (horse-racing / Wall Street technical analysis)

**Article claim.** "Handicapping a lotto is like reading stock charts."

- **A** — Pure marketing copy. No mathematical content.
- **B** — N/A.
- **C** — **Excellent content angle for Sprint 5.** Drafts:
  - "What a quant would do with lottery data (and why it mostly
    doesn't work)"
  - "Lottery handicapping vs technical analysis: same illusions,
    different prices"
  Top-of-funnel SEO magnet linked back to the OSS repo.

**Verdict: ✅ adopt** as content material, not code.
