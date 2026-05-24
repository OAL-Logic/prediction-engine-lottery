"""
Weather Correlation Strategy  ⛅
==================================
Correlates lottery draw outcomes with the weather conditions on the draw date
at the lottery's draw location.

Data source: Open-Meteo Historical Weather API (free, no API key required)
  https://archive-api.open-meteo.com/v1/archive

Weather variables used
----------------------
  temperature_2m_mean   °C — daily mean temperature
  precipitation_sum     mm — daily total precipitation
  windspeed_10m_max     km/h — maximum wind speed

How it works
------------
1. For each historical draw date, fetch weather from Open-Meteo
2. Bucket draws into weather conditions (e.g. hot+dry, cold+wet, etc.)
3. Compute the current / upcoming draw's weather condition
4. Score each number by its frequency in draws with similar conditions

Weather buckets (3×2 = 6 buckets)
-----------------------------------
  Temperature:    cold (<15°C) | mild (15–25°C) | hot (>25°C)
  Precipitation:  dry (<1mm)   | wet (≥1mm)

Results are cached to data/weather_cache_{game}.json so we only hit
the API once per lottery.

Draw locations (default coordinates)
--------------------------------------
  Brazil (Caixa):  São Paulo  -23.5505, -46.6333
  US Powerball:    Tallahassee  30.4518, -84.2727  (Florida Lottery HQ)

Pass `latitude`, `longitude` to override.
"""

from __future__ import annotations

import json
import sys
import logging
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

_ARCHIVE_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude={lat}&longitude={lon}"
    "&start_date={start}&end_date={end}"
    "&daily=temperature_2m_mean,precipitation_sum,windspeed_10m_max,surface_pressure_mean"
    "&timezone=auto"
)
_FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&daily=temperature_2m_mean,precipitation_sum,windspeed_10m_max,surface_pressure_mean"
    "&forecast_days=3"
    "&timezone=auto"
)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"

# Default draw locations
_LOCATIONS: dict[str, tuple[float, float]] = {
    "br": (-23.5505, -46.6333),   # São Paulo
    "us": (30.4518,  -84.2727),   # Tallahassee, FL
}


logger = logging.getLogger(__name__)


def _temp_bucket(t: float | None) -> str:
    if t is None:
        return "?"
    if t < 15:
        return "cold"
    if t < 25:
        return "mild"
    return "hot"


def _precip_bucket(p: float | None) -> str:
    if p is None:
        return "?"
    return "wet" if p >= 1.0 else "dry"


def _density_bucket(temp: float | None, pressure: float | None) -> str:
    # Air density ρ = p / (R_specific * T)
    if temp is None or pressure is None:
        return "?"
    t_kelvin = temp + 273.15
    p_pa = pressure * 100.0
    density = p_pa / (287.058 * t_kelvin)
    
    # Standard sea level air density is ~1.225 kg/m^3
    if density < 1.15:
        return "light"
    if density > 1.25:
        return "heavy"
    return "normal"


def _refraction_index(temp: float | None, pressure: float | None) -> float:
    """
    Simplified atmospheric refractive index (n-1) * 10^6 (N-units).
    Refractivity N = 77.6 * (P / T)
    High N = higher moisture/density = lower static charge.
    """
    if temp is None or pressure is None:
        return 0.0
    t_kelvin = temp + 273.15
    return 77.6 * (pressure / t_kelvin)


def _weather_bucket(temp: float | None, precip: float | None, pressure: float | None) -> str:
    ref = _refraction_index(temp, pressure)
    ref_s = "low" if ref < 260 else "high" if ref > 300 else "med"
    return f"{_temp_bucket(temp)}_{_precip_bucket(precip)}_{_density_bucket(temp, pressure)}_{ref_s}"


