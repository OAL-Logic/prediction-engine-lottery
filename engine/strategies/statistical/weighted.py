"""
Weighted Statistical Strategy
==============================
Blends three historical signals into a single per-number score:

  frequency_score   How often has this number appeared?          (higher = hotter)
  gap_score         How overdue is this number?                  (higher = more overdue)
  position_score    Does this number tend to appear in a         (slot-based tendency)
                    specific sorted position? Useful for
                    lotteries where draw order matters.

Weights are configurable. Defaults give equal weight to all three.

This is the "Nerd mode" heuristic, promoted to a proper strategy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class WeightedStrategy(BaseStrategy):
    name = "weighted"
    description = "⚖️ Weighted blend of frequency, gap recency, and positional tendency"
    tier = "statistical"

    requires_history = 30

    def __init__(
        self,
        w_frequency: float = 1.0,
        w_gap:       float = 1.0,
        w_position:  float = 0.5,
    ) -> None:
        """
        Parameters
        ----------
        w_frequency
            Hot number weight. How much to reward numbers that appear often. 
            Higher = favor "lucky" numbers that keep showing up.
        w_gap
            Overdue number weight. How much to reward numbers that haven't appeared in a long time. 
            Higher = favor "cold" numbers due for a return.
        w_position
            Slot consistency weight. Rewards numbers that consistently land in the same 
            sorted position (e.g. always appearing as the first or last ball).
        """
        self.w_frequency = float(w_frequency)
        self.w_gap       = float(w_gap)
        self.w_position  = float(w_position)

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.arange(lo, hi + 1)
        n_draws = len(df)
        pick = rules.pick_count

        # Convert numbers to a matrix (D x P)
        draws_matrix = np.array([sorted(row) for row in df["numbers"]])

        # 1. Frequency Score (Vectorized)
        unique, counts = np.unique(draws_matrix, return_counts=True)
        # Create a full counts array including missing numbers
        full_counts = np.zeros(hi + 1)
        full_counts[unique] = counts
        freq_raw = full_counts[all_numbers]
        max_c = np.max(freq_raw) if freq_raw.size > 0 else 1
        freq_score = freq_raw / max_c

        # 2. Gap Score (Vectorized)
        # We find the last index of each number
        last_indices = np.full(hi + 1, -1)
        for i, row in enumerate(draws_matrix):
            last_indices[row] = i
        
        gaps = (n_draws - 1) - last_indices[all_numbers]
        gap_score = gaps / n_draws

        # 3. Position Score (Vectorized)
        # Count occurrences per slot (D x P) -> (P x N)
        # We build a histogram per slot
        pos_score = np.zeros(len(all_numbers))
        for slot in range(pick):
            slot_nums = draws_matrix[:, slot]
            u_slot, c_slot = np.unique(slot_nums, return_counts=True)
            # Probability that this number appears in THIS specific slot
            # Note: we want to know how 'typical' it is for this number to be here
            # Score = max(P(number in slot X) for X in slots)
            slot_freq = np.zeros(hi + 1)
            slot_freq[u_slot] = c_slot
            # Update pos_score if this slot is more typical for the number than previous slots
            # This requires dividing by total appearances of that number to get concentration
            # but simpler is just raw count comparison for now
            pos_score = np.maximum(pos_score, slot_freq[all_numbers] / (freq_raw + 1e-9))

        # 4. Combine
        total_w = self.w_frequency + self.w_gap + self.w_position or 1.0
        combined_array = (
            self.w_frequency * freq_score
            + self.w_gap * gap_score
            + self.w_position * pos_score
        ) / total_w
        
        return dict(zip(all_numbers.tolist(), combined_array.tolist()))
