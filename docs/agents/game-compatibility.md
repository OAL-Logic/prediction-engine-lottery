# Global Game Compatibility & Architecture Isolation Guide

This document defines the engineering standards and patterns required to keep the Lottery Prediction Engine globally compatible across international lotteries while isolating jurisdiction- and game-specific rules (such as Brazilian Caixa Loterias, US MUSL, European multi-jurisdiction lotteries, etc.).

---

## 1. Core Motivation

The initial feature set of this engine was developed primarily using Brazilian Caixa Econômica Federal games (`br/mega-sena`, `br/lotofacil`, `br/quina`, etc.). However:
1. **Intra-jurisdiction diversity**: Even within Brazil, game rules vary radically:
   - `Lotomania`: 50 numbers selected from a 100-number pool indexed `00` to `99`, where 20 numbers are drawn, mirror bets exist, and ticket formatting requires leading zeros.
   - `Lotofácil`: 15 numbers selected from 25 ($60\%$ pool density), fundamentally altering combinatorial clustering, gap intervals, and filter dynamics.
   - `Dupla Sena`: Two distinct drawings per contest from the same ticket selection.
   - `Dia de Sorte`: 7 numbers from 31 plus an independent categorical attribute ("Mês da Sorte", 1–12).
   - `+Milionária`: 6 numbers from 50 plus 2 clover/bonus numbers from 6.
2. **Global jurisdiction expansion**: Games worldwide introduce further variations:
   - US Powerball & Mega Millions: Main ball pool + independent single bonus ball.
   - EuroMillions & EuroJackpot: Main ball pool + two star numbers.
   - Daily 3 / Pick 4 / Daily Keno: Position-dependent numbers or variable ticket lengths.

**Core Directive**: Core algorithms (filters, generators, analyzers, visualizers, wheels, and backtesters) must NEVER make hardcoded assumptions about any single game's matrix, pricing, or indexing. All specific rules must be isolated and pluggable.

---

## 2. Architectural Design Patterns

### Pattern 1: Abstract Contract & Rules Parameterization
Every core feature receives rules from the domain contract (`DrawRules` or `GameDefinition`):

```python
# ❌ Anti-pattern: Hardcoded assumptions
def filter_high_low(ticket: list[int]) -> bool:
    high_count = sum(1 for n in ticket if n > 30)  # Assumes Mega-Sena 1-60!
    return 2 <= high_count <= 4

# ✅ Recommended pattern: Derived from DrawRules
def filter_high_low(ticket: list[int], rules: DrawRules) -> bool:
    lo, hi = rules.number_range
    midpoint = lo + (hi - lo + 1) // 2
    high_count = sum(1 for n in ticket if n >= midpoint)
    k = len(ticket)
    # Scaled envelope based on ticket size
    return max(1, int(0.3 * k)) <= high_count <= min(k - 1, int(0.7 * k))
```

### Pattern 2: Pluggable Rule Overrides (Hook Pattern)
When a specific lottery needs a custom implementation or workaround for a feature (e.g., custom filter boundaries, distinct distance metrics, or special ticket representation):

1. **Check for game-specific hook**:
   ```python
   def evaluate_feature(ticket: list[int], rules: DrawRules) -> FeatureResult:
       # 1. Look for game or jurisdiction override
       override_fn = get_game_feature_override(rules.name, "my_feature")
       if override_fn is not None:
           return override_fn(ticket, rules)
       
       # 2. Universal mathematical default
       return default_universal_evaluation(ticket, rules)
   ```
2. **Encapsulate game overrides in adapter/game modules**:
   Store game-specific overrides alongside the game's adapter or within a modular feature plugin, never as scattered `if rules.name == "Lotofácil"` blocks throughout the core engine.

### Pattern 3: Decoupled Multi-Pool & Bonus Ball Handling
Composite tickets consisting of primary numbers and bonus/extra balls must be cleanly separated:
- Main ball operations (entropy, parity, consecutive differences, covering wheels) execute on `ticket.numbers`.
- Bonus ball operations execute on `ticket.bonus` with its own distinct `rules.bonus_range` and `rules.bonus_count`.
- Composite validators verify both partitions independently.

---

## 3. Directory Layout Standard

```text
engine/
├── adapters/
│   ├── <country_code>/               # Regional directory (e.g., br/, us/, eu/, jp/)
│   │   ├── __init__.py
│   │   ├── <jurisdiction>_base.py    # Common networking, auth, parser, syndicate logic
│   │   ├── <game_slug>.py            # Concrete LotteryAdapter subclass
│   │   └── rules/                    # Game-specific rule handlers & custom overrides
│   ├── registry.py                   # Central GameDefinition loader from data/registry.yaml
│   └── __init__.py                   # Core Draw, DrawRules, LotteryAdapter definitions
├── modules/
│   ├── filters/                      # Universal vectorized filters (parameterized by DrawRules)
│   ├── wheels/                       # Universal covering algorithms & wheel reducers
│   └── ...
└── strategies/                       # Universal statistical, ML, and heuristic models
```

---

## 4. Developer & Agent Quality Gate

When adding or modifying any feature:
1. **Matrix Agnostic**: Verify that changing `(pick_count, pool_size, number_range_min)` does not break the feature.
2. **Zero-Index Verification**: Ensure tests pass with both 1-indexed pools (e.g. 1..60) and 0-indexed pools (e.g. 0..99).
3. **Multi-Bet Verification**: Ensure the feature handles multiple bet sizes ($k \le n \le \text{max\_picks}$) or cleanly validates ticket cardinality.
4. **Tri-Archetype Verification**: Run tests against at least 3 distinct games:
   - `br/mega-sena` (sparse 6/60)
   - `br/lotofacil` (dense 15/25)
   - `us/powerball` (bonus ball 5/69 + 1/26)
