"""
Bio-Feedback Pulse Strategy 💓
==============================
Simulates a 'Pulse' sensor on the historical draw sequence.
Calculates the autocorrelation of the total appearance count (binary time series)
for each number to identify rhythmic cycles.
Numbers that align with an active rhythmic pulse get a 'Resonance Boost'.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class BioFeedbackStrategy(BaseStrategy):
    name = "bio_feedback"
    description = "💓 Bio-Feedback Pulse — detects rhythmic resonance in draw sequences"
    tier = "fun"

    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        df = df.sort_values("draw_id").reset_index(drop=True)
        n_draws = len(df)
        
        # 1. Build binary appearance matrix
        matrix = np.zeros((n_draws, hi - lo + 1))
        for i, row in enumerate(df.itertuples()):
            for num in row.numbers:
                if lo <= num <= hi:
                    matrix[i, num - lo] = 1.0
                    
        scores = {}
        for idx, n in enumerate(all_numbers):
            ts = matrix[:, idx]
            
            # 2. Calculate Autocorrelation
            # We look for a 'pulse' in the last 20 lags
            lags = range(1, 15)
            autocorr = []
            
            # Mean center for correlation
            ts_centered = ts - np.mean(ts)
            
            for lag in lags:
                # np.correlate provides a simple way to find autocorrelation
                # r = E[(X_t - mu)(X_{t-lag} - mu)] / sigma^2
                if n_draws > lag:
                    c = np.correlate(ts_centered[lag:], ts_centered[:-lag])[0]
                    autocorr.append(c)
                else:
                    autocorr.append(0.0)
            
            # 3. Detect Pulse Strength
            # The pulse is the maximum autocorrelation at any significant lag
            pulse_strength = max(autocorr) if autocorr else 0.0
            
            # Check if current state aligns with the detected pulse
            # If lag 'k' is strongest, was it 'k' draws ago?
            best_lag = lags[np.argmax(autocorr)] if autocorr else 1
            last_hit_ago = 0
            found = False
            for i in range(1, min(30, n_draws)):
                if ts[-i] == 1.0:
                    last_hit_ago = i
                    found = True
                    break
            
            # Resonance = high autocorrelation AND recent alignment with period
            resonance = 0.0
            if found:
                # How well does last_hit_ago align with best_lag?
                alignment = 1.0 - (abs(last_hit_ago - best_lag) / best_lag)
                resonance = pulse_strength * max(0, alignment)
                
            # Base frequency component
            base_freq = np.mean(ts)
            
            scores[n] = (base_freq * 0.3) + (resonance * 0.7)

        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: v / max_s for n, v in scores.items()}
