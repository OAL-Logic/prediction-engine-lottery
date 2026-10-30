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
        full_name: str = "GEMINI ENGINE",
        birth_date: str = "1990-01-01",
        coords_str: str = "-23.5505,-46.6333", # Coordinates for São Paulo Caixa base
        target_date: str | None = None,
        target_time: str | None = None,
        solar_kp: float | None = None,
        seismic_mag: float | None = None,
        lunar_phase: float | None = None,
        tide_level: float | None = None,
        wind_kmh: float | None = None,
        pressure_hpa: float | None = None,
        weight_personal: float = 0.40,
        weight_lunar: float = 0.20,
        weight_solar: float = 0.20,
        weight_seismic: float = 0.20,
        **kwargs: Any,
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
        target_time : str | None
            Scheduled draw time in HH:MM format (e.g., "20:00").
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
            
        self.target_date = str(target_date)[:10] if target_date else date.today().isoformat()
        self.target_time = target_time
        
        # Overrides
        self.solar_kp = solar_kp
        self.seismic_mag = seismic_mag
        self.lunar_phase = lunar_phase
        self.tide_level = tide_level
        self.wind_kmh = wind_kmh
        self.pressure_hpa = pressure_hpa
        
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
            target_time=self.target_time,
            override_solar_kp=self.solar_kp,
            override_seismic_mag=self.seismic_mag,
            override_lunar_phase=self.lunar_phase,
            override_tide_level=self.tide_level,
            override_wind_kmh=self.wind_kmh,
            override_pressure_hpa=self.pressure_hpa,
        )
        
        # Generate deterministic weights using deterministic hash mapping
        seed, esot_weights = self.pipeline.generate_weights(context, lo, hi)
        
        # Multi-Domain Synthesis:
        # 1. Esoteric / Celestial / Geophysical / Vortex / Spiritual (esot_weights)
        # 2. Timeless Statistical Frequency (full historical distribution)
        # 3. Temporal Cycle Completion & Recency Momentum (missing cycle numbers + EWMA)
        # 4. Homologous Historical Reference Resonance (draws at same Earth orbital
        #    longitude, same Lunar synodic phase, and same Weekday cycle)
        weights = dict(esot_weights)
        if not df.empty and "numbers" in df.columns:
            from collections import Counter
            pool_size = max(1, hi - lo + 1)

            # (A) Timeless empirical frequency
            counts = Counter(n for row in df["numbers"] for n in row if lo <= n <= hi)
            max_c = max(counts.values()) if counts else 1
            timeless_freq = {n: counts.get(n, 0) / max_c for n in range(lo, hi + 1)}

            # (B) Temporal Cycle Completion & Recent Momentum (last 50 draws)
            seen_in_cycle: set[int] = set()
            for row in reversed(df["numbers"].tolist()):
                row_valid = {n for n in row if lo <= n <= hi}
                if len(seen_in_cycle | row_valid) >= pool_size:
                    break
                seen_in_cycle |= row_valid
            missing_in_cycle = set(range(lo, hi + 1)) - seen_in_cycle

            recent_rows = df["numbers"].tail(50).tolist()
            rec_counts = Counter(n for row in recent_rows for n in row if lo <= n <= hi)
            max_rec = max(rec_counts.values()) if rec_counts else 1
            temporal_score = {}
            for n in range(lo, hi + 1):
                cycle_boost = 1.0 if n in missing_in_cycle else 0.0
                rec_norm = rec_counts.get(n, 0) / max_rec
                temporal_score[n] = 0.65 * rec_norm + 0.35 * cycle_boost

            # (C) Homologous Historical Reference Resonance (Orbital + Lunar + Weekday)
            t_date_obj = date.fromisoformat(self.target_date[:10])
            t_doy = t_date_obj.timetuple().tm_yday
            t_lunar = ((t_date_obj.toordinal() - 730125) % 29.530588853) / 29.530588853
            t_weekday = t_date_obj.weekday()

            homologous_Accumulator: dict[int, float] = {n: 0.0 for n in range(lo, hi + 1)}
            orbital_matches = 0
            lunar_matches = 0
            weekday_matches = 0

            date_col = "date" if "date" in df.columns else ("draw_date" if "draw_date" in df.columns else None)
            if date_col:
                for dt_val, nums in zip(df[date_col], df["numbers"]):
                    try:
                        d_str = str(dt_val)[:10]
                        d_obj = date.fromisoformat(d_str)
                    except Exception:
                        continue
                    # Earth heliocentric / seasonal day-of-year circular distance
                    d_doy = d_obj.timetuple().tm_yday
                    doy_diff = abs(d_doy - t_doy)
                    orbital_dist = min(doy_diff, 365.25 - doy_diff)
                    is_orbital = orbital_dist <= 12.0  # ~12 deg of Earth's orbit

                    # Lunar synodic phase circular distance
                    d_lunar = ((d_obj.toordinal() - 730125) % 29.530588853) / 29.530588853
                    lunar_diff = abs(d_lunar - t_lunar)
                    lunar_dist = min(lunar_diff, 1.0 - lunar_diff)
                    is_lunar = lunar_dist <= 0.10

                    # Same weekday
                    is_weekday = (d_obj.weekday() == t_weekday)

                    sim_w = 0.0
                    if is_orbital:
                        orbital_matches += 1
                        sim_w += 0.45 * (1.0 - orbital_dist / 15.0)
                    if is_lunar:
                        lunar_matches += 1
                        sim_w += 0.35 * (1.0 - lunar_dist / 0.12)
                    if is_weekday:
                        weekday_matches += 1
                        sim_w += 0.20

                    if sim_w > 0.0:
                        for n in nums:
                            if lo <= n <= hi:
                                homologous_Accumulator[n] += sim_w

            max_hom = max(homologous_Accumulator.values()) if any(homologous_Accumulator.values()) else 1.0
            homologous_score = {
                n: (homologous_Accumulator[n] / max_hom) if max_hom > 0 else 0.5
                for n in range(lo, hi + 1)
            }

            for n in range(lo, hi + 1):
                weights[n] = round(
                    0.35 * esot_weights.get(n, 0.5)
                    + 0.25 * timeless_freq.get(n, 0.5)
                    + 0.20 * temporal_score.get(n, 0.5)
                    + 0.20 * homologous_score.get(n, 0.5),
                    6,
                )

            top_homologous = sorted(homologous_score.items(), key=lambda kv: kv[1], reverse=True)[:10]
            context["homologous_resonance"] = {
                "orbital_homologues_count": orbital_matches,
                "lunar_homologues_count": lunar_matches,
                "weekday_homologues_count": weekday_matches,
                "cycle_missing_numbers": sorted(missing_in_cycle),
                "top_homologous_numbers": [n for n, _ in top_homologous],
            }
        
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
        pick = kwargs.get("pick") or rules.pick_count
        pool_override = kwargs.get("pool")
        key_numbers = [n for n in (kwargs.get("key") or []) if lo <= n <= hi]
        filters_list = kwargs.get("filters")
        k_of_n = kwargs.get("filters_k_of_n", 0)
        seed_override = kwargs.get("seed")
        
        # Calculate historical statistical bounds from history (scaled if pick != rules.pick_count)
        pick_ratio = pick / float(rules.pick_count) if rules.pick_count else 1.0
        if not df.empty:
            hist_sums = df["numbers"].apply(sum) * pick_ratio
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
        if pool_override:
            numbers = [n for n in pool_override if lo <= n <= hi and n not in key_numbers]
        else:
            numbers = [n for n in range(lo, hi + 1) if n not in key_numbers]
        needed = max(0, pick - len(key_numbers))
        
        # Deterministic generator seeded by our pipeline hash (or seed override)
        active_seed = seed_override if seed_override is not None else self._last_seed
        local_rng = np.random.default_rng(active_seed)
        
        tickets: list[list[int]] = []
        attempts = 0
        max_attempts = count * 500
        
        # Parity limits
        if pick == 5: # Quina
            allowed_odds = {2, 3} # 2:3 or 3:2 balance
        elif pick == 6: # Mega-Sena
            allowed_odds = {2, 3, 4} # 2:4, 3:3, 4:2 balance
        elif pick == 15: # Lotofácil
            allowed_odds = {7, 8, 9, 6, 10} # High parity balance (around 8:7)
        else:
            allowed_odds = set(range(max(1, int(pick * 0.3)), min(pick - 1, int(pick * 0.7)) + 1))
            
        # Compile probabilities based on temperature-scaled weights
        raw_p = np.array([max(1e-9, scores[n]) for n in numbers], dtype=float)
        # Sharpen weights with temperature
        scaled_temp = max(0.1, temperature)
        raw_p = raw_p ** (1.0 / scaled_temp)
        probs = raw_p / raw_p.sum() if len(raw_p) > 0 else np.array([])
        
        while len(tickets) < count and attempts < max_attempts:
            attempts += 1
            
            # Weighted sample of numbers without replacement
            if needed > 0 and len(numbers) >= needed:
                sampled = local_rng.choice(numbers, size=needed, replace=False, p=probs).tolist()
                ticket = sorted(list(key_numbers) + sampled)
            else:
                ticket = sorted(list(key_numbers)[:pick])
            
            # --- Strict Statistical Core Gate Filters ---
            
            # Gate A: Parity ratio check (Odd/Even count)
            odds = sum(1 for n in ticket if n % 2 != 0)
            if odds not in allowed_odds:
                continue
                
            # Gate B: Standard Deviation bounds on the ticket sum
            t_sum = sum(ticket)
            if t_sum < sum_min or t_sum > sum_max:
                continue
                
            # Gate C: Universal Row/Decade Cluster Detection (Game-agnostic via rules.board_cols)
            row_width = max(5, getattr(rules, "board_cols", 10) or 10)
            pool_span = max(1, hi - lo + 1)
            num_rows = max(1, (pool_span + row_width - 1) // row_width)
            expected_per_row = pick / float(num_rows)
            # Dynamic maximum per row: 2 for pick=5 on 8 rows, 3 for pick=6 on 6 rows, 4 for pick=15 on 5 rows
            if pick <= 5 and num_rows >= 6:
                max_row_cluster = 2
            elif pick <= 6 and num_rows >= 5:
                max_row_cluster = 3
            else:
                max_row_cluster = max(2, min(row_width, int(np.ceil(expected_per_row * 1.65))))
            row_counts = [0] * (num_rows + 1)
            for n in ticket:
                idx = min(num_rows, max(0, (n - lo) // row_width))
                row_counts[idx] += 1
            if max(row_counts) > max_row_cluster:
                continue
                    
            # Gate D: Optional Harmony Filters from CLI
            if filters_list and not self.is_harmonious(ticket, rules, filters=filters_list, k_of_n=k_of_n, df=df, birth_date=self.birth_date, target_date=self.target_date):
                continue

            # Avoid duplicate tickets
            if ticket not in tickets:
                tickets.append(ticket)
                
        # Handle fallback if statistical gates are too strict and fail to converge
        if len(tickets) < count:
            logger.warning("Strict statistical gates failed to fully converge. Relaxing constraints for fallback tickets.")
            while len(tickets) < count:
                if needed > 0 and len(numbers) >= needed:
                    sampled = local_rng.choice(numbers, size=needed, replace=False, p=probs).tolist()
                    ticket = sorted(list(key_numbers) + sampled)
                else:
                    ticket = sorted(list(key_numbers)[:pick])
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
