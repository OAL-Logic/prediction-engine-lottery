"""
Kinetic Simulator Strategy 🎱
============================
A pseudo-physics engine that simulates lottery balls bouncing in a 2D drum.
Balls are seeded with initial velocities based on their historical frequencies,
and we simulate elastic collisions. Balls that spend the most time near the
"exit chute" (bottom of the drum) get higher scores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class KineticStrategy(BaseStrategy):
    name = "kinetic"
    description = "🎱 Pseudo-Kinetic Simulation — models balls bouncing in a 2D drum"
    tier = "fun"

    requires_history = 10

    def __init__(self, steps: int = 1000, dt: float = 0.1) -> None:
        self.steps = steps
        self.dt = dt

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        n_balls = hi - lo + 1
        all_numbers = list(range(lo, hi + 1))
        
        # Initial frequencies
        freqs = {n: 0.0 for n in all_numbers}
        if not df.empty:
            for row in df.itertuples():
                for num in row.numbers:
                    freqs[num] = freqs.get(num, 0.0) + 1.0
        
        max_f = max(freqs.values()) if freqs else 1.0
        if max_f == 0: max_f = 1.0
        
        # Simulation setup
        # Drum is a circle of radius R=100
        R = 100.0
        
        # Balls: pos(x,y), vel(vx,vy)
        pos = np.random.uniform(-R/2, R/2, (n_balls, 2))
        
        # Velocity seeded by frequency (hotter balls move faster)
        speeds = np.array([freqs[n] / max_f * 50 + 10 for n in all_numbers])
        angles = np.random.uniform(0, 2*np.pi, n_balls)
        vel = np.column_stack((speeds * np.cos(angles), speeds * np.sin(angles)))
        
        exit_hits = {n: 0.0 for n in all_numbers}
        
        # Gravity
        g = np.array([0, -9.8])
        
        for _ in range(self.steps):
            vel += g * self.dt
            pos += vel * self.dt
            
            # Boundary collision
            dists = np.linalg.norm(pos, axis=1)
            out_of_bounds = dists > R
            if np.any(out_of_bounds):
                # Reflect velocity normal to boundary
                normals = pos[out_of_bounds] / dists[out_of_bounds][:, np.newaxis]
                vel[out_of_bounds] -= 2 * np.sum(vel[out_of_bounds] * normals, axis=1)[:, np.newaxis] * normals
                # Push back inside
                pos[out_of_bounds] = normals * R * 0.99
                
                # Check if hit exit chute (bottom of drum, e.g., y < -0.9*R and abs(x) < 0.2*R)
                hit_exit = (pos[out_of_bounds][:, 1] < -0.9 * R) & (np.abs(pos[out_of_bounds][:, 0]) < 0.2 * R)
                
                # Find which numbers hit the exit
                indices_out = np.where(out_of_bounds)[0]
                exit_indices = indices_out[hit_exit]
                for idx in exit_indices:
                    exit_hits[all_numbers[idx]] += 1.0
                    
        # Normalize scores
        max_h = max(exit_hits.values()) if exit_hits else 1.0
        if max_h == 0: max_h = 1.0
        return {n: v / max_h for n, v in exit_hits.items()}
