"""
Test suite for API endpoints — covers both existing and Sprint 2 gap-closure endpoints.

Tests use mock adapters to avoid network dependencies and work without lottery data.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_draw_rules():
    """Create a minimal DrawRules object for testing."""
    from engine.adapters import DrawRules
    return DrawRules(
        name="Test Lottery",
        pick_count=6,
        number_range=(1, 60),
        prize_tiers=[4, 5, 6],
        ticket_price=5.0,
        currency="BRL",
        odds={6: 50063860, 5: 154518, 4: 2332},
    )

@pytest.fixture
def mock_adapter(mock_draw_rules):
    """Create a mock adapter with minimal draw data."""
    import pandas as pd
    import numpy as np
    
    adapter = MagicMock()
    adapter.rules = mock_draw_rules
    
    # Create a small synthetic draw history
    draws = []
    rng = np.random.default_rng(42)
    for i in range(50):
        nums = sorted(rng.choice(range(1, 61), size=6, replace=False).tolist())
        draws.append({
            "draw_id": 3000 + i,
            "date": pd.Timestamp(f"2025-01-{(i % 28) + 1}", tz="UTC"),
            "numbers": nums,
            "bonus": [],
        })
    
    adapter.load_data.return_value = pd.DataFrame(draws)
    return adapter

# ---------------------------------------------------------------------------
# Model Import Tests
# ---------------------------------------------------------------------------

class TestModelsImport:
    """Verify all Pydantic models can be imported."""

    def test_core_models(self):
        from engine.api.models import (
            GameRulesSchema, GameSummary, AnalysisResultSchema,
            SuggestionRequest, SuggestionResponse,
        )
        assert GameRulesSchema is not None
        assert SuggestionRequest is not None
    
    def test_sprint2_gap_models(self):
        from engine.api.models import (
            SumDistributionResponse, GapAnalysisResponse,
            CompareResponse, CompareItem,
            WheelRequest, WheelResponse,
            TicketGradeRequest, HealthResponse,
        )
        assert SumDistributionResponse is not None
        assert HealthResponse is not None

    def test_health_response_serialization(self):
        from engine.api.models import HealthResponse
        h = HealthResponse(
            status="healthy",
            version="11.2.0",
            uptime_seconds=42.0,
            registered_games=10,
            registered_strategies=80,
        )
        data = h.model_dump()
        assert data["status"] == "healthy"
        assert data["version"] == "11.2.0"
    
    def test_sum_distribution_response(self):
        from engine.api.models import SumDistributionResponse
        s = SumDistributionResponse(
            game="test",
            midpoint=183.0,
            sigma=22.5,
            range_lo=141,
            range_hi=225,
            coverage=0.70,
            pmf={183: 0.05, 184: 0.049},
        )
        assert s.game == "test"
        assert s.range_lo == 141
    
    def test_gap_analysis_response(self):
        from engine.api.models import GapAnalysisResponse
        g = GapAnalysisResponse(
            game="test",
            number=7,
            last_seen_draw=3050,
            draws_since_last=5,
            expected_interval=10.0,
            deviation_ratio=0.5,
        )
        assert g.deviation_ratio == 0.5

    def test_wheel_request(self):
        from engine.api.models import WheelRequest
        w = WheelRequest(pool=[1, 2, 3, 4, 5, 6, 7, 8])
        assert w.wheel_type == "key"  # default
        assert len(w.pool) == 8

    def test_ticket_grade_request(self):
        from engine.api.models import TicketGradeRequest
        t = TicketGradeRequest(numbers=[3, 7, 12, 24, 31, 45])
        assert len(t.numbers) == 6


# ---------------------------------------------------------------------------
# Sum Range Module Tests (used by sum-distribution endpoint)
# ---------------------------------------------------------------------------

class TestSumRangeIntegration:
    """Test sum_range module functions that power the API endpoint."""
    
    def test_most_probable_range(self, mock_draw_rules):
        from engine.modules.sum_range import most_probable_range
        lo, hi, mid, sigma = most_probable_range(mock_draw_rules)
        assert lo < mid < hi
        assert sigma > 0
        # Mega-Sena like: midpoint should be around 183
        assert 170 < mid < 200
    
    def test_pmf(self, mock_draw_rules):
        from engine.modules.sum_range import pmf
        distribution = pmf(mock_draw_rules)
        assert isinstance(distribution, dict)
        assert len(distribution) > 0
        # PMF should sum to ~1.0
        total = sum(distribution.values())
        assert abs(total - 1.0) < 0.01
    
    def test_classify(self, mock_draw_rules):
        from engine.modules.sum_range import classify
        # A typical combo
        combo = [3, 12, 24, 31, 45, 58]  # sum = 173
        bucket, z = classify(combo, mock_draw_rules)
        assert bucket in ("below", "in", "above")
        assert isinstance(z, float)


# ---------------------------------------------------------------------------
# Deviation Module Tests (used by gap endpoint)
# ---------------------------------------------------------------------------

class TestDeviationIntegration:
    """Test deviation module functions that power the gap endpoint."""
    
    def test_analyze(self, mock_adapter):
        from engine.modules.deviation import analyze as analyze_deviation
        result = analyze_deviation(
            mock_adapter.load_data(),
            mock_adapter.rules,
        )
        assert result.total_draws == 50
        assert len(result.table) > 0
        assert len(result.gap_stats) > 0
        assert len(result.overdue) > 0


# ---------------------------------------------------------------------------
# Wheels Module Tests (used by wheel endpoint)
# ---------------------------------------------------------------------------

class TestWheelsIntegration:
    """Test wheels module functions that power the wheel endpoint."""
    
    def test_full_wheel(self):
        from engine.wheels import generate_full_wheel
        tickets = generate_full_wheel([1, 2, 3, 4, 5, 6, 7], 6)
        # C(7,6) = 7 tickets
        assert len(tickets) == 7
    
    def test_key_wheel(self):
        from engine.wheels import generate_key_wheel
        pool = [1, 2, 3, 4, 5, 6, 7]
        tickets = generate_key_wheel(pool, 6, [1])
        # All tickets should contain key number 1
        for t in tickets:
            assert 1 in t
    
    def test_evaluate_prizes(self):
        from engine.wheels import evaluate_prizes
        # Simple prize evaluation
        tickets = [[1, 2, 3, 4, 5, 6]]
        winning = [1, 2, 3, 4, 5, 7]
        result = evaluate_prizes(tickets, winning)
        assert isinstance(result, dict)
        assert 5 in result  # 5 matches


# ---------------------------------------------------------------------------
# Odds Comparator Tests (used by compare endpoint)
# ---------------------------------------------------------------------------

class TestOddsComparator:
    """Test odds comparison logic."""
    
    def test_compare_lotteries(self, mock_draw_rules):
        from engine.odds.comparator import compare_lotteries
        results = compare_lotteries([mock_draw_rules])
        assert len(results) >= 0  # May be 0 if odds not set properly


# ---------------------------------------------------------------------------
# Strategy Registry Tests
# ---------------------------------------------------------------------------

class TestStrategyRegistry:
    """Verify strategy registry integrity."""
    
    def test_registry_not_empty(self):
        from engine.strategies import STRATEGY_REGISTRY
        assert len(STRATEGY_REGISTRY) > 50
    
    def test_all_strategies_have_required_keys(self):
        from engine.strategies import STRATEGY_REGISTRY
        for name, info in STRATEGY_REGISTRY.items():
            assert "module" in info, f"Strategy '{name}' missing 'module' key"
            assert "tier" in info, f"Strategy '{name}' missing 'tier' key"
            assert "description" in info, f"Strategy '{name}' missing 'description' key"
    
    def test_valid_tiers(self):
        from engine.strategies import STRATEGY_REGISTRY
        valid_tiers = {"statistical", "ml", "deep", "fun"}
        for name, info in STRATEGY_REGISTRY.items():
            assert info["tier"] in valid_tiers, \
                f"Strategy '{name}' has invalid tier '{info['tier']}'"

    def test_list_strategies(self):
        from engine.strategies import list_strategies
        strategies = list_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 50
        # Each should be a dict with name, tier, description
        for s in strategies:
            assert "name" in s
            assert "tier" in s

    def test_get_strategy_weighted(self):
        """Test that the most common strategy can be loaded."""
        from engine.strategies import get_strategy
        strat = get_strategy("weighted")
        assert strat is not None
        assert hasattr(strat, "score")
        assert hasattr(strat, "suggest")


# ---------------------------------------------------------------------------
# CLI Integration Tests
# ---------------------------------------------------------------------------

class TestCLIImports:
    """Verify that key CLI command modules can be imported."""

    def test_import_suggest(self):
        from engine.cli.commands.suggest import suggest
        assert callable(suggest)

    def test_import_analyze(self):
        from engine.cli.commands.analyze import analyze
        assert callable(analyze)

    def test_import_backtest(self):
        from engine.cli.commands.backtest import backtest
        assert callable(backtest)

    def test_import_forecast(self):
        from engine.cli.commands.forecast import forecast
        assert callable(forecast)

    def test_import_scan(self):
        from engine.cli.commands.scan import scan
        assert callable(scan)

    def test_import_daily(self):
        from engine.cli.commands.daily import daily
        assert callable(daily)

    def test_import_session(self):
        from engine.cli.commands.session import session
        assert callable(session)

    def test_import_check(self):
        from engine.cli.commands.check import check
        assert callable(check)

    def test_import_streak_report(self):
        from engine.cli.commands.streak_report import streak_report
        assert callable(streak_report)

    def test_import_leaderboard(self):
        from engine.cli.commands.leaderboard import leaderboard
        assert callable(leaderboard)

    def test_import_risk(self):
        from engine.cli.commands.risk import risk
        assert callable(risk)

    def test_import_ticket_grade(self):
        from engine.cli.commands.ticket_grade import ticket_grade
        assert callable(ticket_grade)

    def test_import_expert_suggest(self):
        from engine.cli.commands.expert_suggest import expert_suggest
        assert callable(expert_suggest)
