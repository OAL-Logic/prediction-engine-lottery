"""
Unit and integration tests for the Interactive Portfolio Dashboard,
Combo-Play Simulation, and FastAPI REST endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient

from engine.adapters import DrawRules
from engine.cli.commands.expert_suggest import resolve_scenario_config, generate_html_dashboard, expert_suggest
from engine.api.main import app

client = TestClient(app)

def test_resolve_scenario_config():
    # Test LotoFácil budget tiers
    picks, count, cost, desc = resolve_scenario_config("br/lotofacil", 30.0)
    assert picks == 15
    assert count == 10
    assert cost == 30.0
    assert "Abbreviated Wheel" in desc

    picks, count, cost, desc = resolve_scenario_config("br/lotofacil", 60.0)
    assert picks == 16
    assert count == 1
    assert cost == 48.0
    assert "Premium Ticket" in desc

    picks, count, cost, desc = resolve_scenario_config("br/lotofacil", 150.0)
    assert picks == 15
    assert count == 33
    assert cost == 99.0
    assert "High-Coverage Wheel" in desc

    # Test Mega-Sena budget tiers
    picks, count, cost, desc = resolve_scenario_config("br/mega-sena", 20.0)
    assert picks == 6
    assert count == 4
    assert cost == 20.0

    picks, count, cost, desc = resolve_scenario_config("br/mega-sena", 50.0)
    assert picks == 7
    assert count == 1
    assert cost == 35.0

    picks, count, cost, desc = resolve_scenario_config("br/mega-sena", 120.0)
    assert picks == 6
    assert count == 18
    assert cost == 90.0

def test_generate_html_dashboard():
    stats = {
        "start_bankroll": 500.0,
        "total_spent": 100.0,
        "total_won": 40.0,
        "net_profit": -60.0,
        "roi": -60.0,
        "max_drawdown": 60.0
    }
    details = [
        {
            "lottery_id": "br/lotofacil",
            "draw_id": 3001,
            "date": "2026-05-20",
            "cost": 30.0,
            "winnings": 12.0,
            "bankroll": 482.0,
            "strategy": "spectral",
            "solar_kp": 3.5,
            "seismic_mag": 1.2
        }
    ]
    upcoming = {
        "br/lotofacil": {
            "strategy": "spectral",
            "limit": 50,
            "pool": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "missing": [1, 2],
            "tickets": [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
        }
    }
    
    html = generate_html_dashboard(
        title="Test Dashboard",
        bankroll_history=[500.0, 482.0],
        details_history=details,
        stats=stats,
        lotteries=["br/lotofacil"],
        upcoming_data=upcoming
    )
    
    assert "UNIVERSAL PORTFOLIO DASHBOARD" in html
    assert "br/lotofacil" in html.lower()
    assert "portfolioChart" in html
    assert "Outfit" in html

def test_expert_suggest_combo_smoke(tmp_path):
    # Smoke test running expert-suggest in combo mode and exporting html
    export_html_path = tmp_path / "dashboard.html"
    export_md_path = tmp_path / "report.md"
    
    # Run with small historical window (5 draws) to make it super fast
    try:
        expert_suggest(
            lottery="br/lotofacil,br/mega-sena",
            budget=100.0,
            draws=5,
            start_bankroll=200.0,
            export_md=str(export_md_path),
            export_html=str(export_html_path)
        )
        assert export_html_path.exists()
        assert export_md_path.exists()
        
        # Check generated HTML contains elements
        content = export_html_path.read_text()
        assert "UNIVERSAL PORTFOLIO DASHBOARD" in content
    except Exception as e:
        pytest.fail(f"expert_suggest combo simulation failed: {e}")

def test_api_sacred_manifold_endpoint():
    payload = {
        "numbers": [2, 3, 5, 7, 11, 13],
        "manifold": "sphere"
    }
    resp = client.post("/games/br/mega-sena/sacred-manifold", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["game"] == "br/mega-sena"
    assert data["manifold"] == "sphere"
    assert "coordinates" in data
    assert "center_of_mass" in data
    assert "resonance" in data
    assert "symmetry_grade" in data

def test_api_sacred_manifold_transits_endpoint():
    resp = client.get("/games/br/lotofacil/sacred-manifold/transits")
    assert resp.status_code == 200
    data = resp.json()
    assert data["game"] == "br/lotofacil"
    assert "celestial_angle" in data
    assert "solar_kp" in data
    assert "seismic_mag" in data

def test_api_expert_suggest_endpoint():
    payload = {
        "budget": 80.0,
        "draws": 10
    }
    resp = client.post("/games/br/lotofacil/expert-suggest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "started" in data["message"]
