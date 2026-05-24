"""
Hurst Memory Strategy 🌀
=========================
Calculates the Hurst exponent (H) for each number using R/S analysis.
H measures the 'memory' of a time series:
  H = 0.5: Random Walk (White Noise)
  H > 0.5: Persistent (Trends tend to continue)
  H < 0.5: Anti-Persistent (Mean-reverting)

Scoring logic:
- High H numbers get a boost if they appeared recently (momentum).
- Low H numbers get a boost if they haven't appeared recently (mean reversion).
- H near 0.5 numbers are treated as noise.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

def calculate_hurst(ts: np.ndarray) -> float:
    """Compute Hurst exponent via Rescaled Range (R/S) analysis."""
    N = len(ts)
    if N < 20:
        return 0.5
    
    # Use logarithmic spacing for lags
    max_lag = N // 2
    lags = np.unique(np.geomspace(5, max_lag, 10).astype(int))
    
    rs_values = []
    for lag in lags:
        # Split into chunks of size 'lag'
        n_chunks = N // lag
        if n_chunks == 0: continue
        
        rs_list = []
        for i in range(n_chunks):
            chunk = ts[i*lag : (i+1)*lag]
            # Rescaled Range
            mean = np.mean(chunk)
            centered = chunk - mean
            cumsum = np.cumsum(centered)
            R = np.max(cumsum) - np.min(cumsum)
            S = np.std(chunk)
            if S > 0:
                rs_list.append(R / S)
        
        if rs_list:
            rs_values.append((lag, np.mean(rs_list)))
            
    if len(rs_values) < 3:
        return 0.5
        
    lags_log = np.log([r[0] for r in rs_values])
    rs_log = np.log([r[1] for r in rs_values])
    
    # Hurst exponent is the slope of the log-log plot
    H, _ = np.polyfit(lags_log, rs_log, 1)
    return float(np.clip(H, 0.0, 1.0))

@register
class HurstMemoryStrategy(BaseStrategy):
    name = "hurst_memory"
    description = "📈 Hurst Exponent (Inertia & System Memory)"
    tier = "statistical"

    requires_history = 100 # Needs substantial history for R/S analysis

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        df = df.sort_values("draw_id").reset_index(drop=True)
        n_draws = len(df)
        
        # Build appearance matrix
        matrix = np.zeros((n_draws, hi - lo + 1))
        for i, row in enumerate(df.itertuples()):
            for num in row.numbers:
                if lo <= num <= hi:
                    matrix[i, num - lo] = 1.0
                    
        scores = {}
        for idx, n in enumerate(all_numbers):
            ts = matrix[:, idx]
            H = calculate_hurst(ts)
            
            # Check recent appearance (last 5 draws)
            recent_hit_rate = np.mean(ts[-5:])
            
            if H > 0.6: # Persistent
                # If recently hit, likely to hit again
                score = 0.5 + (recent_hit_rate * 0.5)
            elif H < 0.4: # Anti-persistent
                # If NOT recently hit, likely to revert to mean (hit)
                score = 0.5 + ((1.0 - recent_hit_rate) * 0.5)
            else: # Random walk / Noise
                score = 0.3 # Low confidence
                
            # Blend with absolute frequency
            total_freq = np.mean(ts)
            scores[n] = (score * 0.7) + (total_freq * 0.3)
            
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: v / max_s for n, v in scores.items()}
