"""
Lorentz Attractor Strategy 🌪️
=============================
Uses a chaotic Lorenz system to score numbers based on 'Strange Attractors.'

Theory:
-------
The Lorenz system is a set of differential equations that describe chaotic 
flow. By mapping board numbers to 3D space (x, y, z) and running a short 
simulation, we can see which numbers the 'butterfly' visits most often.
This is a pure Chaos Mode strategy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import date
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class LorentzStrategy(BaseStrategy):
    name = "lorentz"
    description = "🌪️ Lorenz Attractor — chaotic flow simulation and strange attractor scoring"
    tier = "fun"
    requires_history = 0

    def __init__(self, sigma: float = 10.0, rho: float = 28.0, beta: Any = "8/3") -> None:
        """
        Parameters
        ----------
        sigma : float
            Prandtl number (default: 10.0). Controls the 'stretch' of the attractor.
        rho : float
            Rayleigh number (default: 28.0). Controls the point of convective instability.
        beta : float | str
            Geometric factor (default: '8/3'). Controls the aspect ratio of the strange attractor.
        """
        self.sigma = float(sigma)
        self.rho = float(rho)
        
        # Safely evaluate string fractions (like '8/3') from CLI/Wizard
        if isinstance(beta, str) and "/" in beta:
            try:
                num, den = beta.split("/")
                self.beta = float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                self.beta = 8/3
        else:
            try:
                self.beta = float(beta)
            except (ValueError, TypeError):
                self.beta = 8/3

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = np.array(list(range(lo, hi + 1)))
        
        # 1. Map numbers to a 3D grid
        n_points = len(all_numbers)
        side = int(np.ceil(n_points**(1/3)))
        
        # Build mapping matrix (N x 3)
        indices = np.arange(n_points)
        x_m = indices % side
        y_m = (indices // side) % side
        z_m = indices // (side * side)
        mapping_matrix = np.stack([x_m, y_m, z_m], axis=1).astype(float)

        # 2. Run Lorentz simulation
        target_date = kwargs.get("draw_date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date[:10])
            
        dt = 0.01
        steps = 2000
        
        # Pre-allocate trajectory
        trajectory = np.zeros((steps, 3))
        # Initial state seeded by date
        trajectory[0] = [target_date.day / 10, target_date.month / 10, target_date.year / 2000]
        
        # Core Lorentz integration
        curr = trajectory[0]
        for i in range(1, steps):
            x, y, z = curr
            dx = self.sigma * (y - x) * dt
            dy = (x * (self.rho - z) - y) * dt
            dz = (x * y - self.beta * z) * dt
            curr = curr + [dx, dy, dz]
            trajectory[i] = curr
            
        # 3. Vectorized Nearest-Neighbor Scoring
        # Scale and modulo trajectory to fit mapping space
        scaled_trajectory = trajectory % side
        
        # Calculate distances from every step to every board point
        # (steps, 1, 3) - (1, n_points, 3) -> (steps, n_points, 3)
        diffs = scaled_trajectory[:, np.newaxis, :] - mapping_matrix[np.newaxis, :, :]
        dists = np.linalg.norm(diffs, axis=2) # (steps, n_points)
        
        # Find index of closest board point for each step
        closest_indices = np.argmin(dists, axis=1)
        
        # Count visits
        unique_idx, counts = np.unique(closest_indices, return_counts=True)
        visit_counts = {all_numbers[idx]: count for idx, count in zip(unique_idx, counts)}
            
        # 4. Score based on visit frequency
        max_v = max(visit_counts.values()) if visit_counts else 1
        scores = {n: visit_counts.get(n, 0) / max_v for n in all_numbers}
        
        return scores

from collections import Counter
