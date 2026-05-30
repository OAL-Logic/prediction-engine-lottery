"""
Sacred Manifold Grid Strategy 🌀
=================================
Projects the lottery grid numbers onto a non-Euclidean sphere.
Modulates number resonance scores based on celestial transit azimuths (Lunar & Solar zenith/altitude).
"""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
from typing import Any

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.modules.geometry import get_manifold_coords
from engine.modules.environment import EnvironmentalService

@register
class SacredManifoldStrategy(BaseStrategy):
    name = "sacred_manifold"
    description = "🌀 Sacred Manifold Grid — aligns spherical ticket manifolds with celestial azimuth transits"
    tier = "fun"
    requires_history = 0

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Fetch current celestial transits from the environmental service
        try:
            env = EnvironmentalService()
            jitter = env.get_jitter()
            from datetime import datetime
            now = datetime.now()
            hour_fraction = (now.hour * 3600 + now.minute * 60 + now.second) / 86400.0
            angle = hour_fraction * 2.0 * math.pi
            
            # Modulate angle using geomagnetic Kp flux
            kp_mod = (jitter.get("kp", 3.0) / 9.0) * math.pi
            celestial_azimuth = angle + kp_mod
        except Exception:
            celestial_azimuth = 0.0
            
        # 2. Convert celestial azimuth to a unit vector on the manifold sphere equator
        cosmic_vector = (math.cos(celestial_azimuth), math.sin(celestial_azimuth), 0.0)
        
        scores = {}
        for n in all_numbers:
            # Project number to unit sphere coordinates
            x, y, z = get_manifold_coords(n, rules, "sphere")
            
            # 3. Calculate dot product (cosine similarity) with the cosmic alignment vector
            dot_product = x * cosmic_vector[0] + y * cosmic_vector[1] + z * cosmic_vector[2]
            resonance = (dot_product + 1.0) / 2.0
            
            # prime oscillator multiplier
            is_prime = n in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
            prime_factor = 1.05 if is_prime else 0.95
            
            scores[n] = resonance * prime_factor

        # Normalize scores to [0, 1]
        max_s = max(scores.values()) if scores else 1.0
        if max_s == 0: max_s = 1.0
        return {n: float(v / max_s) for n, v in scores.items()}
