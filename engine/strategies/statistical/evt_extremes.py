from __future__ import annotations

import pandas as pd
import numpy as np
import math
from typing import Dict

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class EVTExtremesStrategy(BaseStrategy):
    """
    Extreme Value Theory (EVT) Strategy 🌋
    ======================================
    Focuses on the "Tail of the Distribution" instead of the mean.
    
    Theory: The lottery is a statistical extreme event. By modeling the 
    Largest Delays (Maxima) using the Generalized Extreme Value (GEV) 
    distribution or Peaks-Over-Threshold (POT), we can detect when a 
    number is about to suffer a "support breakout" and be drawn due to 
    extreme mathematical pressure.
    """
    name = "evt_extremes"
    description = "🌋 Extreme Value Theory (EVT - Tail Breakout)"

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        scores = {n: 0.1 for n in range(lo, hi + 1)}
        
        if len(df) < 50:
            return scores

        for num in range(lo, hi + 1):
            # Find all 'gaps' (delays between hits) for the number
            gaps = []
            current_gap = 0
            # Important: iterate from past to present
            for _, row in df.iloc[::-1].iterrows():
                if num in row['numbers']:
                    gaps.append(current_gap)
                    current_gap = 0
                else:
                    current_gap += 1
            
            # Current delay is current_gap after processing full history
            current_delay = current_gap
            
            if len(gaps) < 3:
                scores[num] = 0.5
                continue
                
            # Simplified Peaks-Over-Threshold (POT) approach
            # Take only gaps representing the 10% largest historical delays for this number
            threshold = np.percentile(gaps, 90)
            extremes = [g for g in gaps if g > threshold]
            
            if not extremes:
                continue
                
            # Calculate mean of extremes (expected shortfall)
            mean_extreme = np.mean(extremes)
            
            # If CURRENT delay is approaching or exceeding the mean of extremes,
            # we are in a "Tail Breakout" zone (High EVT Probability)
            if current_delay > threshold:
                # Exponential activation function based on how extreme the delay is
                urgency = min(1.0, current_delay / (mean_extreme * 1.2))
                scores[num] = float(urgency)
            else:
                # If not in the extreme tail, score drops rapidly
                scores[num] = float(current_delay / threshold) * 0.4

        # Normalize
        max_s = max(scores.values())
        min_s = min(scores.values())
        if max_s > min_s:
            scores = {k: (v - min_s) / (max_s - min_s) for k, v in scores.items()}
            
        return scores
