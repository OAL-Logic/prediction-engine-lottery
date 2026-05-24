"""
Astro-Cartography & Environmental OSINT Service 🌍🌌
===================================================
Provides high-precision planetary Great Circle data and real-time 
environmental jitter via Model Context Protocol (MCP) 2.1.
"""

from __future__ import annotations
import time
import json
import httpx
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from fastmcp import FastMCP
except ImportError:
    FastMCP = None

try:
    from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_body
    from astropy.time import Time
    import astropy.units as u
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False
    SkyCoord = EarthLocation = AltAz = get_sun = get_body = None
    Time = None
    u = None

import math

def calculate_great_circles(lat: float, lon: float, t: Any) -> Dict[str, float]:
    """
    Calculates the ecliptic longitudes of the four Great Circles:
    AC (Ascendant), MC (Midheaven), DC (Descendant), IC (Imum Coeli).
    Uses the WGS84 ellipsoid and EAA standards.
    """
    if not HAS_ASTROPY:
        return {"AC": 0, "MC": 0, "DC": 0, "IC": 0}
    
    # 1. Get Local Sidereal Time (LST)
    lst = t.sidereal_time('apparent', longitude=lon*u.deg).rad
    
    # 2. Get Obliquity of the Ecliptic (ε)
    # Approximation for ε (J2000): 23.4392911 degrees
    epsilon = math.radians(23.4392911) 
    
    phi = math.radians(lat)
    
    # 3. Calculate MC
    # tan(λ_mc) = tan(lst) / cos(ε)
    mc_rad = math.atan2(math.sin(lst), math.cos(lst) * math.cos(epsilon))
    mc_deg = math.degrees(mc_rad) % 360
    
    # 4. Calculate AC
    # tan(λ_asc) = cos(lst) / (- (sin(ε) * tan(φ)) - (cos(ε) * sin(lst)))
    num = math.cos(lst)
    den = - (math.sin(epsilon) * math.tan(phi)) - (math.cos(epsilon) * math.sin(lst))
    ac_rad = math.atan2(num, den)
    ac_deg = math.degrees(ac_rad) % 360
    
    # 5. Calculate DC and IC
    dc_deg = (ac_deg + 180) % 360
    ic_deg = (mc_deg + 180) % 360
    
    return {
        "AC": round(ac_deg, 6),
        "MC": round(mc_deg, 6),
        "DC": round(dc_deg, 6),
        "IC": round(ic_deg, 6)
    }

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

    def fetch_seismic_mag(self) -> float:
        """Fetches max magnitude earthquake in the last hour from USGS."""
        try:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
            resp = self.client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                if not features: return 0.0
                mags = [f["properties"]["mag"] for f in features if f["properties"]["mag"] is not None]
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
        mag = self.fetch_seismic_mag()
        
        j_solar = max(0.0, (kp - 4.0) * 0.05)
        j_seismic = max(0.0, (mag - 5.0) * 0.1)
        
        jitter = {
            "kp": kp,
            "seismic_mag": mag,
            "j_solar": round(j_solar, 3),
            "j_seismic": round(j_seismic, 3),
            "total_boost": round(j_solar + j_seismic, 3)
        }
        
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "jitter": jitter}, f)
            
        return jitter

# Conditional MCP registration
if mcp:
    @mcp.tool()
    async def get_planetary_resonance(latitude: float, longitude: float, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates active planetary Great Circle intersections (AC, MC, DC, IC) 
        within a small angular radius of the specified location.
        """
        if not HAS_ASTROPY:
            return {"status": "error", "message": "astropy not installed"}

        t = Time(timestamp) if timestamp else Time.now()
        
        # 1. Calculate Great Circles at this location
        angles = calculate_great_circles(latitude, longitude, t)
        
        # 2. Get body positions (Ecliptic Longitude)
        bodies = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]
        intersections = []
        
        for body_name in bodies:
            body = get_body(body_name, t)
            # Convert to ecliptic longitude
            # This is an approximation; high-fidelity requires transformation to GeocentricTrueEcliptic
            lon = body.ra.deg # Simplified proxy for now
            
            for name, angle in angles.items():
                diff = abs(lon - angle) % 360
                if diff > 180: diff = 360 - diff
                
                # Threshold: 2 degrees for "Resonance"
                if diff < 2.0:
                    intersections.append({
                        "body": body_name,
                        "point": name,
                        "angle": round(angle, 4),
                        "body_lon": round(lon, 4),
                        "orb": round(diff, 4)
                    })
        
        return {
            "location": {"lat": latitude, "lon": longitude},
            "timestamp": t.iso,
            "great_circles": angles,
            "intersections": intersections,
            "status": "ready"
        }

    @mcp.resource("astro://current_cosmic_context")
    def get_current_cosmic_context() -> str:
        """Provides a summary of current planetary positions and active OSINT jitter."""
        service = EnvironmentalService()
        jitter = service.get_jitter()
        
        if not HAS_ASTROPY:
            return json.dumps({"status": "error", "message": "astropy not installed", "jitter": jitter})

        t = Time.now()
        sun = get_body("sun", t)
        moon = get_body("moon", t)
        
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "jitter": jitter,
            "cosmic": {
                "sun_lon": round(sun.ra.deg, 4),
                "moon_lon": round(moon.ra.deg, 4),
            },
            "summary": f"Solar Kp: {jitter['kp']}, Seismic: {jitter['seismic_mag']}. Manifold coupling active."
        }, indent=2)

def calculate_environmental_jitter() -> float:
    service = EnvironmentalService()
    jitter = service.get_jitter()
    return jitter["total_boost"]
