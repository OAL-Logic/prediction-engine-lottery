"""
Test Suite for Embedded p4lottery Dual-Core, Budget Wheels & Storage Features
=============================================================================
Validates across >= 3 distinct game archetypes (Mega-Sena 6/60, Lotofácil 15/25,
Powerball 5/69+1/26, and 0-indexed Lotomania 20/100):
1. Deterministic astronomical and contextual calculations (zero PRNG drift).
2. Dual-Core Scoring Architecture (strict 80/20 ratio and [0.0, 1.0] bounds) & `dual_core` strategy.
3. Statistical pipeline (multi-horizon frequency, delays, universal quadrants, high-density recurrence).
4. Budget-constrained combinatorial wheel generation (`engine.wheels.budget_wheel`):
   - `reduce-coverage` (Uniform Reduction)
   - `reduce-pool` (Universe Reduction)
5. `LotteryStorage` precomputed wheel cache, multi-format ingestion (.csv/.json/.txt), and diagnostics.
6. End-to-end execution via the canonical `./p4lottery` CLI.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from engine.adapters import DrawRules
from engine.cli.utils import get_adapter
from engine.modules.dual_core import (
    DEFAULT_TARGET_ISO,
    ContextEngine,
    DualCoreScorer,
    StatisticalPipeline,
    get_quadrant,
)
from engine.modules.storage import LotteryStorage, PrecomputedWheel
from engine.strategies import get_strategy
from engine.wheels.budget_wheel import WheelEngine

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def mega_rules() -> DrawRules:
    return get_adapter("br/mega-sena").rules


@pytest.fixture
def loto_rules() -> DrawRules:
    return get_adapter("br/lotofacil").rules


@pytest.fixture
def powerball_rules() -> DrawRules:
    return get_adapter("us/powerball").rules


@pytest.fixture
def lotomania_rules() -> DrawRules:
    return DrawRules(
        name="Lotomania",
        number_range=(0, 99),
        pick_count=20,
        bonus_range=None,
        bonus_count=0,
        ticket_price=3.0,
        currency="BRL",
        board_cols=10,
    )


@pytest.fixture
def sample_history_mega() -> pd.DataFrame:
    """Synthetic fixture for Mega-Sena (6/60 sparse single-pool)."""
    base_numbers = [
        [5, 10, 15, 20, 25, 30],
        [1, 2, 3, 4, 5, 6],
        [7, 14, 21, 28, 35, 42],
        [11, 22, 33, 44, 55, 60],
        [10, 20, 30, 40, 50, 60],
        [2, 4, 6, 8, 10, 12],
        [1, 3, 5, 7, 9, 11],
        [13, 23, 33, 43, 53, 59],
        [18, 28, 38, 48, 58, 60],
        [6, 12, 18, 24, 30, 36],
        [9, 19, 29, 39, 49, 59],
        [4, 8, 16, 32, 48, 56],
        [15, 25, 35, 45, 55, 57],
        [14, 28, 34, 42, 50, 58],
        [7, 17, 27, 37, 47, 57],
        [3, 6, 9, 12, 15, 18],
        [21, 22, 23, 24, 25, 26],
        [31, 32, 33, 34, 35, 36],
        [41, 42, 43, 44, 45, 46],
        [6, 30, 32, 38, 49, 57],
    ]
    rows = [
        {"draw_id": idx, "date": f"2026-01-{idx:02d}", "numbers": nums, "bonus": []}
        for idx, nums in enumerate(base_numbers, 1)
    ]
    return pd.DataFrame(rows)


@pytest.fixture
def sample_history_loto() -> pd.DataFrame:
    """Synthetic fixture for Lotofácil (15/25 high-density single-pool)."""
    d1 = list(range(1, 16))
    rows = [{"draw_id": 1, "date": "2026-01-01", "numbers": d1, "bonus": []}]
    prev = d1
    for idx in range(2, 11):
        repeats = prev[:9]
        not_in_prev = [n for n in range(1, 26) if n not in prev]
        current = sorted(repeats + not_in_prev[:6])
        rows.append({"draw_id": idx, "date": f"2026-01-{idx:02d}", "numbers": current, "bonus": []})
        prev = current
    return pd.DataFrame(rows)


@pytest.fixture
def sample_history_powerball() -> pd.DataFrame:
    """Synthetic fixture for US Powerball (5/69 + 1/26 multi-pool)."""
    rows = []
    for idx in range(1, 16):
        nums = sorted([((idx * 7 + j * 11) % 69) + 1 for j in range(5)])
        # Ensure 5 distinct numbers
        while len(set(nums)) < 5:
            for cand in range(1, 70):
                if cand not in nums:
                    nums.append(cand)
                    break
            nums = sorted(set(nums))[:5]
        bonus = [(idx % 26) + 1]
        rows.append({"draw_id": idx, "date": f"2026-01-{idx:02d}", "numbers": nums, "bonus": bonus})
    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# 1. Context Engine Tests (including 0-indexed and multi-pool archetypes)
# -----------------------------------------------------------------------------

def test_context_engine_determinism(mega_rules, lotomania_rules):
    """Ensure context scores are 100% deterministic and support 0-based indexing."""
    ctx1 = ContextEngine(target_iso=DEFAULT_TARGET_ISO)
    ctx2 = ContextEngine(target_iso=DEFAULT_TARGET_ISO)

    scores1 = ctx1.generate_context_scores(mega_rules)
    scores2 = ctx2.generate_context_scores(mega_rules)
    assert scores1 == scores2
    assert len(scores1) == 60
    assert all(0.0 <= s <= 1.0 for s in scores1.values())

    # 0-indexed Lotomania (00..99)
    scores_0 = ctx1.generate_context_scores(lotomania_rules)
    assert 0 in scores_0 and 99 in scores_0
    assert len(scores_0) == 100
    assert all(0.0 <= s <= 1.0 for s in scores_0.values())


def test_context_engine_target_date_harmonics():
    """Verify astronomical calculations for October 29, 2026."""
    ctx = ContextEngine("2026-10-29T20:30:00-03:00")
    astro = ctx.astronomy
    assert astro.day_of_year == 302
    assert -20.0 <= astro.solar_declination_deg <= -10.0
    assert 0.0 <= astro.lunar_phase < 1.0
    assert 0.0 <= astro.lunar_illumination <= 1.0


# -----------------------------------------------------------------------------
# 2. Statistical Pipeline & Dual-Core Strategy Tests
# -----------------------------------------------------------------------------

def test_statistical_pipeline_and_dual_core_ratio(sample_history_mega, mega_rules):
    """Verify statistical fitness scores and strict 80/20 Dual-Core blend."""
    pipeline = StatisticalPipeline(sample_history_mega, mega_rules)
    s_stat = pipeline.compute_stat_scores()

    assert len(s_stat) == 60
    assert min(s_stat.values()) == 0.0
    assert max(s_stat.values()) == 1.0

    s_ctx = ContextEngine().generate_context_scores(mega_rules)
    composite = DualCoreScorer(s_stat, s_ctx).compute_composite_scores()

    for n in range(1, 61):
        expected = round(0.80 * s_stat[n] + 0.20 * s_ctx[n], 6)
        assert abs(composite[n] - expected) < 1e-5
        assert 0.0 <= composite[n] <= 1.0


def test_registered_dual_core_strategy_across_3_archetypes(
    sample_history_mega,
    sample_history_loto,
    sample_history_powerball,
    mega_rules,
    loto_rules,
    powerball_rules,
):
    """Verify the registered `dual_core` strategy across 3 distinct game archetypes."""
    strat = get_strategy("dual_core")

    res_mega = strat.suggest(sample_history_mega, mega_rules, count=2, temperature=0.0)
    assert len(res_mega.tickets) == 2
    assert all(len(t) == 6 for t in res_mega.tickets)

    res_loto = strat.suggest(sample_history_loto, loto_rules, count=2, temperature=0.0)
    assert len(res_loto.tickets) == 2
    assert all(len(t) == 15 for t in res_loto.tickets)

    res_pb = strat.suggest(sample_history_powerball, powerball_rules, count=2, temperature=0.0)
    assert len(res_pb.tickets) == 2
    assert all(len(t) == 5 for t in res_pb.tickets)
    assert len(res_pb.bonus_tickets) == 2
    assert all(len(b) == 1 and 1 <= b[0] <= 26 for b in res_pb.bonus_tickets)


def test_universal_quadrant_calculation(mega_rules, loto_rules, lotomania_rules):
    """Verify universal 4-quadrant spatial distribution via `rules.board_cols`."""
    assert get_quadrant(1, mega_rules) == 1
    assert get_quadrant(6, mega_rules) == 2
    assert get_quadrant(31, mega_rules) == 3
    assert get_quadrant(60, mega_rules) == 4

    assert get_quadrant(1, loto_rules) == 1
    assert get_quadrant(25, loto_rules) == 4

    assert get_quadrant(0, lotomania_rules) == 1
    assert get_quadrant(99, lotomania_rules) == 4


# -----------------------------------------------------------------------------
# 3. Budget-Constrained Wheels Across 3 Game Archetypes
# -----------------------------------------------------------------------------

def test_mega_sena_budget_wheels(sample_history_mega, mega_rules):
    """Test Mega-Sena reduce-coverage and reduce-pool within budget."""
    strat = get_strategy("dual_core")
    scores = strat.score(sample_history_mega, mega_rules)
    wheel_engine = WheelEngine(mega_rules)

    budget = mega_rules.ticket_price * 10
    res_cov = wheel_engine.generate_wheel(
        scores=scores,
        budget=budget,
        pool_size=12,
        guarantee_t=4,
        reduction_strategy="reduce-coverage",
    )
    assert len(res_cov.tickets) <= 10
    assert res_cov.audit.total_cost <= budget
    assert res_cov.audit.total_pool_v == 12
    assert res_cov.audit.coverage_percentage > 0.0

    res_pool = wheel_engine.generate_wheel(
        scores=scores,
        budget=budget,
        pool_size=12,
        guarantee_t=4,
        reduction_strategy="reduce-pool",
    )
    assert len(res_pool.tickets) <= 10
    assert res_pool.audit.total_cost <= budget
    assert res_pool.audit.coverage_percentage == 100.0
    assert res_pool.audit.is_100_percent_guarantee is True


def test_lotofacil_budget_wheels_recurrence(sample_history_loto, loto_rules):
    """Test Lotofácil high-density recurrence enforcement (8-10 repeats) and reduce-pool."""
    pipeline = StatisticalPipeline(sample_history_loto, loto_rules)
    s_stat = pipeline.compute_stat_scores()
    s_ctx = ContextEngine().generate_context_scores(loto_rules)
    scores = DualCoreScorer(s_stat, s_ctx).compute_composite_scores()

    wheel_engine = WheelEngine(loto_rules)
    budget = loto_rules.ticket_price * 16

    res_cov = wheel_engine.generate_wheel(
        scores=scores,
        budget=budget,
        pool_size=18,
        guarantee_t=13,
        reduction_strategy="reduce-coverage",
        last_draw=pipeline.last_draw,
    )
    assert len(res_cov.tickets) <= 16
    last_draw_set = set(pipeline.last_draw)
    for tkt in res_cov.tickets:
        assert len(tkt.numbers) == 15
        repeats = sum(1 for n in tkt.numbers if n in last_draw_set)
        assert 8 <= repeats <= 10

    res_pool = wheel_engine.generate_wheel(
        scores=scores,
        budget=budget,
        pool_size=18,
        guarantee_t=14,
        reduction_strategy="reduce-pool",
        last_draw=pipeline.last_draw,
    )
    assert res_pool.audit.is_100_percent_guarantee is True
    assert res_pool.audit.coverage_percentage == 100.0


def test_powerball_multi_pool_budget_wheel(sample_history_powerball, powerball_rules):
    """Test US Powerball (5/69 + 1/26) budget wheel with bonus ball assignment."""
    strat = get_strategy("dual_core")
    scores = strat.score(sample_history_powerball, powerball_rules)
    wheel_engine = WheelEngine(powerball_rules)

    res = wheel_engine.generate_wheel(
        scores=scores,
        budget=20.00,
        pool_size=9,
        guarantee_t=3,
        reduction_strategy="reduce-coverage",
    )
    assert len(res.tickets) <= 10
    assert res.audit.currency == "USD"
    for tkt in res.tickets:
        assert len(tkt.numbers) == 5
        assert len(tkt.bonus) == 1
        assert 1 <= tkt.bonus[0] <= 26


# -----------------------------------------------------------------------------
# 4. Storage Wheel Cache, Multi-Format Ingestion & Diagnostics Tests
# -----------------------------------------------------------------------------

def test_storage_wheel_cache_and_csv_ingestion(tmp_path, mega_rules):
    """Verify LotteryStorage wheel caching and CSV ingestion."""
    test_db = tmp_path / "test_storage.db"
    store = LotteryStorage(db_path=test_db)

    is_valid, msg = store.validate_environment("test/unseeded-game")
    assert is_valid is False
    assert "p4lottery fetch" in msg

    pw = PrecomputedWheel(
        lottery_id="br/mega-sena",
        v=8,
        k=6,
        t=4,
        m=6,
        ticket_count=4,
        tickets=[[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 6, 7], [0, 1, 4, 5, 6, 7], [2, 3, 4, 5, 6, 7]],
        theoretical_coverage=100.0,
    )
    store.save_precomputed_wheel(pw)
    fetched = store.get_precomputed_wheel("br/mega-sena", 8, 6, 4, 6)
    assert fetched is not None
    assert fetched.ticket_count == 4
    assert fetched.tickets == pw.tickets

    csv_file = tmp_path / "mega.csv"
    csv_file.write_text(
        "Concurso;Data;Bola1;Bola2;Bola3;Bola4;Bola5;Bola6\n"
        "1;11/03/1996;04;05;30;33;41;52\n"
        "2;18/03/1996;09;37;39;41;43;49\n",
        encoding="utf-8",
    )
    parsed = store.ingest_file(csv_file, lottery_id="br/mega-sena", rules=mega_rules, dry_run=True)
    assert len(parsed) == 2
    assert parsed[0]["draw_id"] == 1
    assert parsed[0]["numbers"] == [4, 5, 30, 33, 41, 52]


# -----------------------------------------------------------------------------
# 5. Canonical p4lottery CLI End-to-End Tests
# -----------------------------------------------------------------------------

def test_p4lottery_wheel_budget_cli(tmp_path):
    """Run canonical `./p4lottery wheel` with `--budget`, `--reduction-strategy`, and `--export`."""
    export_file = tmp_path / "lotofacil_wheel.json"
    launcher = PROJECT_ROOT / "p4lottery"
    cmd = [
        str(launcher),
        "wheel",
        "br/lotofacil",
        "--budget", "50.00",
        "--reduction-strategy", "reduce-pool",
        "--guarantee", "14",
        "--export", str(export_file),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    assert "Combinatorial Coverage & Financial Audit" in proc.stdout
    assert export_file.exists()

    data = json.loads(export_file.read_text(encoding="utf-8"))
    assert data["generator"] == "p4lottery"
    assert data["audit"]["is_100_percent_guarantee"] is True
    assert data["audit"]["total_cost"] <= 50.00


def test_p4lottery_omni_cli_reduce_coverage(tmp_path):
    """Run `./p4lottery omni` with reduce-coverage, target date, and JSON export."""
    export_file = tmp_path / "omni_mega_coverage.json"
    launcher = PROJECT_ROOT / "p4lottery"
    cmd = [
        str(launcher),
        "omni",
        "br/mega-sena",
        "--budget", "40.00",
        "--reduction-strategy", "reduce-coverage",
        "--target-date", "2026-10-29",
        "--export", str(export_file),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    assert "Auditoria Combinatória de Cobertura" in proc.stdout or "Coverage" in proc.stdout
    assert export_file.exists()

    payload = json.loads(export_file.read_text(encoding="utf-8"))
    assert payload["engine"] == "lottery-omni-generator"
    assert "coverage_audit" in payload
    assert "reduce-coverage" in payload["coverage_audit"]["reduction_strategy"]
    assert len(payload["tickets"]) > 0


def test_p4lottery_omni_cli_reduce_pool(tmp_path):
    """Run `./p4lottery omni` with reduce-pool guarantee."""
    export_file = tmp_path / "omni_mega_pool.json"
    launcher = PROJECT_ROOT / "p4lottery"
    cmd = [
        str(launcher),
        "omni",
        "br/mega-sena",
        "--budget", "40.00",
        "--reduction-strategy", "reduce-pool",
        "--target-date", "2026-10-29",
        "--export", str(export_file),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    assert proc.returncode == 0, f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
    assert export_file.exists()

    payload = json.loads(export_file.read_text(encoding="utf-8"))
    assert "reduce-pool" in payload["coverage_audit"]["reduction_strategy"]
    assert payload["coverage_audit"]["is_100_percent_guarantee"] is True


def test_p4lottery_news_cli():
    """Run multilingual `./p4lottery news` in both pt_br and en."""
    launcher = PROJECT_ROOT / "p4lottery"

    cmd_pt = [str(launcher), "news", "br/mega-sena", "--locale", "pt_br"]
    proc_pt = subprocess.run(cmd_pt, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    assert proc_pt.returncode == 0, f"STDOUT: {proc_pt.stdout}\nSTDERR: {proc_pt.stderr}"
    assert "Informativo Loterias Caixa" in proc_pt.stdout

    cmd_en = [str(launcher), "news", "br/mega-sena", "--locale", "en"]
    proc_en = subprocess.run(cmd_en, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    assert proc_en.returncode == 0, f"STDOUT: {proc_en.stdout}\nSTDERR: {proc_en.stderr}"
    assert "Astronomical Bulletin" in proc_en.stdout

