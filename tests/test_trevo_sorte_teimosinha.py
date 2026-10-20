from __future__ import annotations

from pathlib import Path
import pandas as pd
from typer.testing import CliRunner

from engine.adapters.br.mega_sena import MegaSenaAdapter
from engine.adapters.br.quina import QuinaAdapter
from engine.cli.main import app
from engine.modules import harmony
from engine.strategies import get_strategy
from engine.strategies.fun.trevo_sorte import compute_trevo_profile, get_lucky_number


# Synthetic test fixtures only (see docs/agents/pii-policy.md — never use real PII)
SYNTHETIC_BIRTH_DATE_LUCKY_7 = "2000-04-16"  # day 16 -> 1+6 = 7 (Lucky #7)
SYNTHETIC_DEFAULT_DATE = "1990-01-01"        # standard synthetic default


def _make_dummy_df(max_num: int, pick: int, n_draws: int = 80) -> pd.DataFrame:
    rows = []
    for i in range(1, n_draws + 1):
        nums = sorted([((i * 7 + j * 11) % max_num) + 1 for j in range(pick)])
        while len(set(nums)) < pick:
            for k in range(pick):
                if nums.count(nums[k]) > 1:
                    nums[k] = (nums[k] % max_num) + 1
            nums.sort()
        rows.append(
            {
                "draw_id": i,
                "date": pd.Timestamp("2026-01-01") + pd.Timedelta(days=i),
                "numbers": nums,
            }
        )
    return pd.DataFrame(rows)


def test_trevo_sorte_profile_synthetic():
    assert get_lucky_number(SYNTHETIC_BIRTH_DATE_LUCKY_7) == 7
    assert get_lucky_number(SYNTHETIC_DEFAULT_DATE) == 1
    profile = compute_trevo_profile(
        birth_date_str=SYNTHETIC_BIRTH_DATE_LUCKY_7,
        target_date_str="2026-10-20",
        teimosinha_draws=3,
        max_num=60,
        game_name="Mega-Sena",
    )
    assert profile["lucky_number"] == 7
    assert profile["sacred_weekday_pt"] == "Sábado"
    assert profile["lucky_days"] == [7, 16, 25]
    assert profile["lucky_months"] == [7, 4]
    assert 7 in profile["core_anchors"]
    assert 16 in profile["core_anchors"]
    assert any(d["is_sacred_weekday"] for d in profile["teimosinha_schedule"])


def test_quina_adapter_prize_tiers_and_harmony():
    rules = QuinaAdapter.rules
    assert rules.prize_tiers == [2, 3, 4, 5]
    assert rules.jackpot_odds == 24_040_016
    assert rules.odds[2] == 36
    assert rules.odds[3] == 866
    assert rules.odds[4] == 64_106

    # Pick-5 ticket with distinct differences (AC=6 >= 4) and 4-quadrant spread
    ticket = [7, 16, 29, 53, 78]
    assert harmony.registry.validate(
        ticket,
        rules,
        ["sum_range", "parity", "breadth", "ac_value", "quadrant_balance", "trevo_resonance"],
        birth_date=SYNTHETIC_BIRTH_DATE_LUCKY_7,
        target_date="2026-10-20",
    )


def test_trevo_sorte_strategy_and_ensemble_forwarding():
    df_mega = _make_dummy_df(60, 6, 80)
    strat = get_strategy(
        "trevo_sorte",
        birth_date=SYNTHETIC_BIRTH_DATE_LUCKY_7,
        target_date="2026-10-20",
        teimosinha_draws=3,
    )
    res = strat.suggest(
        df_mega,
        MegaSenaAdapter.rules,
        count=2,
        temperature=0.5,
        filters=["sum_range", "parity", "breadth", "ac_value", "quadrant_balance", "trevo_resonance"],
    )
    assert len(res.tickets) == 2
    for t in res.tickets:
        assert len(t) == 6

    ens = get_strategy(
        "voting:markov=0.5,trevo_sorte=0.5",
        birth_date=SYNTHETIC_BIRTH_DATE_LUCKY_7,
        target_date="2026-10-20",
        teimosinha_draws=3,
    )
    ens_scores = ens.score(df_mega, MegaSenaAdapter.rules)
    assert len(ens_scores) == 60
    assert ens_scores[7] > 0.0


def test_cli_suggest_returns_output():
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "suggest",
            "br/mega-sena",
            "--strategy",
            "trevo_sorte",
            "--birth-date",
            SYNTHETIC_DEFAULT_DATE,
            "--target-date",
            "2026-10-20",
            "--teimosinha",
            "3",
            "--count",
            "2",
        ],
    )
    assert result.exit_code == 0
    assert "Ticket 1:" in result.stdout
    assert "Teimosinha" in result.stdout


def test_pii_policy_files_exist():
    repo_root = Path(__file__).resolve().parent.parent
    agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    assert "PII" in agents_md
    assert (repo_root / "docs" / "agents" / "pii-policy.md").exists()
    assert (repo_root / ".agents" / "rules" / "no-pii.md").exists()
    assert (repo_root / "personal.example.yaml").exists()

    from scripts.check_no_pii import scan_repository

    violations = scan_repository(repo_root)
    assert violations == [], f"Found PII violations in repository: {violations}"

