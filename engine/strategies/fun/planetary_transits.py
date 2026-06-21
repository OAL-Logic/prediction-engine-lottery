"""
Planetary Transits Strategy 🪐
==============================
Calculates planetary positions (longitudes) and Placidus houses for the draw date
using high-precision Astropy (with a pure-Python Keplerian orbits fallback).

It scores numbers based on:
1. Modulo mapping of planetary degrees to the number pool.
2. Major astrological aspects (conjunction, trine, sextile, square, opposition).
3. Placidus house placements (especially 5th House amplification).
4. Blending with historical frequency of draws under the same planet-in-sign transits.
"""

from __future__ import annotations

from collections import Counter
import datetime
from datetime import date, timedelta
from typing import Any
import warnings
import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, SuggestionResult, register

# Silence Astropy warnings
try:
    from astropy.utils.exceptions import AstropyWarning
    warnings.simplefilter("ignore", category=AstropyWarning)
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

# Keplerian Elements (J2000)
# Body elements mapping: (a, a_dot, e, e_dot, i, i_dot, L, L_dot, w, w_dot, o, o_dot)
# Where angles are in degrees, distance in AU, and rates are per Julian Century.
KEPLER_ELEMENTS = {
    "sun": (1.00000011, -0.00000005, 0.01671022, -0.00003804, 0.00005, -0.01300, 100.46435, 36000.76983, 102.94719, 0.32327, -11.26064, -0.24119),
    "mercury": (0.38709893, 0.0, 0.20563069, 0.00002040, 7.00487, -0.00594, 252.25084, 149472.67411, 77.45645, 0.15940, 48.33167, -0.12534),
    "venus": (0.72333199, 0.0, 0.00677323, -0.00004776, 3.39471, -0.00077, 181.97973, 58517.81538, 131.53298, 0.00244, 76.68069, -0.27769),
    "mars": (1.52366231, 0.0, 0.09341233, 0.00011902, 1.85061, -0.00813, 355.45332, 19140.30268, 336.04084, 0.44388, 49.57854, -0.29250),
    "jupiter": (5.20336301, 0.00000202, 0.04839266, 0.00018002, 1.30530, -0.00415, 34.40438, 3034.74612, 14.75385, 0.21980, 100.55615, -0.19890),
    "saturn": (9.53707032, -0.00003067, 0.05415060, -0.00037394, 2.48446, -0.00373, 49.94432, 1222.49436, 92.43194, -0.36674, 113.71504, -0.23666),
    "uranus": (19.19126393, -0.00048335, 0.04716771, -0.00001915, 0.76986, -0.00242, 313.23218, 428.48202, 170.96424, 0.08833, 74.22988, -0.07020),
    "neptune": (30.06896348, 0.00028913, 0.00858587, 0.00009733, 1.76917, -0.00224, 304.88003, 218.45945, 44.97135, -0.32241, 131.72169, -0.16000),
    "pluto": (39.48168677, -0.00769788, 0.24880766, 0.00001127, 17.14175, -0.01187, 238.92881, 145.20780, 224.06676, -0.26000, 110.30347, -0.25000)
}

PLANET_INFO = {
    "sun":     ("Su", "☉", "yellow"),
    "moon":    ("Mo", "☽", "white"),
    "mercury": ("Me", "☿", "green"),
    "venus":   ("Ve", "♀", "magenta"),
    "mars":    ("Ma", "♂", "red"),
    "jupiter": ("Ju", "♃", "cyan"),
    "saturn":  ("Sa", "♄", "blue"),
    "uranus":  ("Ur", "♅", "bright_blue"),
    "neptune": ("Ne", "♆", "purple"),
    "pluto":   ("Pl", "♇", "red"),
}

# --- Sidereal Time, JD, and Keplerian helpers ---

def get_julian_date(dt: datetime.datetime) -> float:
    y, m, day = dt.year, dt.month, dt.day
    if m <= 2:
        y -= 1
        m += 12
    a = int(y / 100)
    b = 2 - a + int(a / 4)
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5
    ut = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    return jd + ut / 24.0

def get_obliquity(jd: float) -> float:
    T = (jd - 2451545.0) / 36525.0
    return 23.4392911 - 0.013004167 * T

