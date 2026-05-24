"""
Spectral Analysis Strategy  🌊
================================
FFT-based periodicity detection — finds numbers that appear to oscillate
on a regular cycle and scores them based on phase alignment with the
upcoming draw.

How it works
------------
1. For each number, build a binary time series:
       series[i] = 1 if number appeared in draw i, else 0

2. Apply a real-valued FFT (numpy.fft.rfft) to each series.

3. Find the dominant frequency component (peak magnitude, excluding DC).
   The corresponding cycle length is:
       cycle_len = N / dominant_freq_index

4. Determine the current phase — where in the cycle are we right now?
   The number's last appearance establishes a phase anchor:
       draws_since_last = N - last_draw_index - 1
       phase_offset = draws_since_last % cycle_len

5. Score = magnitude_strength × cos(2π × phase_offset / cycle_len)
   A score near 1.0 means both:
     • The number has a strong periodic signal (high magnitude)
     • The current moment aligns with a peak in that cycle

When the FFT finds no meaningful periodicity (magnitude below threshold),
the number falls back to a uniform frequency-based score.

Notes
-----
For a truly fair lottery, the FFT will find only noise — all magnitudes near
equal. This is by design. The strategy is most interesting when applied to
historical data from real draws, where ball-machine quirks, seasonal schedule
changes, or pure noise occasionally create apparent patterns.

The minimum_magnitude threshold (default 2.0) filters out cycles so weak
they are indistinguishable from noise. Higher = more selective.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class SpectralStrategy(BaseStrategy):
    name        = "spectral"
    description = "🌊 FFT periodicity detection — numbers whose cycle aligns with the next draw"
    tier        = "statistical"
    requires_history = 50

    def __init__(self, minimum_magnitude: float = 2.0) -> None:
        """
        Parameters
        ----------
        minimum_magnitude
            Minimum FFT peak magnitude to treat as a real signal.
            Below this, the number is scored by plain frequency.
            Increase for stricter periodicity filtering.
        """
        self.minimum_magnitude = float(minimum_magnitude)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        df = df.sort_values("draw_id").reset_index(drop=True)
        n = len(df)

        if n < 4:
            return {num: 1.0 / len(all_numbers) for num in all_numbers}

        # Build presence matrix: shape (n_draws, pool_size)
        idx_map = {num: i for i, num in enumerate(all_numbers)}
        pool    = len(all_numbers)
        matrix  = np.zeros((n, pool), dtype=np.float32)
        for t, (_, row) in enumerate(df.iterrows()):
            for num in row["numbers"]:
                if num in idx_map:
                    matrix[t, idx_map[num]] = 1.0

        # Last appearance index per number
        last_seen = np.full(pool, -1, dtype=int)
        for t in range(n):
            for i in range(pool):
                if matrix[t, i] == 1.0:
                    last_seen[i] = t

        # Plain frequency fallback scores (normalised)
        freq = matrix.sum(axis=0) / n
        freq_norm = freq / (freq.max() + 1e-9)

        # FFT per number
        raw = np.zeros(pool, dtype=np.float64)

        for i in range(pool):
            series    = matrix[:, i].astype(np.float64)
            fft_vals  = np.fft.rfft(series)
            magnitudes = np.abs(fft_vals)

            # Exclude DC component (index 0) — that's just the mean
            peak_idx  = int(np.argmax(magnitudes[1:])) + 1
            peak_mag  = magnitudes[peak_idx]

            if peak_mag < self.minimum_magnitude:
                # No meaningful periodicity — fall back to frequency
                raw[i] = freq_norm[i]
                continue

            # Cycle length in draws
            cycle_len = n / peak_idx

            # Phase offset: how far into the cycle will the next draw be?
            if last_seen[i] < 0:
                # Never appeared — score by frequency only
                raw[i] = freq_norm[i]
                continue

            draws_to_next = n - last_seen[i]   # draws from last appearance to the upcoming draw
            phase_frac  = (draws_to_next % cycle_len) / cycle_len
            # cos peaks at 0 and 1 (aligned with a new expected appearance),
            # troughs at 0.5 (halfway between appearances)
            phase_score = 0.5 * (np.cos(2 * np.pi * phase_frac) + 1.0)

            # Combine: magnitude strength × phase alignment
            strength = np.tanh(peak_mag / self.minimum_magnitude)   # 0 → 1
            raw[i]   = strength * phase_score + (1.0 - strength) * freq_norm[i]

        max_v = raw.max()
        if max_v == 0:
            return {num: 1.0 / pool for num in all_numbers}

        normed = raw / max_v
        return {all_numbers[i]: float(normed[i]) for i in range(pool)}
