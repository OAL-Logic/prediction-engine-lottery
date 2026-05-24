---
title: Most Probable Range of Sums — Reference Tables
sources: https://smartluck.com/bestsums.htm
project: Prediction Engine
date: 2026-04-25
note: |
  These ranges are NOT meant to be hardcoded — they should be computed
  analytically by `engine/modules/sum_range.py` from each adapter's
  DrawRules. We keep this table as a sanity-check fixture for unit tests.
---

# Most Probable Range of Sums — Reference Tables

For each `(pick_count, number_field)` combination, the table lists:
- **Midpoint** = `pick * (n+1) / 2` (mean of sum distribution)
- **70% range** = approximately `midpoint ± 1.04 · σ` where
  `σ² = pick * (n+1) * (n-pick) / 12`

These are the published Smart Luck values. Use them in tests as the
expected output of `most_probable_range(rules, coverage=0.70)`.

## Pick-4

| Field | Midpoint | 70% Range |
|------:|---------:|:----------|
| 4/24 | 50  | 36–64   |
| 4/33 | 68  | 49–87   |
| 4/35 | 72  | 51–93   |
| 4/44 | 90  | 64–116  |
| 4/45 | 92  | 65–119  |
| 4/49 | 100 | 71–129  |
| 4/50 | 102 | 72–132  |
| 4/60 | 122 | 95–184  |
| 4/77 | 156 | 110–202 |

## Pick-5

| Field | Midpoint | 70% Range |
|------:|---------:|:----------|
| 5/19 | 51  | 39–61   |
| 5/20 | 53  | 40–65   |
| 5/25 | 65  | 49–81   |
| 5/26 | 68  | 51–84   |
| 5/28 | 73  | 55–90   |
| 5/30 | 78  | 58–97   |
| 5/31 | 80  | 60–100  |
| 5/32 | 83  | 62–103  |
| 5/33 | 85  | 64–106  |
| 5/34 | 88  | 66–109  |
| 5/35 | 90  | 68–112  |
| 5/36 | 93  | 69–116  |
| 5/37 | 95  | 71–119  |
| 5/38 | 98  | 73–122  |
| 5/39 | 100 | 75–125  |
| 5/40 | 103 | 77–128  |
| 5/41 | 105 | 78–132  |
| 5/42 | 108 | 80–135  |
| 5/43 | 110 | 82–137  |
| 5/44 | 113 | 84–141  |
| 5/45 | 115 | 86–144  |
| 5/47 | 120 | 89–151  |
| 5/48 | 123 | 92–153  |
| 5/49 | 125 | 93–157  |
| 5/50 | 128 | 95–160  |
| 5/52 | 133 | 98–167  |
| 5/53 | 135 | 100–170 |
| 5/54 | 138 | 102–173 |
| 5/55 | 140 | 104–176 |
| 5/56 | 143 | 106–179 |
| 5/59 | 150 | 111–189 |
| 5/60 | 162 | 121–204 |
| 5/69 | 175 | 130–221 |
| 5/70 | 177 | 132–223 |
| 5/75 | 190 | 141–240 |
| 5/80 | 203 | 149–256 |
| 5/90 | 228 | 167–288 |

## Pick-6

| Field | Midpoint | 70% Range |
|------:|---------:|:----------|
| 6/25 | 78  | 61–95   |
| 6/30 | 93  | 73–113  |
| 6/32 | 99  | 77–121  |
| 6/33 | 102 | 79–125  |
| 6/34 | 105 | 82–128  |
| 6/35 | 108 | 84–132  |
| 6/36 | 111 | 86–136  |
| 6/37 | 114 | 88–140  |
| 6/38 | 117 | 91–143  |
| 6/39 | 120 | 93–147  |
| 6/40 | 123 | 95–151  |
| 6/41 | 126 | 97–155  |
| 6/42 | 129 | 100–158 |
| 6/43 | 132 | 102–162 |
| 6/44 | 135 | 104–166 |
| 6/45 | 138 | 106–170 |
| 6/46 | 141 | 109–173 |
| 6/47 | 144 | 111–177 |
| 6/48 | 147 | 113–181 |
| 6/49 | 150 | 115–185 |
| 6/50 | 153 | 118–188 |
| 6/51 | 156 | 120–192 |
| 6/52 | 159 | 122–196 |
| 6/53 | 162 | 124–200 |
| 6/54 | 165 | 127–203 |
| 6/55 | 168 | 129–207 |
| 6/56 | 171 | 131–211 |
| 6/58 | 177 | 136–218 |
| 6/59 | 180 | 138–222 |
| 6/60 | 183 | 140–226 |  ← **Mega-Sena**
| 6/63 | 186 | 147–237 |
| 6/69 | 210 | 161–259 |
| 6/90 | 273 | 208–338 |

## Pick-7

| Field | Midpoint | 70% Range |
|------:|---------:|:----------|
| 7/27 | 98  | 79–117  |
| 7/34 | 123 | 98–147  |
| 7/35 | 126 | 100–152 |
| 7/39 | 140 | 111–169 |
| 7/45 | 161 | 127–195 |
| 7/47 | 168 | 133–203 |
| 7/77 | 210 | 161–259 |

## Pick-12

| Field | Midpoint | 70% Range |
|------:|---------:|:----------|
| 12/24 | 150 | 131–169 |

## Notes for the adapters we ship today

- **Mega-Sena (6/60)**: midpoint 183, 70% range 140–226.
- **Lotofácil (15/25)**: not in their tables — derive analytically:
  μ = 15·26/2 = 195. σ² = 15·26·10/12 = 325 → σ ≈ 18.0 →
  70% range ≈ 176–214.
- **Powerball (5/69 main)**: 175, 130–221 (matches their published 5/69).

## Sanity-check Python

```python
import math

def midpoint(pick: int, n: int) -> float:
    return pick * (n + 1) / 2

def sigma(pick: int, n: int) -> float:
    return math.sqrt(pick * (n + 1) * (n - pick) / 12)

def range_70(pick: int, n: int) -> tuple[int, int]:
    mu = midpoint(pick, n)
    s = sigma(pick, n)
    # ~70% under standard normal is mu ± 1.036 sigma
    return round(mu - 1.04 * s), round(mu + 1.04 * s)

# Mega-Sena 6/60
print(midpoint(6, 60), range_70(6, 60))
# → 183.0 (~140, ~226)
```
