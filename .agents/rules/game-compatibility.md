# Global Game Compatibility & Jurisdiction Isolation Rule

Every feature developed in this repository (predictive models, combinatorial filters, ticket generators, statistical analyzers, backtesters, CLI commands, wheeling algorithms, UI views, and data pipelines) MUST maintain architectural compatibility with diverse lottery formats worldwide.

While Brazilian Caixa Loterias serves as the primary reference implementation, the codebase must never be tightly coupled to Caixa specifics. Features must be structured to allow localized variations, game-specific rules, parameters, and workarounds across different jurisdictions.

---

## 1. Zero Hardcoding Policy (Universal Core)

Core logic in `engine/` (`modules/`, `strategies/`, `wheels/`, `cli/`, `desktop/`) MUST NOT hardcode game-specific parameters:
1. **Never hardcode pool size $N$ or pick count $k$**:
   - ❌ FORBIDDEN: `if ball > 60:`, `range(1, 61)`, `k = 6`, `sum_range = (150, 220)`.
   - ✅ REQUIRED: Derive dynamically from `rules.number_range`, `rules.pick_count`, or hypergeometric formulas $\mathbb{E}[\text{Sum}] = \frac{k(N+1)}{2}$.
2. **Never assume 1-based ball indexing**:
   - ❌ FORBIDDEN: `for i in range(1, pool_size + 1):`
   - ✅ REQUIRED: Use `rules.number_range` (e.g. `(rules.number_range[0], rules.number_range[1])`), accommodating zero-indexed lotteries (e.g., Lotomania `00-99`).
3. **Never assume single-pool mechanics**:
   - ❌ FORBIDDEN: Discarding or ignoring bonus balls when validating or predicting.
   - ✅ REQUIRED: Check `rules.bonus_count > 0` and process bonus pools (e.g. US Powerball 1-26, EuroMillions 1-12, +Milionária 1-6) through secondary generators/filters.
4. **Never hardcode currency or pricing structures**:
   - ❌ FORBIDDEN: Hardcoding `R$ 5,00`, `float(count) * 5.0`.
   - ✅ REQUIRED: Query `rules.currency`, `rules.ticket_price`, and `rules.calculate_bet_cost(n_picked)`.

---

## 2. Global Lottery Archetypes Matrix

Every feature must be designed with the following lottery archetypes in mind:

| Archetype | Examples | Distinguishing Properties & Required Feature Behavior |
| :--- | :--- | :--- |
| **Standard Single-Pool Matrix** | Mega-Sena (6/60), Quina (5/80), UK Lotto (6/59), Canada 6/49 (6/49) | Classic $k$ from $N$. Sparse distribution ($k \ll N$). Standard combinatorial metrics apply. |
| **Multi-Pool / Bonus Ball Matrix** | US Powerball (5/69 + 1/26), Mega Millions (5/70 + 1/25), EuroMillions (5/50 + 2/12), +Milionária (6/50 + 2/6) | Two independent or semi-independent draws. Features must handle composite tickets `(numbers, bonus)`. |
| **High-Density Single-Pool Matrix** | Lotofácil (15/25), Keno (10-20/80) | Pick density $> 50\%$. Consecutive sequences, high overlap, and complement spaces dominate. Standard low-density filters must adjust thresholds dynamically. |
| **Zero-Indexed / Centesimal Pools** | Lotomania (50/100, balls `00-99`) | Mirror bets ($100 - x$), zero indexation, 20 drawn balls vs 50 picked balls. String formatting must support two-digit `"00"`. |
| **Multi-Draw per Contest** | Dupla Sena (Draw 1 & Draw 2 per concurso) | Historical feeds contain 2 distinct series per draw ID. Features must allow targeting Draw 1, Draw 2, or both. |
| **Categorical / Calendar Attributes** | Dia de Sorte (7/31 + Month of Luck 1-12) | Special secondary attribute with non-numerical semantics (calendar months, astrological signs). Must not contaminate numerical integer arrays. |
| **Variable Multiple / System Bets** | Mega-Sena (6..20 picks), Lotofácil (15..20 picks) | Single tickets containing $M > k$ numbers. Features must respect `rules.allowed_picks` and calculate combinatorial expansion $\binom{M}{k}$. |

---

## 3. Directory & File Organization for Pluggable Rules

To allow game-specific and jurisdiction-specific rules without polluting generic core logic, organize files as follows:

```text
engine/
├── adapters/
│   ├── <country_code>/               # e.g. br/, us/, eu/, uk/, jp/
│   │   ├── <jurisdiction>_base.py    # Common API, rate-limits, syndicate (bolão) rules (e.g. caixa_base.py)
│   │   ├── <game_slug>.py            # Game-specific rules, payout tiers, idiosyncrasies
│   │   └── rules/                    # Optional: game-specific rule overrides & handlers
│   └── registry.py                   # Central GameDefinition loader from data/registry.yaml
├── modules/
│   ├── filters/                      # Universal vectorized filters (parameterized by DrawRules)
│   ├── wheels/                       # Universal covering & wheel algorithms
│   └── overrides/                    # Feature hooks & overrides indexed by game/jurisdiction
└── strategies/                       # Universal statistical, ML, and esoteric predictors
```

### Rule Extension Pattern: Strategy & Hook Decoupling
When a game requires specific custom logic, workaround, or tailored parameters for a feature:
1. **Feature Parameter Protocol**: The core feature defines default parameters derived dynamically from `DrawRules`.
2. **Game Hook / Override Registry**: The feature checks if the active game registers a custom hook or parameter override (e.g., via `rules.custom_attributes`, a game-specific rule adapter, or a hook registry).
3. **Graceful Fallback**: If no specific override exists, the feature MUST execute its standard generalized mathematical algorithm without raising errors.

---

## 4. Feature Implementation Checklist

Before completing any new feature, command, filter, or strategy, verify:
- [ ] **No Hardcoded Numbers**: No pool sizes, ball counts, or hardcoded ranges exist in core logic.
- [ ] **Zero-Index Safe**: Feature does not assume `1` is the minimum ball; uses `rules.number_range[0]`.
- [ ] **Bonus Ball Tolerant**: If the game defines `bonus_count > 0`, the feature handles bonus numbers or cleanly isolates main numbers.
- [ ] **Dynamic Thresholds**: Filters and thresholds scale proportionally with $(N, k)$ using analytical or normalized scales.
- [ ] **Multiple Bets Supported**: If ticket size $n > k$, the feature either supports multiple bets via `rules.allowed_picks` or explicitly validates ticket length.
- [ ] **Cross-Game Tested**: Tested or verified against at least 3 distinct game archetypes:
  - Standard sparse single-pool (e.g. `br/mega-sena` 6/60 or `br/quina` 5/80)
  - High-density single-pool (e.g. `br/lotofacil` 15/25)
  - Bonus ball / multi-pool (e.g. `us/powerball` 5/69+1/26 or `br/mais-milionaria` 6/50+2/6)
