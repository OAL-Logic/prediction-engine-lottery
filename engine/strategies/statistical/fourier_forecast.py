"""
Fourier Forecast Strategy 🌊
============================
Uses Discrete Fourier Transform (DFT) on the historical sequence of draw sums.
Identifies the dominant global rhythms and projects the expected sum of the next draw.
Scores numbers based on how well they align with the projected average.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class FourierForecastStrategy(BaseStrategy):
    name = "fourier_forecast"
    description = "🌊 Fourier Spectral Projection — predicts next draw sum via dominant rhythm"
    tier = "statistical"

    requires_history = 60

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Get sequence of sums
        sums = [sum(row.numbers) for row in df.itertuples()]
        n = len(sums)
        
        if n < 30:
            return {num: 0.5 for num in all_numbers}
            
        # 2. Perform FFT
        # Subtract mean to remove DC component
        mean_sum = np.mean(sums)
        centered_sums = sums - mean_sum
        
        fft_result = np.fft.rfft(centered_sums)
        frequencies = np.fft.rfftfreq(n)
        
        # 3. Find dominant frequencies (top 3)
        magnitudes = np.abs(fft_result)
        # Set DC to 0 just in case
        magnitudes[0] = 0
        
        top_indices = np.argsort(magnitudes)[-3:]
        
        # 4. Project next value (t = n)
        # Reconstruct using only the top frequencies
        t_next = n
        projected_centered_sum = 0.0
        
        for idx in top_indices:
            # Complex amplitude
            c = fft_result[idx]
            # Frequency
            f = frequencies[idx]
            
            # The original signal is roughly sum of (C_k * exp(i * 2 * pi * f_k * t)) / N
            # For rfft, the reconstruction of a specific frequency component k at time t is:
            # 2/N * |C_k| * cos(2 * pi * f_k * t + phase_k)
            amp = np.abs(c)
            phase = np.angle(c)
            
            term = (2.0 / n) * amp * np.cos(2 * np.pi * f * t_next + phase)
            projected_centered_sum += term
            
        projected_sum = mean_sum + projected_centered_sum
        
        # Bound the projected sum to valid ranges
        min_possible_sum = sum(range(lo, lo + rules.pick_count))
        max_possible_sum = sum(range(hi - rules.pick_count + 1, hi + 1))
        projected_sum = np.clip(projected_sum, min_possible_sum, max_possible_sum)
        
        # 5. Score numbers
        # If the target sum is X, the average number should be X / pick_count
        target_avg = projected_sum / rules.pick_count
        
        scores = {}
        max_dist = max(abs(hi - target_avg), abs(lo - target_avg))
        if max_dist == 0: max_dist = 1.0
        
        for num in all_numbers:
            # Closer to the target average is better
            dist = abs(num - target_avg)
            score = 1.0 - (dist / max_dist)
            
            # Add a micro-jitter based on historical frequency to break ties
            scores[num] = max(0.01, score)

        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {num: v / max_s for num, v in scores.items()}
