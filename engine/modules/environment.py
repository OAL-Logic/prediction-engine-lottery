"""
Astro-Cartography & Environmental OSINT Service 🌍🌌
===================================================
Provides high-precision planetary ecliptic data (using GeocentricTrueEcliptic)
and real-time environmental jitter via NOAA solar flux & USGS seismic feeds.
"""

from __future__ import annotations

import asyncio
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

try:
    import astropy.units as u
    from astropy.coordinates import AltAz, EarthLocation, GeocentricTrueEcliptic, SkyCoord, get_body, get_sun
    from astropy.time import Time
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False
    SkyCoord = EarthLocation = AltAz = get_sun = get_body = None
    GeocentricTrueEcliptic = None
    Time = None
    u = None


def calculate_great_circles(lat: float, lon: float, t: Any) -> Dict[str, float]:
    """Calculates the ecliptic longitudes of the four Great Circles:

    AC (Ascendant), MC (Midheaven), DC (Descendant), IC (Imum Coeli).
    """
    if not HAS_ASTROPY:
        return {"AC": 0, "MC": 0, "DC": 0, "IC": 0}

    # 1. Get Local Sidereal Time (LST)
    lst = t.sidereal_time("apparent", longitude=lon * u.deg).rad

    # 2. Get Obliquity of the Ecliptic (ε)
    epsilon = math.radians(23.4392911)
    phi = math.radians(lat)

    # 3. Calculate MC
    mc_rad = math.atan2(math.sin(lst), math.cos(lst) * math.cos(epsilon))
    mc_deg = math.degrees(mc_rad) % 360

    # 4. Calculate AC
    num = math.cos(lst)
    den = -(math.sin(epsilon) * math.tan(phi)) - (math.cos(epsilon) * math.sin(lst))
    ac_rad = math.atan2(num, den)
    ac_deg = math.degrees(ac_rad) % 360

    # 5. Calculate DC and IC
    dc_deg = (ac_deg + 180) % 360
    ic_deg = (mc_deg + 180) % 360

    return {
        "AC": round(ac_deg, 6),
        "MC": round(mc_deg, 6),
        "DC": round(dc_deg, 6),
        "IC": round(ic_deg, 6),
    }


def calculate_aspects(body_lons: Dict[str, float]) -> List[Dict[str, Any]]:
    """Calculates planetary aspects (Conjunction, Opposition, Trine, Square, Sextile)

    between all active celestial bodies.
    """
    aspects = []
    keys = list(body_lons.keys())
    
    aspect_defs = {
        "Conjunction": (0.0, 8.0),   # angle, orb tolerance
        "Opposition": (180.0, 8.0),
        "Trine": (120.0, 6.0),
        "Square": (90.0, 6.0),
        "Sextile": (60.0, 4.0),
    }

    for i in range(len(keys)):
        p1 = keys[i]
        lon1 = body_lons[p1]
        for j in range(i + 1, len(keys)):
            p2 = keys[j]
            lon2 = body_lons[p2]

            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            for aspect_name, (target, orb) in aspect_defs.items():
                if abs(diff - target) <= orb:
                    aspects.append({
                        "body1": p1,
                        "body2": p2,
                        "aspect": aspect_name,
                        "angle": round(diff, 2),
                        "orb": round(abs(diff - target), 2)
                    })
    return aspects


# Initialize FastMCP server
mcp = FastMCP("Astro-Expert") if FastMCP else None

CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "cache" / "env_jitter.json"


