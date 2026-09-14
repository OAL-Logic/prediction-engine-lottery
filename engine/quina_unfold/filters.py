"""
FilterPipeline — configurable rule engine applying structural rejection
thresholds to a candidate N-number pool.
==========================================================================
Every rule is a pure function of (pool, feature_table, rules) -> (passed, detail).
Thresholds are explicit, overridable constructor args — nothing is hard-coded
inside a rule body, so the same pipeline can be re-tuned per game/season
without touching this file.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable, Dict, List, Sequence, Tuple

import pandas as pd

from engine.adapters import DrawRules
from engine.modules import sum_range as sum_range_module

Predicate = Callable[[Sequence[int], pd.DataFrame, DrawRules], Tuple[bool, str]]


@dataclass
class FilterRule:
    name: str
    description: str
    predicate: Predicate


@dataclass
class FilterReport:
    passed: bool
    details: Dict[str, str] = field(default_factory=dict)
    failures: List[str] = field(default_factory=list)


class FilterPipeline:
    """Ordered collection of FilterRules, evaluated against a candidate pool."""

    def __init__(self):
        self.rules: List[FilterRule] = []

    def add_rule(self, rule: FilterRule) -> "FilterPipeline":
        self.rules.append(rule)
        return self

    def evaluate(self, pool: Sequence[int], features: pd.DataFrame, rules: DrawRules) -> FilterReport:
        details: Dict[str, str] = {}
        failures: List[str] = []
        for rule in self.rules:
            ok, detail = rule.predicate(pool, features, rules)
            details[rule.name] = detail
            if not ok:
                failures.append(rule.name)
        return FilterReport(passed=(len(failures) == 0), details=details, failures=failures)

    # ------------------------------------------------------------------
    # Default envelope — the boundary filters described in the brief
    # ------------------------------------------------------------------

    @classmethod
    def default_envelope(
        cls,
        parity_band: Tuple[float, float] = (0.40, 0.60),
        sum_coverage: float = 0.70,
        max_per_decile_slack: int = 1,
        max_per_quadrant_slack: int = 2,
        max_repeat_fraction: float = 0.40,
        max_adjacent_fraction: float = 0.30,
        min_hot_or_overdue_fraction: float = 0.30,
    ) -> "FilterPipeline":
        """
        Build the standard macro-structural envelope:
          - Parity  : odd fraction inside [parity_band]      (2:5-3:5 generalized)
          - Sum     : within the `sum_coverage` analytical band, scaled to N
          - Decile  : no decile holds more than a proportionate share + slack
          - Quadrant: no quadrant holds more than a proportionate share + slack
          - Repeats : fraction of pool repeating the prior draw <= max_repeat_fraction
          - Adjacency: fraction of pool adjacent (+/-1) to the prior draw <= max_adjacent_fraction
          - Cycle mix: at least min_hot_or_overdue_fraction of the pool is hot/overdue
                       (i.e. the pool isn't 100% "warm"/inert numbers)
        """
        pipeline = cls()

        def parity_rule(pool, features, rules):
            odd = sum(1 for n in pool if n % 2 == 1)
            frac = odd / len(pool)
            lo, hi = parity_band
            ok = lo <= frac <= hi
            return ok, f"odd_fraction={frac:.2f} (target {lo:.2f}-{hi:.2f}), odd={odd}/{len(pool)}"

        pipeline.add_rule(FilterRule("parity_balance", "Odd/even ratio within band", parity_rule))

        def sum_rule(pool, features, rules):
            scaled = replace(rules, pick_count=len(pool))
            lo_sum, hi_sum, mean, sigma = sum_range_module.most_probable_range(scaled, coverage=sum_coverage)
            s = sum(pool)
            ok = lo_sum <= s <= hi_sum
            return ok, f"sum={s} (band {lo_sum}-{hi_sum}, mean={mean:.0f}, sigma={sigma:.1f})"

        pipeline.add_rule(FilterRule("sum_band", f"Sum within {sum_coverage:.0%} analytical band, scaled to N", sum_rule))

        def decile_rule(pool, features, rules):
            deciles = features.loc[list(pool), "decile"]
            counts = deciles.value_counts()
            n_deciles = 10
            expected = max(1, round(len(pool) / n_deciles))
            cap = expected + max_per_decile_slack
            worst = int(counts.max()) if not counts.empty else 0
            occupied = counts.shape[0]
            ok = worst <= cap
            return ok, f"max_per_decile={worst} (cap {cap}), deciles_occupied={occupied}/10"

        pipeline.add_rule(FilterRule("decile_spread", "No decile over-concentrated", decile_rule))

        def quadrant_rule(pool, features, rules):
            quads = features.loc[list(pool), "quadrant"]
            counts = quads.value_counts()
            n_quadrants = 4
            expected = max(1, round(len(pool) / n_quadrants))
            cap = expected + max_per_quadrant_slack
            worst = int(counts.max()) if not counts.empty else 0
            occupied = counts.shape[0]
            ok = worst <= cap and occupied == n_quadrants
            return ok, f"max_per_quadrant={worst} (cap {cap}), quadrants_occupied={occupied}/4"

        pipeline.add_rule(FilterRule("quadrant_spread", "All 4 quadrants represented, none over-concentrated", quadrant_rule))

        def repeat_rule(pool, features, rules):
            repeats = int(features.loc[list(pool), "is_repeat_of_prior"].sum())
            frac = repeats / len(pool)
            ok = frac <= max_repeat_fraction
            return ok, f"prior_repeats={repeats}/{len(pool)} ({frac:.2f}, cap {max_repeat_fraction:.2f})"

        pipeline.add_rule(FilterRule("prior_repeat_rate", "Repeat rate vs. immediate prior draw bounded", repeat_rule))

        def adjacency_rule(pool, features, rules):
            adj = int(features.loc[list(pool), "is_adjacent_to_prior"].sum())
            frac = adj / len(pool)
            ok = frac <= max_adjacent_fraction
            return ok, f"prior_adjacent={adj}/{len(pool)} ({frac:.2f}, cap {max_adjacent_fraction:.2f})"

        pipeline.add_rule(FilterRule("prior_adjacency", "Adjacency to prior draw bounded", adjacency_rule))

        def cycle_mix_rule(pool, features, rules):
            classes = features.loc[list(pool), "cycle_class"]
            hot_overdue = int(classes.isin(["hot", "overdue"]).sum())
            frac = hot_overdue / len(pool)
            ok = frac >= min_hot_or_overdue_fraction
            return ok, f"hot_or_overdue={hot_overdue}/{len(pool)} ({frac:.2f}, floor {min_hot_or_overdue_fraction:.2f})"

        pipeline.add_rule(FilterRule("cycle_mix", "Pool includes a minimum share of hot/overdue numbers", cycle_mix_rule))

        return pipeline
