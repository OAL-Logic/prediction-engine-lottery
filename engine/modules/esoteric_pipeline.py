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

    @classmethod
    def analyze_historical_correlations(
        cls,
        df: Any,
        rules: Any,
        target_date: Optional[str] = None,
        target_time: Optional[str] = "20:00",
        coords: Tuple[float, float] = (-23.5505, -46.6333),
    ) -> Dict[str, Any]:
        """
        Comprehensive Lunar, Orbital, Tidal, Seasonal & Weekday correlation analysis
        across all historical draws of any lottery game.

        Computes:
          1. 8-Phase Lunar Breakdown (draw counts, sum Cohen's d, parity, primes,
             and top Binomial Z-score numbers per moon phase).
          2. Continuous Metric vs. Structural Property Pearson r & p-value matrix
             (Lunar Illumination, Perigee Proximity, Tidal Intensity, Solar/Earth
             Orbital Cosine, Earth Orbital Velocity vs. Sum, Parity, Primes, Spread).
          3. Target-Moment Regime Binomial Z-Score Number Resonance across 5 views:
             - Lunar Phase Window (|Δφ| <= 0.08 around target moon phase)
             - Lunar Syzygy / Tidal Band (matching tidal regime)
             - Earth/Solar Orbital Sector (|ΔDOY| <= 15 days around target orbit)
             - Hemisphere Season (matching target season)
             - Weekday Cycle (matching target weekday)
          4. Historical Twin Astronomical Moments (past draws where BOTH Earth's
             orbital position AND the Moon's synodic phase aligned with target_date).
        """
        import math
        from collections import Counter, defaultdict

        lo, hi = rules.number_range
        pool_size = max(1, hi - lo + 1)
        pick = rules.pick_count
        p_ball = pick / float(pool_size)
        q_ball = max(1e-9, 1.0 - p_ball)

        t_date = date.fromisoformat(target_date[:10]) if target_date else date.today()
        t_eph = cls().calculate_celestial_ephemeris(t_date, target_time=target_time or "20:00", coords=coords)
        t_lunar = ((t_date.toordinal() - 730125) % 29.530588853) / 29.530588853
        t_dist = (1.0 - math.cos(2.0 * math.pi * ((t_date.toordinal() - 730129) % 27.554551) / 27.554551)) / 2.0
        t_tide = 0.7 * ((math.cos(4.0 * math.pi * t_lunar) + 1.0) / 2.0) + 0.3 * (1.0 - t_dist)
        t_doy = t_date.timetuple().tm_yday
        t_weekday = t_date.weekday()
        t_season = t_eph["season"]
        southern_hemisphere = coords[0] < 0

        phase_names = [
            "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
            "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
        ]
        t_phase_idx = int(t_lunar * 8) % 8
        t_phase_label = phase_names[t_phase_idx]

        # Precompute primes in [lo..hi]
        def _is_prime(num: int) -> bool:
            if num < 2:
                return False
            for k in range(2, int(math.isqrt(num)) + 1):
                if num % k == 0:
                    return False
            return True

        primes_set = {n for n in range(lo, hi + 1) if _is_prime(n)}

        date_col = "date" if "date" in df.columns else ("draw_date" if "draw_date" in df.columns else None)
        if df.empty or date_col is None or "numbers" not in df.columns:
            return {"error": "insufficient dated draws"}

        # Collect per-draw records
        records: list[dict[str, Any]] = []
        phase_Macro: dict[str, list[dict[str, Any]]] = defaultdict(list)
        phase_num_counts: dict[str, Counter] = defaultdict(Counter)

        # Regime counters for Target-Moment Z-score views
        regimes = {
            "lunar_window": {"n": 0, "counts": Counter(), "label": f"Lunar Window ({t_phase_label}, φ={t_lunar:.1%})"},
            "tidal_regime": {"n": 0, "counts": Counter(), "label": f"Tidal Regime (Tide={t_tide:.0%})"},
            "orbital_sector": {"n": 0, "counts": Counter(), "label": f"Earth/Sun Orbit (λ☉={t_eph['sun_longitude_deg']:.1f}° / λ⊕={t_eph['earth_heliocentric_lon_deg']:.1f}°)"},
            "season_regime": {"n": 0, "counts": Counter(), "label": f"Season ({t_season})"},
            "weekday_cycle": {"n": 0, "counts": Counter(), "label": f"Weekday ({t_date.strftime('%A')})"},
        }
        twin_moments: list[dict[str, Any]] = []
        twin_counter: Counter = Counter()

        for _, row in df.iterrows():
            try:
                d_raw = row[date_col]
                d_obj = d_raw.date() if hasattr(d_raw, "date") else date.fromisoformat(str(d_raw)[:10])
                nums = [int(x) for x in row["numbers"] if lo <= int(x) <= hi]
                if not nums:
                    continue
            except Exception:
                continue

            l_ratio = ((d_obj.toordinal() - 730125) % 29.530588853) / 29.530588853
            p_idx = int(l_ratio * 8) % 8
            p_name = phase_names[p_idx]
            illum = (1.0 - math.cos(2.0 * math.pi * l_ratio)) / 2.0
            d_ratio = (1.0 - math.cos(2.0 * math.pi * ((d_obj.toordinal() - 730129) % 27.554551) / 27.554551)) / 2.0
            perigee_prox = 1.0 - d_ratio
            tide = 0.7 * ((math.cos(4.0 * math.pi * l_ratio) + 1.0) / 2.0) + 0.3 * perigee_prox

            doy = d_obj.timetuple().tm_yday
            # Approximate solar longitude & orbital velocity
            sun_lon_approx = (280.460 + 0.9856474 * (d_obj.toordinal() - 730120)) % 360.0
            mean_anom_rad = math.radians((357.528 + 0.9856003 * (d_obj.toordinal() - 730120)) % 360.0)
            r_au = 1.00014 - 0.01671 * math.cos(mean_anom_rad)
            v_orb = 29.7847 * math.sqrt(max(0.5, 2.0 / r_au - 1.0))

            s_quad = int(((sun_lon_approx + 90.0) % 360.0) // 90.0) % 4
            s_names_south = ["Summer", "Autumn", "Winter", "Spring"]
            s_names_north = ["Winter", "Spring", "Summer", "Autumn"]
            s_name = (s_names_south if southern_hemisphere else s_names_north)[s_quad]

            t_sum = float(sum(nums))
            odd_ratio = sum(1 for x in nums if x % 2 != 0) / float(len(nums))
            p_cnt = float(sum(1 for x in nums if x in primes_set))
            spread = float(max(nums) - min(nums)) if len(nums) > 1 else 0.0

            rec = {
                "draw_id": int(row["draw_id"]) if "draw_id" in row else 0,
                "date": d_obj.isoformat(),
                "nums": sorted(nums),
                "phase_name": p_name,
                "l_ratio": l_ratio,
                "illum": illum,
                "perigee_prox": perigee_prox,
                "tide": tide,
                "sun_lon_cos": math.cos(math.radians(sun_lon_approx)),
                "v_orb": v_orb,
                "sum": t_sum,
                "odd_ratio": odd_ratio,
                "primes": p_cnt,
                "spread": spread,
            }
            records.append(rec)
            phase_Macro[p_name].append(rec)
            phase_num_counts[p_name].update(nums)

            # Check target-moment regimes
            l_diff = abs(l_ratio - t_lunar)
            l_dist_circ = min(l_diff, 1.0 - l_diff)
            if l_dist_circ <= 0.08:
                regimes["lunar_window"]["n"] += 1
                regimes["lunar_window"]["counts"].update(nums)

            if abs(tide - t_tide) <= 0.15:
                regimes["tidal_regime"]["n"] += 1
                regimes["tidal_regime"]["counts"].update(nums)

            doy_diff = abs(doy - t_doy)
            orb_dist = min(doy_diff, 365.25 - doy_diff)
            if orb_dist <= 15.0:
                regimes["orbital_sector"]["n"] += 1
                regimes["orbital_sector"]["counts"].update(nums)

            if s_name == t_season:
                regimes["season_regime"]["n"] += 1
                regimes["season_regime"]["counts"].update(nums)

            if d_obj.weekday() == t_weekday:
                regimes["weekday_cycle"]["n"] += 1
                regimes["weekday_cycle"]["counts"].update(nums)

            # Twin astronomical moment: BOTH orbital (<= 15 days) AND lunar (<= 0.10)
            if orb_dist <= 15.0 and l_dist_circ <= 0.10:
                twin_moments.append({
                    "draw_id": rec["draw_id"],
                    "date": rec["date"],
                    "lunar_phase": f"{p_name} ({l_ratio:.0%})",
                    "sun_lon": round(sun_lon_approx, 1),
                    "numbers": rec["nums"],
                    "sum": int(t_sum),
                    "odd_count": int(sum(1 for x in nums if x % 2 != 0)),
                    "prime_count": int(p_cnt),
                    "spread": int(spread),
                })
                twin_counter.update(nums)

        if not records:
            return {"error": "no valid records"}

        all_sums = np.array([r["sum"] for r in records], dtype=float)
        grand_sum_mean = float(np.mean(all_sums))
        grand_sum_std = float(np.std(all_sums)) or 1.0

        # 1. Build 8-Phase Lunar Breakdown Table
        lunar_phase_table = []
        for p_name in phase_names:
            p_recs = phase_Macro.get(p_name, [])
            n_p = len(p_recs)
            if n_p == 0:
                continue
            m_sum = float(np.mean([r["sum"] for r in p_recs]))
            s_d = (m_sum - grand_sum_mean) / grand_sum_std
            m_odd = float(np.mean([r["odd_ratio"] for r in p_recs]))
            m_prm = float(np.mean([r["primes"] for r in p_recs]))

            exp_cnt = n_p * p_ball
            std_cnt = math.sqrt(max(1e-9, n_p * p_ball * q_ball))
            z_list = []
            for num in range(lo, hi + 1):
                obs = phase_num_counts[p_name].get(num, 0)
                z_val = (obs - exp_cnt) / std_cnt
                lift = ((obs / exp_cnt) - 1.0) * 100.0 if exp_cnt > 0 else 0.0
                z_list.append((num, obs, round(z_val, 2), round(lift, 1)))
            z_list.sort(key=lambda item: item[2], reverse=True)

            lunar_phase_table.append({
                "phase": p_name,
                "is_target": (p_name == t_phase_label),
                "n": n_p,
                "mean_sum": round(m_sum, 1),
                "sum_d": round(s_d, 2),
                "mean_odd_pct": round(m_odd * 100.0, 1),
                "mean_primes": round(m_prm, 2),
                "top_numbers": z_list[:5],
            })

        # 2. Continuous Pearson r & p-value Matrix
        from scipy import stats as _sp_stats

        metric_cols = [
            ("Lunar Illumination (0=New..1=Full)", "illum"),
            ("Lunar Perigee Proximity (0=Apogee..1=Perigee)", "perigee_prox"),
            ("Gravitational Tidal Intensity", "tide"),
            ("Solar/Earth Orbital Cosine", "sun_lon_cos"),
            ("Earth Orbital Velocity (km/s)", "v_orb"),
        ]
        struct_cols = [
            ("Ticket Sum", "sum"),
            ("Odd Parity Ratio", "odd_ratio"),
            ("Prime Count", "primes"),
            ("Number Spread", "spread"),
        ]
        continuous_correlations = []
        for m_label, m_key in metric_cols:
            x_arr = np.array([r[m_key] for r in records], dtype=float)
            row_corrs = {"metric": m_label, "correlations": {}}
            for s_label, s_key in struct_cols:
                y_arr = np.array([r[s_key] for r in records], dtype=float)
                if np.std(x_arr) > 1e-9 and np.std(y_arr) > 1e-9:
                    r_val, p_val = _sp_stats.pearsonr(x_arr, y_arr)
                else:
                    r_val, p_val = 0.0, 1.0
                row_corrs["correlations"][s_label] = {
                    "r": round(float(r_val), 4),
                    "p": round(float(p_val), 4),
                }
            continuous_correlations.append(row_corrs)

        # 3. Target-Moment Regime Binomial Z-Score Number Resonance
        metric_number_resonances = {}
        for r_key, r_data in regimes.items():
            n_r = r_data["n"]
            if n_r < 5:
                continue
            exp_r = n_r * p_ball
            std_r = math.sqrt(max(1e-9, n_r * p_ball * q_ball))
            z_map = {}
            ranked = []
            obs_vec = []
            for num in range(lo, hi + 1):
                obs = r_data["counts"].get(num, 0)
                obs_vec.append(obs)
                z_v = (obs - exp_r) / std_r
                lift_v = ((obs / exp_r) - 1.0) * 100.0 if exp_r > 0 else 0.0
                z_map[num] = round(z_v, 3)
                ranked.append((num, round(z_v, 2), round(lift_v, 1), obs, round(exp_r, 1)))
            ranked.sort(key=lambda x: x[1], reverse=True)
            exp_vec = [exp_r] * pool_size
            try:
                chi2_v, p_v = _sp_stats.chisquare(obs_vec, f_exp=exp_vec)
                chi2_f, p_f = round(float(chi2_v), 2), round(float(p_v), 4)
            except Exception:
                chi2_f, p_f = 0.0, 1.0
            metric_number_resonances[r_key] = {
                "label": r_data["label"],
                "n_draws": n_r,
                "chi2": chi2_f,
                "p_value": p_f,
                "top_positive_z": ranked[:8],
                "z_map": z_map,
            }

        # 4. Composite Multi-Correlation Convergence Score across all 5 views
        composite_z_ranking = []
        for num in range(lo, hi + 1):
            z_lun = metric_number_resonances.get("lunar_window", {}).get("z_map", {}).get(num, 0.0)
            z_tid = metric_number_resonances.get("tidal_regime", {}).get("z_map", {}).get(num, 0.0)
            z_orb = metric_number_resonances.get("orbital_sector", {}).get("z_map", {}).get(num, 0.0)
            z_sea = metric_number_resonances.get("season_regime", {}).get("z_map", {}).get(num, 0.0)
            z_wkd = metric_number_resonances.get("weekday_cycle", {}).get("z_map", {}).get(num, 0.0)
            # Weighted convergence favoring Lunar + Orbital + Tidal alignment
            z_comp = 0.30 * z_lun + 0.30 * z_orb + 0.15 * z_tid + 0.15 * z_sea + 0.10 * z_wkd
            composite_z_ranking.append({
                "number": num,
                "composite_z": round(z_comp, 3),
                "lunar_z": round(z_lun, 2),
                "orbital_z": round(z_orb, 2),
                "tidal_z": round(z_tid, 2),
                "season_z": round(z_sea, 2),
                "weekday_z": round(z_wkd, 2),
            })
        composite_z_ranking.sort(key=lambda item: item["composite_z"], reverse=True)

        twin_moments.sort(key=lambda r: r["date"], reverse=True)
        top_twin_numbers = [
            {"number": num, "count": cnt, "pct": round(cnt / max(1, len(twin_moments)) * 100.0, 1)}
            for num, cnt in twin_counter.most_common(12)
        ]

        # 5. Twin Period Co-Occurrence Pairs & Structural Sweet-Spot Envelope
        pair_counter: Counter[tuple[int, int]] = Counter()
        for tm in twin_moments:
            s_nums = sorted(tm["numbers"])
            for i_idx in range(len(s_nums)):
                for j_idx in range(i_idx + 1, len(s_nums)):
                    pair_counter[(s_nums[i_idx], s_nums[j_idx])] += 1

        top_twin_pairs = [
            {
                "pair": list(pair),
                "count": cnt,
                "pct": round(cnt / max(1, len(twin_moments)) * 100.0, 1),
            }
            for pair, cnt in pair_counter.most_common(10)
        ]

        if twin_moments:
            tm_sums = np.array([tm["sum"] for tm in twin_moments], dtype=float)
            tm_odds = np.array([tm["odd_count"] for tm in twin_moments], dtype=float)
            tm_prms = np.array([tm["prime_count"] for tm in twin_moments], dtype=float)
            tm_sprd = np.array([tm["spread"] for tm in twin_moments], dtype=float)
            twin_structural_envelope = {
                "sum_p25": round(float(np.percentile(tm_sums, 25)), 1),
                "sum_median": round(float(np.median(tm_sums)), 1),
                "sum_p75": round(float(np.percentile(tm_sums, 75)), 1),
                "mean_odds": round(float(np.mean(tm_odds)), 2),
                "mean_primes": round(float(np.mean(tm_prms)), 2),
                "mean_spread": round(float(np.mean(tm_sprd)), 1),
            }
        else:
            twin_structural_envelope = {}

        return {
            "target_date": t_date.isoformat(),
            "target_time": target_time or "20:00",
            "total_dated_draws": len(records),
            "target_phase_name": t_phase_label,
            "target_lunar_ratio": round(t_lunar, 4),
            "target_tide_intensity": round(t_tide, 4),
            "lunar_phase_table": lunar_phase_table,
            "continuous_correlations": continuous_correlations,
            "metric_number_resonances": metric_number_resonances,
            "composite_z_ranking": composite_z_ranking,
            "twin_moments_count": len(twin_moments),
            "twin_moments_recent": twin_moments[:10],
            "top_twin_numbers": top_twin_numbers,
            "top_twin_pairs": top_twin_pairs,
            "twin_structural_envelope": twin_structural_envelope,
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