class EnvironmentalService:

    def __init__(self):
        self.client = httpx.Client(timeout=5.0)

    def fetch_solar_kp(self) -> float:
        """Fetches latest Planetary K-Index from NOAA."""
        try:
            url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
            resp = self.client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1:
                    latest = data[-1]
                    return float(latest[1])
        except Exception:
            pass
        return 3.0

    def fetch_solar_f107(self) -> float:
        """Fetches latest F10.7 Solar Flux Index from NOAA."""
        try:
            url = "https://services.swpc.noaa.gov/json/solar-cycle/f107.json"
            resp = self.client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, list):
                    latest = data[-1]
                    return float(latest.get("f107", 120.0))
        except Exception:
            pass
        return 120.0

    def fetch_seismic_mag(self) -> float:
        """Fetches max magnitude earthquake in the last hour from USGS."""
        try:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
            resp = self.client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if not features:
                    return 0.0
                mags = [
                    f["properties"]["mag"]
                    for f in features
                    if f["properties"]["mag"] is not None
                ]
                return max(mags) if mags else 0.0
        except Exception:
            pass
        return 0.0

    def get_jitter(self, force_refresh: bool = False) -> Dict[str, float]:
        if not force_refresh and CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r") as f:
                    cache_data = json.load(f)
                    if time.time() - cache_data["timestamp"] < 3600:
                        return cache_data["jitter"]
            except Exception:
                pass

        kp = self.fetch_solar_kp()
        f107 = self.fetch_solar_f107()
        mag = self.fetch_seismic_mag()

        j_solar = max(0.0, (kp - 4.0) * 0.05) + max(0.0, (f107 - 150.0) * 0.001)
        j_seismic = max(0.0, (mag - 5.0) * 0.1)

        jitter = {
            "kp": kp,
            "f107": f107,
            "seismic_mag": mag,
            "j_solar": round(j_solar, 3),
            "j_seismic": round(j_seismic, 3),
            "total_boost": round(j_solar + j_seismic, 3),
        }

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "jitter": jitter}, f)

        return jitter


# Conditional MCP registration
if mcp:

    @mcp.tool()
    async def get_planetary_resonance(
        latitude: float, longitude: float, timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculates active planetary Great Circle intersections (AC, MC, DC, IC)

        within a small angular radius of the specified location.
        """
        if not HAS_ASTROPY:
            return {"status": "error", "message": "astropy not installed"}

        t = Time(timestamp) if timestamp else Time.now()

        # 1. Calculate Great Circles at this location
        angles = calculate_great_circles(latitude, longitude, t)

        # 2. Get high-precision body positions in GeocentricTrueEcliptic coords
        bodies = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
        ]
        body_lons = {}
        intersections = []

        for body_name in bodies:
            body = get_body(body_name, t)
            # High-fidelity ecliptic longitude transformation
            ecliptic_coord = body.transform_to(GeocentricTrueEcliptic())
            lon = ecliptic_coord.lon.deg
            body_lons[body_name] = lon

            for name, angle in angles.items():
                diff = abs(lon - angle) % 360
                if diff > 180:
                    diff = 360 - diff

                # Orb threshold: 3 degrees for high-resonance
                if diff < 3.0:
                    intersections.append(
                        {
                            "body": body_name,
                            "point": name,
                            "angle": round(angle, 4),
                            "body_lon": round(lon, 4),
                            "orb": round(diff, 4),
                        }
                    )

        # Calculate interplanetary aspects
        aspects = calculate_aspects(body_lons)

        return {
            "location": {"lat": latitude, "lon": longitude},
            "timestamp": t.iso,
            "great_circles": angles,
            "body_longitudes": {k: round(v, 4) for k, v in body_lons.items()},
            "intersections": intersections,
            "aspects": aspects,
            "status": "ready",
        }

    @mcp.resource("astro://current_cosmic_context")
    def get_current_cosmic_context() -> str:
        """Provides a summary of current planetary positions and active OSINT jitter."""
        service = EnvironmentalService()
        jitter = service.get_jitter()

        if not HAS_ASTROPY:
            return json.dumps(
                {"status": "error", "message": "astropy not installed", "jitter": jitter}
            )

        t = Time.now()
        sun = get_body("sun", t).transform_to(GeocentricTrueEcliptic())
        moon = get_body("moon", t).transform_to(GeocentricTrueEcliptic())

        return json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "jitter": jitter,
                "cosmic": {
                    "sun_lon": round(sun.lon.deg, 4),
                    "moon_lon": round(moon.lon.deg, 4),
                },
                "summary": f"Solar Kp: {jitter['kp']}, Solar Flux: {jitter['f107']}, Seismic: {jitter['seismic_mag']}. Ecliptic alignment active.",
            },
            indent=2,
        )


def calculate_environmental_jitter() -> float:
    service = EnvironmentalService()
    jitter = service.get_jitter()
    return jitter["total_boost"]