def get_lst(jd: float, lon: float) -> float:
    T0 = (int(jd - 0.5) + 0.5 - 2451545.0) / 36525.0
    gmst_sec = (24110.54841 + 8640184.812866 * T0 + 0.093104 * T0**2 - 6.2e-6 * T0**3) % 86400.0
    gmst_deg0 = (gmst_sec / 240.0) % 360.0
    ut_hours = ((jd + 0.5) % 1.0) * 24.0
    gmst_deg = (gmst_deg0 + ut_hours * 15.041067178669) % 360.0
    return (gmst_deg + lon) % 360.0

def placidus_cusp(ramc_deg: float, lat_deg: float, obl_deg: float, offset_deg: float, factor: float, sign: float) -> float:
    ramc_rad = np.radians(ramc_deg)
    lat_rad = np.radians(lat_deg)
    obl_rad = np.radians(obl_deg)
    offset_rad = np.radians(offset_deg)
    
    ra = ramc_rad + offset_rad
    for _ in range(20):
        tan_delta = np.sin(ra) * np.tan(obl_rad)
        delta = np.arctan(tan_delta)
        sin_d = np.tan(lat_rad) * factor * np.tan(delta)
        sin_d = np.clip(sin_d, -1.0, 1.0)
        d = np.arcsin(sin_d)
        ra = ramc_rad + offset_rad + sign * d
        
    lon = np.degrees(np.arctan2(np.sin(ra), np.cos(ra) * np.cos(obl_rad))) % 360.0
    return lon

def get_kepler_longitude(body: str, dt: datetime.datetime) -> float:
    jd = get_julian_date(dt)
    T = (jd - 2451545.0) / 36525.0
    
    def solve_kepler(M, e):
        E = M
        for _ in range(15):
            E = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        return E
        
    def get_coords(name):
        params = KEPLER_ELEMENTS[name]
        a = params[0] + params[1] * T
        e = params[2] + params[3] * T
        i = np.radians(params[4] + params[5] * T)
        L = np.radians(params[6] + params[7] * T)
        w = np.radians(params[8] + params[9] * T)
        o = np.radians(params[10] + params[11] * T)
        
        M = L - w
        E = solve_kepler(M, e)
        xp = a * (np.cos(E) - e)
        yp = a * np.sqrt(1.0 - e**2) * np.sin(E)
        omega = w - o
        
        x = xp * (np.cos(omega)*np.cos(o) - np.sin(omega)*np.sin(o)*np.cos(i)) - yp * (np.sin(omega)*np.cos(o) + np.cos(omega)*np.sin(o)*np.cos(i))
        y = xp * (np.cos(omega)*np.sin(o) + np.sin(omega)*np.cos(o)*np.cos(i)) - yp * (np.sin(omega)*np.sin(o) - np.cos(omega)*np.cos(o)*np.cos(i))
        z = xp * (np.sin(omega)*np.sin(i)) + yp * (np.cos(omega)*np.sin(i))
        return x, y, z

    if body == "moon":
        L = np.radians(218.316 + 481267.8813 * T)
        M_moon = np.radians(134.963 + 477198.8675 * T)
        M_sun = np.radians(357.529 + 35999.0503 * T)
        D = np.radians(297.850 + 445267.1115 * T)
        lon_deg = np.degrees(L) + 6.289 * np.sin(M_moon) + 1.274 * np.sin(2*D - M_moon) + 0.658 * np.sin(2*D) - 0.186 * np.sin(M_sun)
        return lon_deg % 360.0

    xe, ye, ze = get_coords("sun")
    if body == "sun":
        return np.degrees(np.arctan2(-ye, -xe)) % 360.0
        
    xp, yp, zp = get_coords(body)
    xg = xp - xe
    yg = yp - ye
    return np.degrees(np.arctan2(yg, xg)) % 360.0

