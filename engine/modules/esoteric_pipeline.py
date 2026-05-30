"""
Esoteric Data Ingestion & Hashing Pipeline 🔮🌌
===============================================
Ingests personal user data, lunar phase details, tide calculations, 
seismic metrics, solar geomagnetic activity, and numerological values,
mapping them deterministically to a discrete seed and a weighting matrix.

This pipeline is constructed strictly for mathematical modeling and simulation
and does not possess any real-world lottery prediction capabilities.
"""

from __future__ import annotations
import json
import hashlib
import time
import httpx
from datetime import date, datetime
from typing import Dict, Any, Tuple, Optional
import numpy as np

# ---------------------------------------------------------------------------
# Gematria / Numerology Core (Chaldean / Kabbalistic style)
# ---------------------------------------------------------------------------
_LETTER_MAP = {
    'A': 1, 'I': 1, 'Q': 1, 'J': 1, 'Y': 1,
    'B': 2, 'K': 2, 'R': 2,
    'C': 3, 'G': 3, 'L': 3, 'S': 3,
    'D': 4, 'M': 4, 'T': 4,
    'E': 5, 'H': 5, 'N': 5, 'X': 5,
    'U': 6, 'V': 6, 'W': 6,
    'O': 7, 'Z': 7,
    'F': 8, 'P': 8
}
_VOWELS = set("AEIOU")
_MASTER = {11, 22}

def _digit_reduce(n: int, preserve_master: bool = True) -> int:
    """Standard numerology reduction to 1-9, preserving 11 and 22."""
    if preserve_master and n in _MASTER:
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n or 9

def _calculate_gematria(name: str) -> Dict[str, int]:
    """Calculates Motivation (vowels), Impression (consonants), and Expression (all)."""
    clean_name = "".join(c for c in name.upper() if c.isalnum())
    vowel_sum = 0
    consonant_sum = 0
    
    for char in clean_name:
        if char in _LETTER_MAP:
            val = _LETTER_MAP[char]
            if char in _VOWELS:
                vowel_sum += val
            else:
                consonant_sum += val
                
    return {
        "motivation": _digit_reduce(vowel_sum),
        "impression": _digit_reduce(consonant_sum),
        "expression": _digit_reduce(vowel_sum + consonant_sum)
    }

def _calculate_destiny(birth_date: date) -> int:
    """Calculates Destiny number from reduced date components."""
    d_red = _digit_reduce(birth_date.day, preserve_master=False)
    m_red = _digit_reduce(birth_date.month, preserve_master=False)
    y_red = _digit_reduce(sum(int(d) for d in str(birth_date.year)), preserve_master=False)
    return _digit_reduce(d_red + m_red + y_red)

