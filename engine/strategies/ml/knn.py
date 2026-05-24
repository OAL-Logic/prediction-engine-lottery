"""
K-Nearest Neighbours Strategy  🔍
===================================
"What moment in draw history looks most like right now —
 and what came after it?"

Unlike all other ML strategies (which train a classifier), KNN asks a
direct analogical question: find the K historical draws that most closely
resemble the current state, look at what numbers were drawn in the *next*
draw after each of those moments, and score numbers proportionally to how
often they appeared in those successor draws — weighted by closeness.

This is the most interpretable ML strategy in the engine: the evidence
is literally "these past moments looked like today, and these numbers
followed them."

Feature vector per draw moment
-------------------------------
For draw at position t, the feature vector is:

  [gap_norm(n1), gap_norm(n2), ..., gap_norm(nK)]   # gap since each number's last appearance
  [freq_norm(n1), ..., freq_norm(nK)]                # recent frequency of each number
  day_of_week / 6.0
  draw_index_norm                                    # how far into the history we are

Where gap_norm(n) = draws_since_last(n) / pool_size
      freq_norm(n) = appearances_in_last_20 / 20

KNN distance: Euclidean (L2) in this feature space.
Scoring: score(n) = Σ (1/dist_k) × appears_in_successor(n, k) / Σ (1/dist_k)

Metadata
--------
The strategy stores the K nearest historical draw dates and their numbers
in result.metadata so the CLI can display them as evidence.

Requires: sklearn (pip install "lottery-engine[ml]")
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

try:
    from sklearn.neighbors import NearestNeighbors
    _SKLEARN = True
except ImportError:
    _SKLEARN = False


@register
class KNNStrategy(BaseStrategy):
    name        = "knn"
    description = "🔍 K-Nearest Neighbours — find moments in history that look like today"
    tier        = "ml"
    requires_history = 60

    def __init__(
        self,
        k:           int = 10,
        freq_window: int = 20,
    ) -> None:
        """
        Parameters
        ----------
        k           Number of nearest historical moments to use.
        freq_window Recent-window size for frequency features.
        """
        self.k           = k
        self.freq_window = freq_window
        self._neighbours: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Feature builder
    # ------------------------------------------------------------------

    def _draw_vector(
        self,
        t: int,
        df: pd.DataFrame,
        all_numbers: list[int],
        pool: int,
    ) -> np.ndarray:
        """Build the feature vector for draw position t."""
        n = len(df)
        fw = min(self.freq_window, t)

        gap_feats  = []
        freq_feats = []
        for num in all_numbers:
            # Gap: how many draws since num last appeared before draw t?
            last = next(
                (t - 1 - i for i in range(t) if num in df.iloc[t - 1 - i]["numbers"]),
                t,
            )
            gap_feats.append(last / max(pool, 1))

            # Frequency in recent window
            window_df = df.iloc[max(0, t - fw): t]
            cnt = sum(1 for _, row in window_df.iterrows() if num in row["numbers"])
            freq_feats.append(cnt / max(fw, 1))

        try:
            dow = df.iloc[t]["date"].dayofweek / 6.0
        except Exception:
            dow = 0.5

        draw_idx_norm = t / max(n - 1, 1)

        return np.array(gap_feats + freq_feats + [dow, draw_idx_norm], dtype=np.float32)

    # ------------------------------------------------------------------
    # score()
    # ------------------------------------------------------------------

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        if not _SKLEARN:
            raise ImportError("pip install 'lottery-engine[ml]'")

        df = df.sort_values("draw_id").reset_index(drop=True)
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        n    = len(df)

        min_t = max(self.freq_window + 1, 5)
        if n < min_t + 2:
            return {num: 1.0 / pool for num in all_numbers}

        # Build feature matrix for all historical positions (each has a known successor)
        indices: list[int] = []
        vectors: list[np.ndarray] = []
        for t in range(min_t, n - 1):
            indices.append(t)
            vectors.append(self._draw_vector(t, df, all_numbers, pool))

        X_hist = np.array(vectors, dtype=np.float32)

        # Current moment vector (position = n-1, no known successor)
        x_now  = self._draw_vector(n - 1, df, all_numbers, pool).reshape(1, -1)

        # Fit KNN and find neighbours of the current moment
        k_actual = min(self.k, len(indices))
        nbrs = NearestNeighbors(n_neighbors=k_actual, metric="euclidean")
        nbrs.fit(X_hist)
        distances, neighbour_idxs = nbrs.kneighbors(x_now)
        distances     = distances[0]
        neighbour_idxs = neighbour_idxs[0]

        # Avoid division by zero for perfect matches
        distances = np.where(distances == 0, 1e-9, distances)
        weights   = 1.0 / distances
        weights  /= weights.sum()

        # Score numbers by weighted frequency in successor draws
        scores: dict[int, float] = defaultdict(float)
        self._neighbours = []

        for w, hist_idx in zip(weights, neighbour_idxs):
            t_hist     = indices[hist_idx]
            successor  = df.iloc[t_hist + 1]
            succ_nums  = set(successor["numbers"])

            try:
                draw_date = df.iloc[t_hist]["date"]
                date_str  = draw_date.date().isoformat() if hasattr(draw_date, "date") else str(draw_date)[:10]
            except Exception:
                date_str = "?"

            self._neighbours.append({
                "date":     date_str,
                "numbers":  sorted(df.iloc[t_hist]["numbers"]),
                "followed_by": sorted(successor["numbers"]),
                "distance": round(float(1.0 / w), 4),
            })

            for num in all_numbers:
                if num in succ_nums:
                    scores[num] += float(w)

        max_v = max(scores.values()) if scores else 1.0
        if max_v == 0:
            return {num: 1.0 / pool for num in all_numbers}

        return {num: scores.get(num, 0.0) / max_v for num in all_numbers}

    # ------------------------------------------------------------------
    # suggest() — inject neighbour evidence into metadata
    # ------------------------------------------------------------------

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata["nearest_neighbours"] = self._neighbours
        result.metadata["k"] = self.k
        return result