def get_positions_vectorized(dates: list[date], timezone_offset: float = -3.0) -> dict[str, np.ndarray]:
    jds = np.array([get_julian_date(datetime.datetime.combine(d, datetime.time(20, 0, 0)) - datetime.timedelta(hours=timezone_offset)) for d in dates])
    T = (jds - 2451545.0) / 36525.0
    
    positions_map = {}
    params_e = KEPLER_ELEMENTS["sun"]
    a_e = params_e[0] + params_e[1] * T
    e_e = params_e[2] + params_e[3] * T
    i_e = np.radians(params_e[4] + params_e[5] * T)
    L_e = np.radians(params_e[6] + params_e[7] * T)
    w_e = np.radians(params_e[8] + params_e[9] * T)
    o_e = np.radians(params_e[10] + params_e[11] * T)
    
    M_e = L_e - w_e
    E_e = M_e.copy()
    for _ in range(10):
        E_e = E_e - (E_e - e_e * np.sin(E_e) - M_e) / (1.0 - e_e * np.cos(E_e))
        
    xp_e = a_e * (np.cos(E_e) - e_e)
    yp_e = a_e * np.sqrt(1.0 - e_e**2) * np.sin(E_e)
    omega_e = w_e - o_e
    
    xe = xp_e * (np.cos(omega_e)*np.cos(o_e) - np.sin(omega_e)*np.sin(o_e)*np.cos(i_e)) - yp_e * (np.sin(omega_e)*np.cos(o_e) + np.cos(omega_e)*np.sin(o_e)*np.cos(i_e))
    ye = xp_e * (np.cos(omega_e)*np.sin(o_e) + np.sin(omega_e)*np.cos(o_e)*np.cos(i_e)) - yp_e * (np.sin(omega_e)*np.sin(o_e) - np.cos(omega_e)*np.cos(o_e)*np.cos(i_e))
    
    for body in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
        if body == "sun":
            positions_map[body] = np.degrees(np.arctan2(-ye, -xe)) % 360.0
        elif body == "moon":
            L = np.radians(218.316 + 481267.8813 * T)
            M_moon = np.radians(134.963 + 477198.8675 * T)
            M_sun = np.radians(357.529 + 35999.0503 * T)
            D = np.radians(297.850 + 445267.1115 * T)
            lon_deg = np.degrees(L) + 6.289 * np.sin(M_moon) + 1.274 * np.sin(2*D - M_moon) + 0.658 * np.sin(2*D) - 0.186 * np.sin(M_sun)
            positions_map[body] = lon_deg % 360.0
        else:
            params = KEPLER_ELEMENTS[body]
            a = params[0] + params[1] * T
            e = params[2] + params[3] * T
            i = np.radians(params[4] + params[5] * T)
            L = np.radians(params[6] + params[7] * T)
            w = np.radians(params[8] + params[9] * T)
            o = np.radians(params[10] + params[11] * T)
            
            M = L - w
            E = M.copy()
            for _ in range(10):
                E = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
                
            xp_p = a * (np.cos(E) - e)
            yp_p = a * np.sqrt(1.0 - e**2) * np.sin(E)
            omega_p = w - o
            
            xp = xp_p * (np.cos(omega_p)*np.cos(o) - np.sin(omega_p)*np.sin(o)*np.cos(i)) - yp_p * (np.sin(omega_p)*np.cos(o) + np.cos(omega_p)*np.sin(o)*np.cos(i))
            yp = xp_p * (np.cos(omega_p)*np.sin(o) + np.sin(omega_p)*np.cos(o)*np.cos(i)) - yp_p * (np.sin(omega_p)*np.sin(o) - np.cos(omega_p)*np.cos(o)*np.cos(i))
            
            xg = xp - xe
            yg = yp - ye
            positions_map[body] = np.degrees(np.arctan2(yg, xg)) % 360.0
            
    return positions_map

def get_timezone_offset(game_id: str, d: date) -> float:
    parts = game_id.split("/")
    country = parts[0] if len(parts) > 1 else "br"
    
    if country == "br":
        return -3.0
    elif country == "us":
        year = d.year
        march_1 = date(year, 3, 1)
        dst_start = date(year, 3, 14 - (march_1.weekday() + 1) % 7)
        nov_1 = date(year, 11, 1)
        dst_end = date(year, 11, 7 - (nov_1.weekday() + 1) % 7)
        if dst_start <= d < dst_end:
            return -4.0
        return -5.0
    elif country == "eu":
        year = d.year
        march_31 = date(year, 3, 31)
        dst_start = date(year, 3, 31 - (march_31.weekday() + 1) % 7)
        oct_31 = date(year, 10, 31)
        dst_end = date(year, 10, 31 - (oct_31.weekday() + 1) % 7)
        if dst_start <= d < dst_end:
            return 2.0
        return 1.0
    return 0.0

