"""
TabFM (Tabular Foundation Model) Strategy 📊
===============================================
Zero-shot / in-context tabular classification over engineered per-number
draw features, via Prior Labs' TabPFN — the real, installable package this
project's TODO.md's "TabFM" integration plan actually described (Google has
no public standalone "TabFM"; TabPFN is the tabular foundation model that
plan's "(like TabPFN/TabFM)" aside pointed at). This is the TabFM half
`timesfm_forecast.py`'s docstring flagged as "a natural follow-on in the
same tier, not implemented [t]here."

Unlike `timesfm` (one univariate series per number), this strategy builds
ONE tabular in-context dataset shared across all numbers: each row is
(number, historical draw) with structural features — gap since last hit,
rolling hit frequency, historical mean gap, parity, pool position — and a
0/1 "did it hit" label. TabPFN is given that table as in-context examples
and classifies one query row per number (built from state as of the most
recent draw) as hit/no-hit; `score()` uses the hit-class probability.

Deliberately dropped vs. TODO.md's original feature list: moon phase /
solar flux / pair-synergy. Those need the weather/solar caches (network) or
a second pass over co-occurrence; keeping this strategy to purely-historical
features keeps it deterministic, offline, and fast to test — closer in
spirit to `hurst_memory`/`kolmogorov_order` than to the `fun` tier's
environmental strategies.

Optional dependency: `pip install 'lottery-engine[foundation]'` (installs
`tabpfn`, which pulls in `torch`). Context is deliberately kept small
(default: last 20 draws x pool size rows) — TabPFN's own docs recommend
CPU-only runs stay under ~1000 rows, and most users of this tier won't have
a GPU. Override via the strategy's `context_draws` kwarg.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

_MODEL_CACHE = None  # process-local singleton; avoids reloading weights per call


def _load_model():
    """Deferred: only imports/loads TabPFN when this strategy actually runs,
    never at module import time."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    from tabpfn import TabPFNClassifier

    _MODEL_CACHE = TabPFNClassifier()
    return _MODEL_CACHE


def _number_features(n: int, lo: int, hi: int, gap: int, rolling_freq: int, mean_gap: float) -> list[float]:
    """Structural feature vector for number `n` as of some point in history."""
    pool_width = hi - lo
    return [
        float(gap),
        float(rolling_freq),
        float(mean_gap),
        float(n % 2),
        float(n - lo) / pool_width if pool_width > 0 else 0.0,
    ]


def _build_table(
    df: pd.DataFrame,
    pool: list[int],
    lo: int,
    hi: int,
    context_draws: int,
    rolling_window: int = 10,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build (X_context, y_context, X_query) for TabPFN.

    X_context/y_context: one row per (number, draw) over the last
    `context_draws` draws. Every row's features are computed from state as
    of strictly-before that row's own draw, so there's no label leakage.
    X_query: one row per number, built from state as of the *last* draw in
    `df` — this is what gets classified as "will hit the next draw."
    """
    n_draws = len(df)
    draw_sets = [set(row) for row in df["numbers"]]

    last_seen: dict[int, int] = {n: -1 for n in pool}  # index of last hit; -1 = never
    hit_counts: dict[int, int] = {n: 0 for n in pool}  # total hits so far

    def _state_features(n: int, t: int) -> list[float]:
        gap = t - last_seen[n]  # last_seen == -1 naturally yields t + 1 ("never seen")
        window_start = max(0, t - rolling_window)
        rolling_freq = sum(1 for w in range(window_start, t) if n in draw_sets[w])
        mean_gap = (t / hit_counts[n]) if hit_counts[n] > 0 else float(t + 1)
        return _number_features(n, lo, hi, gap, rolling_freq, mean_gap)

    start = max(0, n_draws - context_draws)
    X_context: list[list[float]] = []
    y_context: list[int] = []

    for t in range(n_draws):
        if t >= start:
            hit_set = draw_sets[t]
            for n in pool:
                X_context.append(_state_features(n, t))
                y_context.append(1 if n in hit_set else 0)
        # Update running state AFTER recording this draw's features (no leakage).
        for n in draw_sets[t]:
            if n in last_seen:
                last_seen[n] = t
                hit_counts[n] += 1

    X_query = [_state_features(n, n_draws) for n in pool]
    return np.array(X_context, dtype=float), np.array(y_context, dtype=int), np.array(X_query, dtype=float)


@register
class TabFMStrategy(BaseStrategy):
    name = "tabfm"
    description = "📊 TabFM — zero-shot tabular foundation-model (TabPFN) classification over per-number draw features"
    tier = "foundation"
    requires_history = 40  # needs enough draws for a meaningful rolling window + context

    def score(self, df: pd.DataFrame, rules: DrawRules, context_draws: int = 20, **kwargs) -> dict[int, float]:
        try:
            import tabpfn  # noqa: F401 — presence check; _load_model() does the real work
        except ImportError:
            raise ImportError("pip install 'lottery-engine[foundation]'")

        lo, hi = rules.number_range
        pool = list(range(lo, hi + 1))

        df = df.sort_values("draw_id").reset_index(drop=True)
        X_context, y_context, X_query = _build_table(df, pool, lo, hi, context_draws)

        if len(set(y_context.tolist())) < 2:
            # Degenerate context (pathologically short history) — nothing to
            # learn from; fall back to uniform rather than let TabPFN error.
            return {n: 1.0 / len(pool) for n in pool}

        model = _load_model()
        model.fit(X_context, y_context)
        proba = model.predict_proba(X_query)
        hit_col = list(model.classes_).index(1)
        raw = np.clip(proba[:, hit_col], 0.0, None)

        total = float(raw.sum())
        if total <= 0:
            return {n: 1.0 / len(pool) for n in pool}
        return {n: float(raw[i] / total) for i, n in enumerate(pool)}
