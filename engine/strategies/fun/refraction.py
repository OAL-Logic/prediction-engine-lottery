"""
Atmospheric Refraction Strategy 🌡️
=================================
Scores numbers based on the Refractive Index (N) of the atmosphere during the draw.

Theory:
-------
The refractive index of air, N = 77.6 * (P / T), where P is pressure (hPa) 
and T is temperature (K), influences static charge accumulation on 
pneumatic lottery balls. This strategy correlates historical winning 
numbers with the air's dielectric state.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import date
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register
from engine.strategies.fun.weather import WeatherStrategy


@register
class RefractionStrategy(BaseStrategy):
    name = "refraction"
    description = "🌡️ Atmospheric Refraction — correlate hits with static-charge potential (N-Index)"
    tier = "fun"
    requires_history = 50

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Fetch historical weather context (reusing Weather Strategy cache)
        # Initialize WeatherStrategy with rules-derived location if possible
        country = "br" if "mega-sena" in rules.name.lower() or "lotofacil" in rules.name.lower() else "us"
        w_strat = WeatherStrategy(country_hint=country)
        
        # 2. Calculate historical N-Index for each draw
        hist_n = []
        weather_cache = w_strat._load_weather(df)
        
        for _, row in df.iterrows():
            d_str = str(row["date"])[:10]
            w_data = weather_cache.get(d_str, {})
            
            # P in hPa, T in Celsius -> Kelvin
            # N ≈ 77.6 * (P / (T + 273.15))
            p = w_data.get("surface_pressure_mean")
            t = w_data.get("temperature_2m_mean")
            
            if p and t is not None:
                n_idx = 77.6 * (p / (t + 273.15))
                hist_n.append((n_idx, row["numbers"]))
        
        # 3. Calculate Target N-Index (Today)
        target_date = kwargs.get("draw_date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date[:10])
            
        w_strat.upcoming_draw_date = target_date
        t_w_data = w_strat._fetch_upcoming_weather()
        t_p = t_w_data.get("surface_pressure_mean")
        t_t = t_w_data.get("temperature_2m_mean")
        
        if not t_p or t_t is None:
            # Fallback to neutral if no weather data
            return {n: 0.5 for n in all_numbers}
            
        target_n = 77.6 * (t_p / (t_t + 273.15))
        
        # 4. Score by frequency in similar Refraction regimes
        # N usually stays between 250 and 350
        tolerance = 5.0
        matches = [nums for n, nums in hist_n if abs(n - target_n) < tolerance]
        
        if not matches:
            return {n: 0.5 for n in all_numbers}
            
        from collections import Counter
        counts = Counter([n for d in matches for n in d])
        max_c = max(counts.values()) if counts else 1
        
        return {n: counts.get(n, 0) / max_c for n in all_numbers}
