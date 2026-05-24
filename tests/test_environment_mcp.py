import pytest
import json
from pathlib import Path
from astropy.time import Time
from engine.modules.environment import mcp, calculate_great_circles

KGV_FILE = Path(__file__).parent / "factory" / "astro_kgv.json"

@pytest.mark.asyncio
async def test_mcp_server_exists():
    assert mcp is not None
    assert mcp.name == "Astro-Expert"

@pytest.mark.asyncio
async def test_mcp_tools_registered():
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_planetary_resonance" in tool_names

@pytest.mark.asyncio
async def test_mcp_resources_registered():
    resources = await mcp.list_resources()
    resource_uris = [str(r.uri) for r in resources]
    assert "astro://current_cosmic_context" in resource_uris

def test_great_circle_accuracy():
    with open(KGV_FILE, "r") as f:
        kgvs = json.load(f)
    
    for name, kgv in kgvs.items():
        t = Time(kgv["time"])
        result = calculate_great_circles(kgv["lat"], kgv["lon"], t)
        
        for point, expected_val in kgv["expected"].items():
            assert result[point] == pytest.approx(expected_val, abs=1e-5)
