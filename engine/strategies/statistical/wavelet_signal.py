"""
Wavelet Signal Strategy 🌊
==========================
Uses Discrete Wavelet Transform (DWT) to decompose the binary time series
of each number's appearances into different scales. 
Analyzes 'approximation' (low-freq trend) and 'details' (high-freq bursts).
Predicts the next value in the series by reconstructing from filtered components.
"""

from __future__ import annotations

import pywt
import pandas as pd
import numpy as np

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class WaveletSignalStrategy(BaseStrategy):
    name = "wavelet_signal"
    description = "🌊 Wavelet Decomposition (Multi-Scale Analysis)"
    tier = "statistical"

    requires_history = 64 # Needs a power-of-2 window for best results

    def __init__(self, wavelet: str = "db4") -> None:
        self.wavelet = wavelet

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        df = df.sort_values("draw_id").reset_index(drop=True)
        # Use a power-of-2 window
        n_draws = len(df)
        window_size = 2**int(np.floor(np.log2(n_draws)))
        if window_size < 32:
            return {n: 0.5 for n in all_numbers}
            
        window_df = df.tail(window_size)
        
        # Build appearance matrix
        matrix = np.zeros((window_size, hi - lo + 1))
        for i, row in enumerate(window_df.itertuples()):
            for num in row.numbers:
                if lo <= num <= hi:
                    matrix[i, num - lo] = 1.0
                    
        scores = {}
        for idx, n in enumerate(all_numbers):
            ts = matrix[:, idx]
            
            # Decompose
            coeffs = pywt.wavedec(ts, self.wavelet, level=3)
            
            # Reconstruct slightly biased towards the recent pulses
            # We look at the 'detail' coefficients of the most recent level
            details = coeffs[-1]
            pulse_strength = np.abs(details[-1])
            
            # Approximation (low-freq trend)
            approx = coeffs[0]
            trend_strength = approx[-1]
            
            # Blend: current trend + recent high-freq pulse
            score = (trend_strength * 0.4) + (pulse_strength * 0.6)
            scores[n] = float(score)
            
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        min_s = min(scores.values()) if scores else 0.0
        
        if max_s > min_s:
            scores = {n: (v - min_s) / (max_s - min_s) for n, v in scores.items()}
        else:
            scores = {n: 0.5 for n in all_numbers}
            
        return scores
