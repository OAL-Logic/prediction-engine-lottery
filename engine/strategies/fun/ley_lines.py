"""
Astro-Cartography & Ley Lines Strategy 🌐
=========================================
Maps the lottery's physical draw location against the Earth's esoteric energy grid.

Theory:
-------
The Earth is crisscrossed by 'Ley Lines'—invisible pathways of electromagnetic and 
spiritual energy. When a lottery is drawn near a major planetary node (e.g., the 
Becker-Hagens grid vertices), the ambient energy is heightened. This 'Earth Resonance' 
specifically amplifies numbers tied to sacred geometry (multiples of 3, 6, 9) and 
Platonic solids.

How it works:
-------------
1. Takes the latitude and longitude of the lottery's draw location.
2. Compares it against the coordinates of the 62 primary planetary grid nodes.
3. If the draw is within a resonance radius of a node, a 'Geomantic Boost' is triggered.
4. Boosts sacred numbers (3, 6, 9, 12, 33, 36, etc.) during active resonance.
"""

from __future__ import annotations

import pandas as pd
import math
from datetime import date

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

# A subset of Becker-Hagens planetary grid nodes (latitude, longitude)
_GRID_NODES = [
    (31.72, 35.22),   # Jerusalem
    (29.97, 31.13),   # Great Pyramid
    (51.17, -1.82),   # Stonehenge
    (-13.16, -72.54), # Machu Picchu
    (19.43, -99.13),  # Teotihuacan
    (36.19, -112.05), # Grand Canyon
    (37.38, 140.98),  # Mt. Fuji
    (-23.55, -46.63), # São Paulo Node (Example/Approximation for Brazilian resonance)
    (25.0, -75.0),    # Bermuda Triangle
    (-30.0, 120.0),   # Western Australia
]

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth (in km)."""
    R = 6371.0 # Earth radius in km
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

@register
class LeyLinesStrategy(BaseStrategy):
    name = "ley_lines"
    description = "🌐 Astro-Cartography — Earth grid resonance and sacred geometry"
    tier = "fun"
    requires_history = 1

    def __init__(self, latitude: Any = None, longitude: Any = None) -> None:
        """
        Parameters
        ----------
        latitude : float | str | None
            Physical latitude of the draw. (e.g. -23.55)
        longitude : float | str | None
            Physical longitude of the draw. (e.g. -46.63)
        """
        # Default to São Paulo Node if no location provided
        try:
            self.latitude = float(latitude) if latitude not in (None, "", "None") else -23.55
        except (ValueError, TypeError):
            self.latitude = -23.55
            
        try:
            self.longitude = float(longitude) if longitude not in (None, "", "None") else -46.63
        except (ValueError, TypeError):
            self.longitude = -46.63

        self._meta = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Default to São Paulo if no location provided (for Mega-Sena bias)
        lat = float(self.latitude) if self.latitude is not None else -23.55
        lon = float(self.longitude) if self.longitude is not None else -46.63
        
        # Find nearest node
        min_dist = float('inf')
        nearest_node = None
        for n_lat, n_lon in _GRID_NODES:
            dist = haversine_distance(lat, lon, n_lat, n_lon)
            if dist < min_dist:
                min_dist = dist
                nearest_node = (n_lat, n_lon)
                
        # Resonance radius (e.g., 500km)
        is_resonant = min_dist < 500.0
        
        self._meta = {
            "nearest_node_dist": round(min_dist, 1),
            "is_resonant": is_resonant,
            "geomantic_status": "Active (Ley Line Intersection)" if is_resonant else "Dormant (Grid Null Zone)"
        }
        
        scores = {n: 0.5 for n in all_numbers}
        
        # Sacred Geometry (Tesla's 3, 6, 9)
        sacred_roots = [3, 6, 9]
        
        for n in all_numbers:
            # Calculate digit root
            val = n
            while val > 9:
                val = sum(int(digit) for digit in str(val))
                
            if val in sacred_roots:
                # Slight base boost for sacred numbers
                scores[n] += 0.1
                # Massive boost if the physical draw is happening on a Ley Line
                if is_resonant:
                    scores[n] += 0.3
                    
        # Normalize
        max_s = max(scores.values()) or 1.0
        return {n: min(v / max_s, 1.0) for n, v in scores.items()}

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