# ---------------------------------------------------------------------------
# Environmental Ingestion & Fallbacks
# ---------------------------------------------------------------------------
class EsotericPipeline:
    """
    Ingests environmental, astrological, and personal user data,
    processing them deterministically into a discrete numerical seed
    and a normalized number-weighting matrix.
    """
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        
    def fetch_solar_kp(self) -> float:
        """Fetches planetary Kp-index from NOAA with static fallback."""
        try:
            url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
            resp = httpx.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1:
                    return float(data[-1][1])
        except Exception:
            pass
        return 3.0 # Quiet baseline
        
    def fetch_seismic_mag(self, lat: float, lon: float) -> float:
        """Fetches latest max magnitude seismic tremor near location within last day."""
        try:
            # Query USGS last 24h
            url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude={lat}&longitude={lon}&maxradiuskm=500&minmagnitude=1.0"
            resp = httpx.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if features:
                    mags = [f["properties"]["mag"] for f in features if f["properties"]["mag"] is not None]
                    return max(mags) if mags else 0.0
        except Exception:
            pass
        return 0.0 # Stable tectonic state

    def calculate_lunar_phase(self, target_date: date) -> float:
        """
        Approximates lunar phase cycle (0.0 = New Moon, 0.5 = Full Moon, 1.0 = New Moon).
        Simple deterministic approximation.
        """
        # Base New Moon: Jan 6, 2000
        base_date = date(2000, 1, 6)
        diff_days = (target_date - base_date).days
        synodic_month = 29.53059
        phase = (diff_days % synodic_month) / synodic_month
        return round(phase, 4)

    def calculate_tide_intensity(self, lunar_phase: float) -> float:
        """
        Approximates tide intensity based on lunar phase.
        Tide is strongest at New Moon (0.0/1.0) and Full Moon (0.5) (Spring Tides).
        """
        # Distance from nearest Spring Tide
        dist = abs(lunar_phase - 0.5) if lunar_phase > 0.25 and lunar_phase < 0.75 else min(lunar_phase, 1.0 - lunar_phase)
        # Strongest when distance to spring tide is 0
        intensity = 1.0 - (dist / 0.25)
        return round(max(0.0, min(1.0, intensity)), 4)

    def compile_context(
        self,
        full_name: str,
        birth_date: str,
        coords: Tuple[float, float],
        target_date: Optional[str] = None,
        override_solar_kp: Optional[float] = None,
        override_seismic_mag: Optional[float] = None,
        override_lunar_phase: Optional[float] = None,
        override_tide_level: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Aggregates all personal and environmental features into a canonical
        context dictionary.
        """
        # 1. Standardize dates
        t_date = date.fromisoformat(target_date[:10]) if target_date else date.today()
        b_date = date.fromisoformat(birth_date[:10])
        
        # 2. Personal Numerology
        gematria = _calculate_gematria(full_name)
        destiny = _calculate_destiny(b_date)
        mission = _digit_reduce(gematria["expression"] + destiny)
        
        # 3. Geophysical & Solar Data
        solar_kp = override_solar_kp if override_solar_kp is not None else self.fetch_solar_kp()
        seismic_mag = override_seismic_mag if override_seismic_mag is not None else self.fetch_seismic_mag(coords[0], coords[1])
        
        # 4. Lunar & Tidal calculations
        lunar_phase = override_lunar_phase if override_lunar_phase is not None else self.calculate_lunar_phase(t_date)
        tide_level = override_tide_level if override_tide_level is not None else self.calculate_tide_intensity(lunar_phase)
        
        return {
            "full_name": full_name,
            "birth_date": b_date.isoformat(),
            "coords": coords,
            "target_date": t_date.isoformat(),
            "numerology": {
                "motivation": gematria["motivation"],
                "impression": gematria["impression"],
                "expression": gematria["expression"],
                "destiny": destiny,
                "mission": mission
            },
            "environmental": {
                "solar_kp": round(solar_kp, 2),
                "seismic_mag": round(seismic_mag, 2),
                "lunar_phase": round(lunar_phase, 4),
                "tide_level": round(tide_level, 4)
            }
        }

    def generate_weights(self, context: Dict[str, Any], lo: int, hi: int) -> Tuple[int, Dict[int, float]]:
        """
        Maps the aggregated context deterministically to a discrete 32-bit integer seed
        and a normalized, number-specific weighting matrix.
        """
        # Serialize to deterministic JSON
        serialized = json.dumps(context, sort_keys=True)
        h = hashlib.sha256(serialized.encode()).hexdigest()
        
        # 1. Discrete numerical seed (take first 8 hex characters as 32-bit integer)
        seed = int(h[:8], 16)
        
        # 2. Deterministic weight generation
        # We initialize a NumPy generator with this exact seed to guarantee determinism
        rng = np.random.default_rng(seed)
        
        numbers = list(range(lo, hi + 1))
        raw_weights = {}
        
        # Base numerical weights seeded by generator
        for n in numbers:
            # Generate a base weight in [0, 1]
            base_w = rng.uniform(0.1, 0.9)
            
            # Layer personal vibrations (Expression/Destiny congruence)
            # Numbers matching destiny or expression digit receive a 15% boost
            digit_val = _digit_reduce(n)
            if digit_val == context["numerology"]["destiny"] or digit_val == context["numerology"]["expression"]:
                base_w = min(1.0, base_w * 1.15)
                
            # Layer environmental storm jitter
            # High solar Kp (> 5) or seismic activity (> 3) injects deterministic jitter
            kp = context["environmental"]["solar_kp"]
            seismic = context["environmental"]["seismic_mag"]
            
            if kp >= 5.0:
                base_w = min(1.0, base_w + rng.uniform(0.01, 0.1))
            if seismic >= 3.0:
                base_w = min(1.0, base_w + rng.uniform(0.01, 0.1))
                
            # Lunar amplification
            # Amplification peaking during spring tides (high tide_level)
            tide = context["environmental"]["tide_level"]
            base_w = min(1.0, base_w * (1.0 + tide * 0.1))
            
            raw_weights[n] = float(round(base_w, 6))
            
        # Normalize weights so they map cleanly to the suggestion engine expectations
        max_w = max(raw_weights.values()) or 1.0
        normed_weights = {n: float(round(w / max_w, 6)) for n, w in raw_weights.items()}
        
        return seed, normed_weights