def make_ascii_wheel(planet_houses: dict[str, int]) -> str:
    house_planets = {h: [] for h in range(1, 13)}
    for body, h in planet_houses.items():
        name_short, sym, color = PLANET_INFO[body]
        house_planets[h].append(f"[{color}]{sym}{name_short}[/{color}]")
        
    h_labels = {}
    for h in range(1, 13):
        planets = house_planets[h]
        if planets:
            h_labels[f"h{h}"] = " ".join(planets)
        else:
            h_labels[f"h{h}"] = "."
            
    template = """
                      .--- 10 (MC): {h10} ---.
                   .-'        \\   |   /        `-.
                 .'   {h11}    \\  |  /    {h9}    `.
                /               \\ | /               \\
               ;   {h12}         \\|/         {h8}    :
     1 (ASC):  |-----------------[+]-----------------|  7 (DSC): {h7}
       {h1}    ;                 /|\\                 ;  {h6}
                \\    {h2}       / | \\       {h5}    /
                 `.            /  |  \\            .'
                   `-.        /   |   \\        .-'
                      `--- 4 (IC): {h4} ---'
                            {h3}
"""
    return template.format(**h_labels)

# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------

@register
class PlanetaryTransitsStrategy(BaseStrategy):
    name = "planetary_transits"
    description = "🪐 Planetary transits, aspects, and Placidus house mapping for the draw datetime"
    tier = "fun"
    requires_history = 30

    def __init__(self, draw_date: date | str | None = None) -> None:
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = draw_date or (date.today() + timedelta(days=1))
        self._correlation: dict[str, Any] = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        
        # Geographic coordinates from registry (fallback to Sao Paulo if missing)
        lat = getattr(rules, "draw_lat", -23.5505) or -23.5505
        lon = getattr(rules, "draw_lon", -46.6333) or -46.6333
        
        # Deduce timezone
        game_id = getattr(rules, "id", "br/mega-sena")
        timezone_offset = get_timezone_offset(game_id, self.draw_date)
        
        # UTC drawing date
        local_dt = datetime.datetime.combine(self.draw_date, datetime.time(20, 0, 0))
        utc_dt = local_dt - datetime.timedelta(hours=timezone_offset)
        jd = get_julian_date(utc_dt)
        obl = get_obliquity(jd)
        
        # Calculate sidereal RAMC
        if HAS_ASTROPY:
            from astropy.time import Time
            import astropy.units as u
            t = Time(utc_dt)
            lst = t.sidereal_time("mean", longitude=lon*u.deg)
            ramc = lst.degree
        else:
            ramc = get_lst(jd, lon)
            
        # Get Placidus House cusps
        cusps = [0.0] * 12
        ramc_rad = np.radians(ramc)
        obl_rad = np.radians(obl)
        mc = np.degrees(np.arctan2(np.sin(ramc_rad), np.cos(ramc_rad) * np.cos(obl_rad))) % 360.0
        lat_rad = np.radians(lat)
        denom = -np.sin(ramc_rad) * np.cos(obl_rad) - np.tan(lat_rad) * np.sin(obl_rad)
        asc = np.degrees(np.arctan2(np.cos(ramc_rad), denom)) % 360.0
        
        cusps[0] = asc
        cusps[9] = mc
        cusps[10] = placidus_cusp(ramc, lat, obl, 30, 1/3, 1)
        cusps[11] = placidus_cusp(ramc, lat, obl, 60, 2/3, 1)
        cusps[1] = placidus_cusp(ramc, lat, obl, 120, 2/3, -1)
        cusps[2] = placidus_cusp(ramc, lat, obl, 150, 1/3, -1)
        cusps[3] = (cusps[9] + 180.0) % 360.0
        cusps[4] = (cusps[10] + 180.0) % 360.0
        cusps[5] = (cusps[11] + 180.0) % 360.0
        cusps[6] = (cusps[0] + 180.0) % 360.0
        cusps[7] = (cusps[1] + 180.0) % 360.0
        cusps[8] = (cusps[2] + 180.0) % 360.0
        
        # Calculate planet positions
        positions = {}
        if HAS_ASTROPY:
            from astropy.time import Time
            from astropy.coordinates import get_body, GeocentricTrueEcliptic
            t = Time(utc_dt)
            for body in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]:
                try:
                    coord = get_body(body, t)
                    ecl = coord.transform_to(GeocentricTrueEcliptic())
                    positions[body] = float(ecl.lon.degree)
                except Exception:
                    positions[body] = get_kepler_longitude(body, utc_dt)
            positions["pluto"] = get_kepler_longitude("pluto", utc_dt)
        else:
            for body in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
                positions[body] = get_kepler_longitude(body, utc_dt)
                
        # Find which Placidus house each planet resides in
        planet_houses = {}
        for body, plon in positions.items():
            assigned_h = 1
            for h in range(12):
                c_start = cusps[h]
                c_end = cusps[(h + 1) % 12]
                if c_start < c_end:
                    if c_start <= plon < c_end:
                        assigned_h = h + 1
                        break
                else:
                    if plon >= c_start or plon < c_end:
                        assigned_h = h + 1
                        break
            planet_houses[body] = assigned_h
            
        # Calculate major aspects
        aspects = []
        bodies = list(positions.keys())
        aspect_types = [
            ("Conjunction", 0.0, 8.0, 1.0),
            ("Sextile", 60.0, 6.0, 0.4),
            ("Square", 90.0, 6.0, -0.5),
            ("Trine", 120.0, 6.0, 0.8),
            ("Opposition", 180.0, 8.0, -0.6),
        ]
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                b1 = bodies[i]
                b2 = bodies[j]
                lon1 = positions[b1]
                lon2 = positions[b2]
                diff = abs(lon1 - lon2) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff
                for name, angle, orb, val in aspect_types:
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            "body1": b1,
                            "body2": b2,
                            "aspect": name,
                            "angle": angle,
                            "exact_diff": diff,
                            "value": val,
                        })

        # Calculate base transit scores
        transit_scores = {num: 0.1 for num in all_numbers}
        for body, plon in positions.items():
            num = (int(plon) % pool) + lo
            # Boost direct planetary degrees
            transit_scores[num] = max(transit_scores[num], 0.7)
            # 5th House amplification
            if planet_houses[body] == 5:
                transit_scores[num] = max(transit_scores[num], 1.0)
                
        # Aspect overlays
        for aspect in aspects:
            b1 = aspect["body1"]
            b2 = aspect["body2"]
            val = aspect["value"]
            num1 = (int(positions[b1]) % pool) + lo
            num2 = (int(positions[b2]) % pool) + lo
            if val > 0:
                transit_scores[num1] = min(1.0, transit_scores[num1] + 0.1 * val)
                transit_scores[num2] = min(1.0, transit_scores[num2] + 0.1 * val)
            else:
                transit_scores[num1] = max(0.1, transit_scores[num1] + 0.05 * val)
                transit_scores[num2] = max(0.1, transit_scores[num2] + 0.05 * val)

        # Historical correlation
        historical_dates = []
        historical_numbers = []
        for _, row in df.iterrows():
            try:
                raw = row["date"]
                draw_date = raw.date() if hasattr(raw, "date") else date.fromisoformat(str(raw)[:10])
                historical_dates.append(draw_date)
                historical_numbers.append(row["numbers"])
            except Exception:
                continue

        if not historical_dates:
            return transit_scores

        # Vectorized historical calculations
        hist_positions = get_positions_vectorized(historical_dates, timezone_offset)
        hist_signs = {body: (pos // 30).astype(int) + 1 for body, pos in hist_positions.items()}
        target_signs = {body: int(plon // 30) + 1 for body, plon in positions.items()}

        number_counts = {num: 0 for num in all_numbers}
        total_matched_draws = 0
        
        for body in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
            target_sign = target_signs[body]
            body_signs = hist_signs[body]
            match_indices = np.where(body_signs == target_sign)[0]
            for idx in match_indices:
                nums = historical_numbers[idx]
                for n in nums:
                    if n in number_counts:
                        number_counts[n] += 1
                total_matched_draws += 1

        max_h = max(number_counts.values()) if number_counts.values() else 1.0
        hist_norm = {n: number_counts[n] / max_h for n in all_numbers}

        # Composite score
        final_scores = {}
        for n in all_numbers:
            final_scores[n] = 0.55 * transit_scores[n] + 0.45 * hist_norm.get(n, 0.0)

        # Format details
        top_numbers = [
            {"number": n, "frequency": number_counts.get(n, 0)}
            for n, _ in Counter(number_counts).most_common(10)
        ]
        
        self._correlation = {
            "placidus_wheel": make_ascii_wheel(planet_houses),
            "aspects_count": len(aspects),
            "matched_draws": total_matched_draws,
            "top_numbers": top_numbers,
        }
        
        return final_scores

    def suggest(self, *args, **kwargs) -> SuggestionResult:
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._correlation)
        return result
