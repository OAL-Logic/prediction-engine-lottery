"""
Esoteric Statistical Strategy 🔮⚖️
==================================
Registered strategy that fuses a deterministic environmental hashing pipeline
with strict quantitative statistical core filters. 

This class implements the mathematical simulation pipeline and does not
possess any objective lottery prediction or winning capabilities.
"""

from __future__ import annotations
import logging
from datetime import date
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register
from engine.modules.esoteric_pipeline import EsotericPipeline

logger = logging.getLogger(__name__)

@register
class EsotericStatisticalStrategy(BaseStrategy):
    name = "esoteric_statistical"
    description = "🔮 Esoteric Hashing × Statistical Core (Parity, StdDev, Cluster Gates)"
    tier = "fun"
    requires_history = 10 # Low history threshold to ensure maximum compatibility

    def __init__(
        self,
        full_name: str = "GEMINI USER",
        birth_date: str = "1995-05-15",
        coords_str: str = "-23.5505,-46.6333", # Coordinates for São Paulo Caixa base
        target_date: str | None = None,
        solar_kp: float | None = None,
        seismic_mag: float | None = None,
        lunar_phase: float | None = None,
        tide_level: float | None = None,
        weight_personal: float = 0.40,
        weight_lunar: float = 0.20,
        weight_solar: float = 0.20,
        weight_seismic: float = 0.20,
    ) -> None:
        """
        Parameters
        ----------
        full_name : str
            Full birth name for Gematria calculations.
        birth_date : str
            Birthdate in YYYY-MM-DD format.
        coords_str : str
            Latitude and longitude separated by comma (e.g., "-23.5505,-46.6333").
        target_date : str | None
            ISO-8601 target draw date string.
        solar_kp : float | None
            Planetary Kp override for testing.
        seismic_mag : float | None
            USGS earthquake magnitude override for testing.
        lunar_phase : float | None
            Lunar cycle phase override for testing.
        tide_level : float | None
            Marine tide level override for testing.
        """
        self.full_name = full_name
        self.birth_date = birth_date
        
        # Parse coordinates safely
        try:
            lat_s, lon_s = coords_str.split(",")
            self.coords = (float(lat_s), float(lon_s))
        except Exception:
            self.coords = (-23.5505, -46.6333)
            
        self.target_date = target_date or date.today().isoformat()
        
        # Overrides
        self.solar_kp = solar_kp
        self.seismic_mag = seismic_mag
        self.lunar_phase = lunar_phase
        self.tide_level = tide_level
        
        # Ingestion pipeline instance
        self.pipeline = EsotericPipeline()

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        """
        Computes the primary esoteric weighting matrix for the lottery pool numbers,
        seeded by the hashed environmental and astrological context.
        """
        lo, hi = rules.number_range
        
        # Compile environmental and astrological context
        context = self.pipeline.compile_context(
            full_name=self.full_name,
            birth_date=self.birth_date,
            coords=self.coords,
            target_date=self.target_date,
            override_solar_kp=self.solar_kp,
            override_seismic_mag=self.seismic_mag,
            override_lunar_phase=self.lunar_phase,
            override_tide_level=self.tide_level
        )
        
        # Generate deterministic weights using deterministic hash mapping
        seed, weights = self.pipeline.generate_weights(context, lo, hi)
        
        # Store for metadata access in suggest()
        self._last_context = context
        self._last_seed = seed
        self._last_weights = weights
        
        return weights

    def suggest(
        self,
        df: pd.DataFrame,
        rules: DrawRules,
        count: int = 1,
        temperature: float = 1.0,
        **kwargs: Any
    ) -> SuggestionResult:
        """
        Generates tickets biased by the esoteric weighting matrix, but strictly
        filtered by standard statistical core validation gates:
          1. Parity balancing (Odd/Even counts).
          2. Standard deviation bounds on total sum.
          3. Decade-based cluster detection to prevent crowding.
        """
        # 1. Compute baseline scores / weights
        scores = self.score(df, rules)
        
        lo, hi = rules.number_range
        pick = rules.pick_count
        
        # Calculate historical statistical bounds from history
        if not df.empty:
            hist_sums = df["numbers"].apply(sum)
            mean_sum = hist_sums.mean()
            std_sum = hist_sums.std()
            # If standard deviation is 0 or NaN, default to logical bounds
            if pd.isna(std_sum) or std_sum == 0:
                std_sum = (hi - lo) * np.sqrt(pick) / 4
        else:
            mean_sum = ((lo + hi) / 2) * pick
            std_sum = (hi - lo) * np.sqrt(pick) / 4
            
        # 2-Standard Deviation bounds
        sum_min = mean_sum - 2.0 * std_sum
        sum_max = mean_sum + 2.0 * std_sum
        
        # Active numbers
        numbers = list(range(lo, hi + 1))
        
        # Deterministic generator seeded by our pipeline hash
        local_rng = np.random.default_rng(self._last_seed)
        
        tickets: list[list[int]] = []
        attempts = 0
        max_attempts = count * 500
        
        # Parity limits
        if pick == 6: # Mega-Sena
            allowed_odds = {2, 3, 4} # 2:4, 3:3, 4:2 balance
        elif pick == 15: # Lotofácil
            allowed_odds = {7, 8, 9, 6, 10} # High parity balance (around 8:7)
        else:
            allowed_odds = set(range(int(pick * 0.3), int(pick * 0.7) + 1))
            
        # Compile probabilities based on temperature-scaled weights
        raw_p = np.array([scores[n] for n in numbers])
        # Sharpen weights with temperature
        scaled_temp = max(0.1, temperature)
        raw_p = raw_p ** (1.0 / scaled_temp)
        probs = raw_p / raw_p.sum()
        
        while len(tickets) < count and attempts < max_attempts:
            attempts += 1
            
            # Weighted sample of numbers without replacement
            ticket = sorted(local_rng.choice(numbers, size=pick, replace=False, p=probs).tolist())
            
            # --- Strict Statistical Core Gate Filters ---
            
            # Gate A: Parity ratio check (Odd/Even count)
            odds = sum(1 for n in ticket if n % 2 != 0)
            if odds not in allowed_odds:
                continue
                
            # Gate B: Standard Deviation bounds on the ticket sum
            t_sum = sum(ticket)
            if t_sum < sum_min or t_sum > sum_max:
                continue
                
            # Gate C: Historical Cluster Detection (Prevent decade crowding)
            # Mega-Sena decades: 0s (1-9), 10s (10-19), 20s (20-29), etc.
            # Lotofácil rows: 1-5, 6-10, 11-15, 16-20, 21-25.
            if pick == 6:
                # Max 3 numbers in any decade
                decade_counts = [0] * 7
                for n in ticket:
                    decade_counts[n // 10] += 1
                if max(decade_counts) > 3:
                    continue
            elif pick == 15:
                # Max 5 numbers in any row (decade equivalent on 5x5 grid)
                row_counts = [0] * 6
                for n in ticket:
                    row_counts[(n - 1) // 5] += 1
                if max(row_counts) > 5:
                    continue
                    
            # Avoid duplicate tickets
            if ticket not in tickets:
                tickets.append(ticket)
                
        # Handle fallback if statistical gates are too strict and fail to converge
        if len(tickets) < count:
            logger.warning("Strict statistical gates failed to fully converge. Relaxing constraints for fallback tickets.")
            while len(tickets) < count:
                ticket = sorted(local_rng.choice(numbers, size=pick, replace=False, p=probs).tolist())
                if ticket not in tickets:
                    tickets.append(ticket)
                    
        # Wrap final result
        res = SuggestionResult(
            strategy_name=self.name,
            tickets=tickets,
            scores=scores,
            confidence=float(np.mean(list(scores.values()))),
            metadata={
                "seed": self._last_seed,
                "context": self._last_context,
                "statistical_gates": {
                    "sum_bounds": (round(sum_min, 1), round(sum_max, 1)),
                    "parity_allowed_odds": list(allowed_odds)
                }
            }
        )
        
        return res
