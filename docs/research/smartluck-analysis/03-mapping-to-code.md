---
title: Mapping Article Ideas to Current Codebase
project: Prediction Engine
date: 2026-04-25
---

# Mapping — Article Ideas vs `lottery-engine/`

Status legend:
- 🟢 Already implemented
- 🟡 Partially implemented (refactor needed)
- 🔴 Not implemented (new module)
- ⚪ Out of scope for code (content / UX only)

| # | Idea | Status | Where it lives / would live |
|---|------|--------|------------------------------|
| 1 | Game selection / odds compare | 🔴 | new `engine/odds/comparator.py` |
| 2 | Handicapping (hot/cold) | 🟢 | `engine/modules/frequency.py` (chi² already) |
| 2b | Chi² gate at API/UX layer | 🔴 | `engine/api/main.py` + Expo app |
| 3 | Balanced wheels | 🔴 | new `engine/wheels/{full,abbreviated,key}.py` |
| 4 | Most Probable Range of Sums | 🟡 | new `engine/modules/sum_range.py`; refactor `pattern.py` |
| 5 | Avoid never-drawn / out-of-envelope | 🟡 | exists in `pattern.py` consecutive metric; needs `combo_audit` API |
| 6 | "Due numbers" disclaimer | 🟢 | `engine/modules/deviation.py` (correct copy already) |
| 6b | Surface disclaimer in API | 🔴 | API layer + UI strings |
| 7 | Anti-popular (avoid 1–31) | 🔴 | new `engine/strategies/popularity.py` |
| 8 | Higher half of sum range | 🟡 | parameterize popularity module |
| 9 | Bell-curve viz | 🔴 | FastAPI `/sum-distribution` + Expo chart |
| 10 | Skip-and-Hit viz | 🟡 | data exists in `deviation.py`; viz missing |
| 11 | Handicapping content angle | ⚪ | Sprint 5 blog drafts |

## Refactor opportunities surfaced

### `strategies/statistical/pattern.py`

Today it samples 5,000 random combos and measures fit empirically.
After we add `sum_range.py`, this module can:

1. Use `sum_range.most_probable_range(rules)` directly instead of
   `np.percentile` over a sampled `sums` array.
2. Compute the analytical odd/even and high/low envelopes too
   (binomial-like distributions, no sampling needed).
3. Drop `n_samples` parameter entirely → faster + deterministic.

### `engine/modules/deviation.py`

Already says the right thing. Just expose `is_predictive` (= chi² p<0.05
from frequency analysis) on its result objects so the API layer can
honor it.

### `engine/api/main.py` (FastAPI sidecar)

Once `sum_range`, `wheels`, `popularity` and `combo_audit` exist,
recommended endpoint surface:

```
GET  /games                        → list adapters
GET  /games/{slug}/odds            → C(n,k), bonus odds, EV summary
GET  /games/compare                → odds comparator for ranking
GET  /games/{slug}/sum-distribution
GET  /games/{slug}/gap/{number}
POST /games/{slug}/combo/audit     → body: { numbers }, returns full audit
POST /games/{slug}/wheel           → body: { numbers, kind, guarantee }
POST /games/{slug}/strategy/{name} → run a strategy, return scored numbers
```

## What stays exactly as-is

- All adapters (`engine/adapters/*`) — design is correct.
- `correlation.py` — orthogonal to article ideas, no change.
- ML/deep strategies — orthogonal, separate research track.