@register
class WeatherStrategy(BaseStrategy):
    name        = "weather"
    description = "⛅ Weather correlation — numbers that appear when conditions match (Open-Meteo)"
    tier        = "fun"
    requires_history = 50

    def __init__(
        self,
        latitude:  float | None = None,
        longitude: float | None = None,
        country_hint: str = "br",
        upcoming_draw_date: date | None = None,
        timeout: float = 15.0,
    ) -> None:
        """
        Parameters
        ----------
        latitude
            Geographic coordinates (Lat). Precise location for weather data. 
            The wizard can help you find this via city search.
        longitude
            Geographic coordinates (Lon). Precise location for weather data.
        country_hint
            Regional data source. Used to pick default coordinates if none provided.
        upcoming_draw_date
            Draw date. Used to fetch the forecast for the day of the lottery.
        timeout
            API patience. How long to wait for the weather server to respond in seconds.
        """
        loc = _LOCATIONS.get(country_hint, _LOCATIONS["br"])
        self.latitude  = float(latitude)  if latitude  is not None else loc[0]
        self.longitude = float(longitude) if longitude is not None else loc[1]
        
        if isinstance(upcoming_draw_date, str) and upcoming_draw_date.strip() and upcoming_draw_date != "None":
            self.upcoming_draw_date = date.fromisoformat(upcoming_draw_date[:10])
        else:
            self.upcoming_draw_date = upcoming_draw_date or date.today()
            
        self.timeout   = float(timeout)
        self._correlation: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))

        # Handle NaT / None dates (Temporal Blindness fix)
        if pd.isna(self.upcoming_draw_date):
            logger.debug("Upcoming draw date is NaT; returning neutral scores.")
            return {n: 0.5 for n in all_numbers}

        # Fetch / load historical weather
        weather_map = self._load_weather(df)

        # Get upcoming draw weather
        upcoming_weather = self._fetch_upcoming_weather()
        target_temp   = upcoming_weather.get("temperature_2m_mean")
        target_precip = upcoming_weather.get("precipitation_sum")
        target_pressure = upcoming_weather.get("surface_pressure_mean")
        target_bucket = _weather_bucket(target_temp, target_precip, target_pressure)

        # Group draws by weather bucket; collect matched rows for evidence
        bucket_counts: dict[str, Counter]  = defaultdict(Counter)
        bucket_draws:  dict[str, int]      = defaultdict(int)
        matched_rows:  list[dict]          = []

        for _, row in df.iterrows():
            d_str = str(row["date"])[:10]
            w     = weather_map.get(d_str, {})
            temp  = w.get("temperature_2m_mean")
            prec  = w.get("precipitation_sum")
            pres  = w.get("surface_pressure_mean")
            bucket = _weather_bucket(temp, prec, pres)
            bucket_counts[bucket].update(row["numbers"])
            bucket_draws[bucket] += 1
            if bucket == target_bucket:
                matched_rows.append({
                    "date":        d_str,
                    "numbers":     sorted(row["numbers"]),
                    "condition":   bucket,
                    "temp_c":      round(temp, 1) if temp is not None else None,
                    "precip_mm":   round(prec, 1) if prec is not None else None,
                    "pressure_hpa": round(pres, 1) if pres is not None else None,
                })

        target_counts = bucket_counts.get(target_bucket, Counter())
        target_n      = bucket_draws.get(target_bucket, 0)

        # Build correlation evidence.
        # Sizes are driven by self.recent_matches_count / self.top_numbers_count
        # (BaseStrategy defaults: 5 and 10) so users can control them via the
        # CLI --recent-matches / --top-numbers flags without touching this file.
        matched_rows.sort(key=lambda r: r["date"], reverse=True)
        top_numbers = [
            {"number": n, "frequency": target_counts.get(n, 0)}
            for n, _ in target_counts.most_common(self.top_numbers_count)
        ]
        self._correlation = {
            "condition":      target_bucket,
            "temp_c":         round(target_temp, 1) if target_temp is not None else None,
            "precip_mm":      round(target_precip, 1) if target_precip is not None else None,
            "pressure_hpa":   round(target_pressure, 1) if target_pressure is not None else None,
            "refraction_n":   round(_refraction_index(target_temp, target_pressure), 1),
            "matched_draws":  target_n,
            "recent_matches": matched_rows[:self.recent_matches_count],
            "top_numbers":    top_numbers,
        }

        if target_n == 0:
            return {n: 1.0 / len(all_numbers) for n in all_numbers}

        raw   = {n: target_counts.get(n, 0) / target_n for n in all_numbers}
        max_v = max(raw.values()) or 1.0
        return {n: v / max_v for n, v in raw.items()}

    # ------------------------------------------------------------------
    # suggest() — override to inject correlation evidence
    # ------------------------------------------------------------------

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._correlation)
        return result

    # ------------------------------------------------------------------
    # Weather fetch helpers
    # ------------------------------------------------------------------

    def _load_weather(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        """Return {date_str: {variable: value}} for all draw dates."""
        cache_path = DATA_DIR / f"weather_{self.latitude:.2f}_{self.longitude:.2f}.json"

        cached: dict[str, dict[str, float]] = {}
        if cache_path.exists():
            try:
                cached = json.loads(cache_path.read_text())
            except json.JSONDecodeError:
                cached = {}

        dates = sorted({str(row["date"])[:10] for _, row in df.iterrows()})
        missing = [d for d in dates if d not in cached]

        if missing:
            try:
                fetched = self._fetch_archive(missing[0], missing[-1])
                cached.update(fetched)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(cached, indent=2))
            except Exception as exc:
                print(f"  ⚠ Weather fetch failed: {exc}", file=sys.stderr)

        return cached

    def _fetch_archive(
        self, start: str, end: str
    ) -> dict[str, dict[str, float]]:
        url = _ARCHIVE_URL.format(
            lat=self.latitude, lon=self.longitude,
            start=start, end=end,
        )
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temps = daily.get("temperature_2m_mean", [])
        precs = daily.get("precipitation_sum", [])
        winds = daily.get("windspeed_10m_max", [])
        press = daily.get("surface_pressure_mean", [])

        result: dict[str, dict[str, float]] = {}
        for i, d in enumerate(dates):
            result[d] = {
                "temperature_2m_mean": temps[i] if i < len(temps) else None,
                "precipitation_sum":   precs[i] if i < len(precs) else None,
                "windspeed_10m_max":   winds[i] if i < len(winds) else None,
                "surface_pressure_mean": press[i] if i < len(press) else None,
            }
        return result

    def _fetch_historical_weather(self, date_str: str, rules: DrawRules) -> dict[str, float | None]:
        """Fetch weather for a specific historical date (cached)."""
        # Ensure cache is loaded for this lottery's location
        # (Usually called via score(), but we handle it here for safety)
        # We don't have the full DF here, so we just use the date_str
        cache_path = DATA_DIR / f"weather_{self.latitude:.2f}_{self.longitude:.2f}.json"
        cached = {}
        if cache_path.exists():
            try:
                cached = json.loads(cache_path.read_text())
            except Exception:
                cached = {}
        
        if date_str in cached:
            return cached[date_str]
            
        # If missing, fetch just this date
        try:
            fetched = self._fetch_archive(date_str, date_str)
            if fetched:
                cached.update(fetched)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(json.dumps(cached, indent=2))
                return fetched.get(date_str, {})
        except Exception as exc:
            logger.debug("Single date weather fetch failed: %s", exc)
            
        return {}

    def _fetch_upcoming_weather(self) -> dict[str, float | None]:
        import pandas as pd
        if pd.isna(self.upcoming_draw_date):
            return {}
            
        target = str(self.upcoming_draw_date)[:10]

        # If the target date is in the past, use the archive API
        if self.upcoming_draw_date < date.today():
            try:
                archive = self._fetch_archive(target, target)
                if target in archive:
                    return archive[target]
            except Exception as exc:
                logger.debug("Weather archive fetch failed for backtest: %s", exc)
            return {}

        try:
            url = _FORECAST_URL.format(lat=self.latitude, lon=self.longitude)
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.json()

            daily = data.get("daily", {})
            times = daily.get("time", [])
            
            # Find the best match: exact target or first available forecast
            match_idx = -1
            if target in times:
                match_idx = times.index(target)
            elif times:
                # If target (upcoming) is not in the 3-day forecast yet,
                # fall back to the most recent available forecast (usually today)
                match_idx = 0
            
            if match_idx >= 0:
                return {
                    "temperature_2m_mean": daily.get("temperature_2m_mean", [])[match_idx],
                    "precipitation_sum":   daily.get("precipitation_sum",   [])[match_idx],
                    "windspeed_10m_max":   daily.get("windspeed_10m_max",   [])[match_idx],
                    "surface_pressure_mean": daily.get("surface_pressure_mean", [])[match_idx] if "surface_pressure_mean" in daily else None,
                }
        except Exception as exc:
            logger.debug("Weather forecast fetch failed: %s", exc)

        return {}
