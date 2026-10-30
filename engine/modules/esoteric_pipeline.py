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
        """
        Fetches planetary Kp-index from NOAA with static fallback. Cached for
        the rest of the calendar day (keyed by today's date) so repeated
        calls on the same day — as --weather-seed relies on for its
        reproducibility guarantee — don't race a live, sub-daily-updating
        feed and land on different values.
        """
        def _do_fetch() -> float:
            try:
                url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
                resp = httpx.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    if len(data) > 1:
                        return float(data[-1][1])
            except Exception:
                pass
            return 3.0  # Quiet baseline

        from engine.cli.utils import get_cached_data
        result = get_cached_data(f"solar_kp_{date.today().isoformat()}", _do_fetch, ttl=86400)
        return result if result is not None else _do_fetch()
        
    def fetch_seismic_mag(self, lat: float, lon: float) -> float:
        """
        Fetches latest max magnitude seismic tremor near location within last
        day. Cached for the rest of the calendar day (see fetch_solar_kp) so
        --weather-seed stays reproducible across repeated same-day calls
        instead of racing a rolling "last 24h" live feed.
        """
        def _do_fetch() -> float:
            try:
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
            return 0.0  # Stable tectonic state

        from engine.cli.utils import get_cached_data
        result = get_cached_data(f"seismic_mag_{lat}_{lon}_{date.today().isoformat()}", _do_fetch, ttl=86400)
        return result if result is not None else _do_fetch()

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

    def fetch_weather(self, lat: float, lon: float, target_date: date) -> Dict[str, Optional[float]]:
        """
        Fetches real daily weather (mean temperature °C, precipitation mm) for the
        given coordinates and date from Open-Meteo — the same free/no-key public
        source used by the historical `weather` fun-strategy
        (engine/strategies/fun/weather.py). Used here only as one more real-world,
        deterministic ingredient for the hash below; on any network issue we fall
        back to `None` rather than raising, since this is personalization data,
        never a hard dependency.

        For today/future dates this hits the *forecast* endpoint, which is
        updated intraday — cached per (lat, lon, target_date) for the rest of
        the calendar day so repeated same-day calls (what --weather-seed's
        reproducibility guarantee depends on) don't race an updating forecast
        and land on different readings.
        """
        def _do_fetch() -> Dict[str, Optional[float]]:
            try:
                today = date.today()
                is_past = target_date < today
                base = (
                    "https://archive-api.open-meteo.com/v1/archive"
                    if is_past else "https://api.open-meteo.com/v1/forecast"
                )
                params = f"latitude={lat}&longitude={lon}&daily=temperature_2m_mean,precipitation_sum&timezone=auto"
                if is_past:
                    params += f"&start_date={target_date.isoformat()}&end_date={target_date.isoformat()}"
                else:
                    params += "&forecast_days=3"
                resp = httpx.get(f"{base}?{params}", timeout=self.timeout)
                if resp.status_code == 200:
                    daily = resp.json().get("daily", {})
                    dates = daily.get("time", [])
                    temps = daily.get("temperature_2m_mean", [])
                    precs = daily.get("precipitation_sum", [])
                    target_str = target_date.isoformat()
                    idx = dates.index(target_str) if target_str in dates else (0 if dates else None)
                    if idx is not None:
                        return {
                            "temperature_c": temps[idx] if idx < len(temps) else None,
                            "precip_mm": precs[idx] if idx < len(precs) else None,
                        }
            except Exception:
                pass
            return {"temperature_c": None, "precip_mm": None}

        from engine.cli.utils import get_cached_data
        result = get_cached_data(f"esoteric_weather_{lat}_{lon}_{target_date.isoformat()}", _do_fetch, ttl=86400)
        return result if result is not None else _do_fetch()

    def calculate_celestial_ephemeris(
        self,
        target_date: date,
        target_time: str = "20:00",
        coords: Tuple[float, float] = (-23.5505, -46.6333),
        wind_kmh: Optional[float] = None,
        precip_mm: Optional[float] = None,
        pressure_hpa: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Computes exact deterministic astronomical, seasonal, telluric, and
        severe-weather/vortex metrics for a given draw date, time, and location.
        Works across all world jurisdictions (Northern/Southern hemisphere aware).
        """
        import math
        from datetime import datetime as _dt, timedelta as _td
        from engine.strategies.fun.planetary_transits import (
            get_julian_date,
            get_obliquity,
            get_lst,
            get_kepler_longitude,
        )
        from engine.strategies.fun.moon_phase import (
            moon_phase_ratio,
            moon_distance_ratio,
            phase_name,
        )

        # Parse HH:MM
        try:
            parts = target_time.strip().split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
        except Exception:
            hour, minute = 20, 0

        lat, lon = float(coords[0]), float(coords[1])
        # Approximate timezone offset from longitude (or -3.0 for Brazil coordinates)
        tz_offset = -3.0 if (-35.0 <= lat <= 5.0 and -75.0 <= lon <= -30.0) else round(lon / 15.0)
        local_dt = _dt(target_date.year, target_date.month, target_date.day, hour, minute, 0)
        utc_dt = local_dt - _td(hours=tz_offset)

        jd = get_julian_date(utc_dt)
        obl = get_obliquity(jd)
        lst_deg = get_lst(jd, lon)

        # Solar & Lunar Ecliptic Longitudes (0-360 deg)
        sun_lon = round(float(get_kepler_longitude("sun", utc_dt)), 4)
        moon_lon = round(float(get_kepler_longitude("moon", utc_dt)), 4)

        # Earth Heliocentric Longitude (opposite to Sun geocentric longitude)
        earth_helio_lon = round((sun_lon + 180.0) % 360.0, 4)

        # Earth-Sun distance in AU (Keplerian eccentricity approximation)
        T = (jd - 2451545.0) / 36525.0
        M_earth = math.radians((357.52911 + 35999.05029 * T) % 360.0)
        e_earth = 0.016708634 - 0.000042037 * T
        earth_sun_dist_au = round(1.000001018 * (1.0 - e_earth * math.cos(M_earth)), 6)

        # Earth orbital velocity km/s (Vis-Viva equation: v ≈ 29.78 * sqrt(2/r - 1))
        earth_orbital_vel_kms = round(29.7847 * math.sqrt(max(0.1, 2.0 / earth_sun_dist_au - 1.0)), 4)

        # Season determination (Hemisphere-aware via ecliptic solar longitude)
        # 0-90: Spring (NH) / Autumn (SH)
        # 90-180: Summer (NH) / Winter (SH)
        # 180-270: Autumn (NH) / Spring (SH)
        # 270-360: Winter (NH) / Summer (SH)
        quadrant = int(sun_lon // 90) % 4
        is_southern = lat < 0
        sh_seasons = ["Autumn", "Winter", "Spring", "Summer"]
        nh_seasons = ["Spring", "Summer", "Autumn", "Winter"]
        season = sh_seasons[quadrant] if is_southern else nh_seasons[quadrant]
        season_progress = round((sun_lon % 90.0) / 90.0, 4)

        # Diurnal period & Hour Angle
        hour_fraction = (hour * 60 + minute) / 1440.0
        if 5 <= hour < 12:
            diurnal_period = "Morning"
        elif 12 <= hour < 18:
            diurnal_period = "Afternoon"
        elif 18 <= hour < 22:
            diurnal_period = "Evening/Nocturnal"
        else:
            diurnal_period = "Late Night"

        # Lunar anomalistic distance & phase name
        l_phase = moon_phase_ratio(target_date)
        l_dist_ratio = round(moon_distance_ratio(target_date), 4)
        l_phase_name = phase_name(target_date)

        # Atmospheric Vortex / Tornado / Cyclone Convective Potential Index (0.0 - 1.0)
        # Combines wind shear proxy, precipitation intensity, and low barometric pressure drop
        w_val = wind_kmh if wind_kmh is not None else 12.0
        p_val = precip_mm if precip_mm is not None else 0.0
        pr_val = pressure_hpa if pressure_hpa is not None else 1013.25
        pressure_drop = max(0.0, 1015.0 - pr_val)
        vortex_index = min(1.0, (w_val / 90.0) * 0.45 + (min(p_val, 80.0) / 80.0) * 0.35 + (pressure_drop / 35.0) * 0.20)
        vortex_index = round(float(vortex_index), 4)
        if vortex_index >= 0.65:
            vortex_regime = "Severe Convective / Tornado-Vortex Alert"
        elif vortex_index >= 0.30:
            vortex_regime = "Moderate Baroclinic / Storm Instability"
        else:
            vortex_regime = "Stable / Laminar Atmospheric Flow"

        return {
            "target_time": f"{hour:02d}:{minute:02d}",
            "julian_date": round(jd, 5),
            "local_sidereal_time_deg": round(lst_deg, 4),
            "obliquity_deg": round(obl, 4),
            "sun_longitude_deg": sun_lon,
            "moon_longitude_deg": moon_lon,
            "lunar_phase_name": l_phase_name,
            "lunar_distance_ratio": l_dist_ratio,
            "earth_heliocentric_lon_deg": earth_helio_lon,
            "earth_sun_distance_au": earth_sun_dist_au,
            "earth_orbital_velocity_kms": earth_orbital_vel_kms,
            "season": season,
            "season_progress": season_progress,
            "diurnal_period": diurnal_period,
            "diurnal_fraction": round(hour_fraction, 4),
            "wind_speed_kmh": round(w_val, 2),
            "pressure_hpa": round(pr_val, 2),
            "vortex_convective_index": vortex_index,
            "vortex_regime": vortex_regime,
        }

    def compile_context(
        self,
        full_name: str = "",
        birth_date: str = "1990-01-01",
        coords: Tuple[float, float] = (-23.5505, -46.6333),
        target_date: Optional[str] = None,
        override_solar_kp: Optional[float] = None,
        override_seismic_mag: Optional[float] = None,
        override_lunar_phase: Optional[float] = None,
        override_tide_level: Optional[float] = None,
        override_temp_c: Optional[float] = None,
        override_precip_mm: Optional[float] = None,
        target_time: Optional[str] = None,
        override_wind_kmh: Optional[float] = None,
        override_pressure_hpa: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Aggregates all personal and environmental features into a canonical
        context dictionary.

        `full_name` / `birth_date` default to neutral placeholders (matching the
        convention already used by `portfolio`'s "GEMINI ENGINE" / "1990-01-01")
        so pure environmental/weather use — no personal numerology requested —
        never requires real personal data.
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

        # 5. Real weather (Open-Meteo) — see fetch_weather() docstring above.
        if override_temp_c is not None or override_precip_mm is not None:
            temp_c, precip_mm = override_temp_c, override_precip_mm
        else:
            w = self.fetch_weather(coords[0], coords[1], t_date)
            temp_c, precip_mm = w.get("temperature_c"), w.get("precip_mm")

        ctx: Dict[str, Any] = {
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
                "tide_level": round(tide_level, 4),
                "temperature_c": round(temp_c, 2) if temp_c is not None else None,
                "precip_mm": round(precip_mm, 2) if precip_mm is not None else None,
            }
        }

        if target_time is not None or override_wind_kmh is not None or override_pressure_hpa is not None:
            ctx["celestial_ephemeris"] = self.calculate_celestial_ephemeris(
                target_date=t_date,
                target_time=target_time or "20:00",
                coords=coords,
                wind_kmh=override_wind_kmh,
                precip_mm=precip_mm,
                pressure_hpa=override_pressure_hpa,
            )

        return ctx

    def derive_seed(self, context: Dict[str, Any]) -> int:
        """
        Deterministically hashes a context dict (as produced by compile_context())
        down to a 32-bit integer seed. Same context in → same seed out, always —
        this is the property that makes it useful for reproducible runs, and it is
        the ONLY property being claimed. It carries no predictive information about
        future lottery draws (see module docstring).
        """
        serialized = json.dumps(context, sort_keys=True)
        h = hashlib.sha256(serialized.encode()).hexdigest()
        return int(h[:8], 16)

    def generate_weights(self, context: Dict[str, Any], lo: int, hi: int) -> Tuple[int, Dict[int, float]]:
        """
        Maps the aggregated context deterministically to a discrete 32-bit integer seed
        and a normalized, number-specific weighting matrix.
        """
        seed = self.derive_seed(context)

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

            # Weather jitter — extreme heat/cold at the draw location on record.
            # Same category of cosmetic, deterministic jitter as the Kp/seismic
            # terms above: it changes WHICH equally-valid combination this run
            # lands on, not the odds of any of them.
            temp_c = context["environmental"].get("temperature_c")
            if temp_c is not None and (temp_c >= 32.0 or temp_c <= 8.0):
                base_w = min(1.0, base_w + rng.uniform(0.01, 0.1))

            # Lunar amplification
            # Amplification peaking during spring tides (high tide_level)
            tide = context["environmental"]["tide_level"]
            base_w = min(1.0, base_w * (1.0 + tide * 0.1))

            # Celestial Ephemeris & Vortex Resonance (when target_time / ephemeris is active)
            ephem = context.get("celestial_ephemeris")
            if ephem:
                pool_size = max(1, hi - lo + 1)
                sun_deg = float(ephem.get("sun_longitude_deg", 0.0))
                moon_deg = float(ephem.get("moon_longitude_deg", 0.0))
                earth_deg = float(ephem.get("earth_heliocentric_lon_deg", 0.0))
                lst_deg = float(ephem.get("local_sidereal_time_deg", 0.0))
                vortex_idx = float(ephem.get("vortex_convective_index", 0.0))

                # Harmonic Modulo Projection onto Game Pool [lo..hi]
                resonant_nodes = {
                    (int(round(sun_deg)) % pool_size) + lo,
                    (int(round(moon_deg)) % pool_size) + lo,
                    (int(round(earth_deg)) % pool_size) + lo,
                    (int(round(lst_deg)) % pool_size) + lo,
                }
                if n in resonant_nodes:
                    base_w = min(1.0, base_w * 1.12)

                # Vortex / Severe Weather Convective Modulation
                if vortex_idx >= 0.30:
                    base_w = min(1.0, base_w + vortex_idx * 0.08 * rng.uniform(0.2, 1.0))
            
            raw_weights[n] = float(round(base_w, 6))
            
        # Normalize weights so they map cleanly to the suggestion engine expectations
        max_w = max(raw_weights.values()) or 1.0
        normed_weights = {n: float(round(w / max_w, 6)) for n, w in raw_weights.items()}

        return seed, normed_weights


# ---------------------------------------------------------------------------
# CLI convenience entry point
# ---------------------------------------------------------------------------

def build_environmental_seed(
    coords: Tuple[float, float],
    target_date: Optional[date] = None,
    full_name: str = "",
    birth_date: str = "1990-01-01",
    target_time: Optional[str] = None,
    wind_kmh: Optional[float] = None,
    pressure_hpa: Optional[float] = None,
    **overrides: Any,
) -> Tuple[int, Dict[str, Any]]:
    """
    Build today's (or `target_date`'s) full environmental context for `coords`
    and hash it down to a deterministic seed — no personal numerology required.

    Used by `suggest --weather-seed` / `--esoteric-mode` and `genetic-wheel
    --weather-seed` to replace *unseeded* randomness (Python's default
    OS-entropy `random`) with a *reproducible* one derived from real,
    independently-checkable data: today's date, real weather at the draw
    location (Open-Meteo), real lunar phase/tide, and real solar Kp (NOAA).

    This changes WHICH of the many equally-valid combinations a run lands on.
    It does not, and structurally cannot, change the probability that any
    given combination matches a future draw — see this module's docstring
    and README's "Privacy & Integrity" section.

    Returns
    -------
    (seed, context) — `context` is the full ingredient breakdown, suitable for
    printing so the choice stays fully auditable.
    """
    if wind_kmh is not None:
        overrides.setdefault("override_wind_kmh", wind_kmh)
    if pressure_hpa is not None:
        overrides.setdefault("override_pressure_hpa", pressure_hpa)
    pipeline = EsotericPipeline()
    context = pipeline.compile_context(
        full_name=full_name,
        birth_date=birth_date,
        coords=coords,
        target_date=target_date.isoformat() if target_date else None,
        target_time=target_time,
        **overrides,
    )
    seed = pipeline.derive_seed(context)
    return seed, context
