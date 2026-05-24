"""
Sacred Geometry Strategy 🌀
===========================
Overlays the Golden Ratio (Phi) spiral onto the physical layout of the 
lottery ticket. Calculates the physical coordinates of each number, finds
the geometric center, and traces a Fibonacci spiral outwards. 
Numbers that lie exactly on the spiral path get maximum resonance scores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import math

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class SacredGridStrategy(BaseStrategy):
    name = "sacred_grid"
    description = "🌀 Geometria Sagrada (Espiral de Phi)"
    tier = "fun"

    requires_history = 0 # Pure geometric, no history needed

    def _get_coords(self, n: int, rules: DrawRules) -> tuple[float, float]:
        """Convert number to (x, y) coordinates based on board width."""
        width = rules.board_cols or 10
        # For a standard grid, row = (n-1)//width, col = (n-1)%width
        # Let's map it so (0,0) is top-left
        row = (n - 1) // width
        col = (n - 1) % width
        return float(col), float(row)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Find the geometric center of the board
        width = rules.board_cols or 10
        height = math.ceil((hi - lo + 1) / width)
        
        center_x = (width - 1) / 2.0
        center_y = (height - 1) / 2.0
        
        scores = {}
        
        # Golden ratio
        PHI = (1 + math.sqrt(5)) / 2
        
        # Generate a set of points along the Golden Spiral
        # r = a * e^(b * theta), where b = ln(Phi) / (pi/2)
        b = math.log(PHI) / (math.pi / 2)
        a = 0.5 # Scale factor
        
        spiral_points = []
        for theta in np.linspace(0, 8 * math.pi, 200): # 4 full turns
            r = a * math.exp(b * theta)
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            
            # Only keep points within the board
            if -1 <= x <= width and -1 <= y <= height:
                spiral_points.append((x, y))
                
        # 2. Score each number based on its minimum distance to the spiral
        max_possible_dist = math.sqrt(width**2 + height**2)
        
        for n in all_numbers:
            nx, ny = self._get_coords(n, rules)
            
            if not spiral_points:
                scores[n] = 0.5
                continue
                
            # Find min distance to any spiral point
            min_dist = min(math.sqrt((nx - px)**2 + (ny - py)**2) for px, py in spiral_points)
            
            # The closer to the spiral, the higher the score
            # We use an exponential decay so points exactly on the spiral get 1.0, and it drops fast
            score = math.exp(-min_dist * 2.0)
            
            # Add micro jitter
            jitter = (n % 7) * 0.005
            scores[n] = min(1.0, score + jitter)
            
        # Normalize
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: v / max_s for n, v in scores.items()}
