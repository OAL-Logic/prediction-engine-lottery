"""
Tests for Continuous Popperian Falsification Audit Script (`scripts/audit_fringe_theories.py`).
"""

import math
import random
import pytest

from engine.adapters import DrawRules
from scripts.audit_fringe_theories import (
    calculate_arithmetic_complexity,
    generate_uniform_ticket,
    generate_orthodox_ticket,
    compute_hypergeometric_probabilities,
    audit_game,
    main,
    parse_args,
)


def test_calculate_arithmetic_complexity():
    # Consecutive numbers have identical differences: AC is minimal (0)
    comb_min = [1, 2, 3, 4, 5, 6]
    assert calculate_arithmetic_complexity(comb_min) == 0

    # High complexity ticket with mostly unique differences
    comb_high = [4, 15, 23, 38, 47, 59]
    ac = calculate_arithmetic_complexity(comb_high)
    assert ac >= 6

    # Edge cases
    assert calculate_arithmetic_complexity([]) == 0
    assert calculate_arithmetic_complexity([1, 2]) == 0


def test_generate_uniform_ticket():
    rules = DrawRules("Mega-Sena", 6, (1, 60))
    rng = random.Random(42)
    ticket = generate_uniform_ticket(rules, rng)
    assert len(ticket) == 6
    assert len(set(ticket)) == 6
    assert all(1 <= n <= 60 for n in ticket)
    assert ticket == sorted(ticket)


def test_generate_orthodox_ticket_mega_sena():
    rules = DrawRules("Mega-Sena", 6, (1, 60))
    rng = random.Random(123)
    ticket = generate_orthodox_ticket(rules, rng)
    assert len(ticket) == 6
    assert 121 <= sum(ticket) <= 296
    evens = sum(1 for x in ticket if x % 2 == 0)
    assert 2 <= evens <= 4
    ac = calculate_arithmetic_complexity(ticket)
    assert 6 <= ac <= 10


def test_generate_orthodox_ticket_lotofacil():
    rules = DrawRules("Lotofácil", 15, (1, 25))
    rng = random.Random(456)
    ticket = generate_orthodox_ticket(rules, rng)
    assert len(ticket) == 15
    assert 160 <= sum(ticket) <= 220
    evens = sum(1 for x in ticket if x % 2 == 0)
    assert 6 <= evens <= 9
    ac = calculate_arithmetic_complexity(ticket)
    assert ac >= 4


def test_compute_hypergeometric_probabilities():
    # Mega-Sena: 6/60
    probs_mega = compute_hypergeometric_probabilities(60, 6)
    assert len(probs_mega) == 7
    assert pytest.approx(sum(probs_mega), rel=1e-5) == 1.0
    exp_mega = sum(x * p for x, p in enumerate(probs_mega))
    assert pytest.approx(exp_mega, rel=1e-5) == 0.6000

    # Quina: 5/80
    probs_quina = compute_hypergeometric_probabilities(80, 5)
    assert len(probs_quina) == 6
    assert pytest.approx(sum(probs_quina), rel=1e-5) == 1.0
    exp_quina = sum(x * p for x, p in enumerate(probs_quina))
    assert pytest.approx(exp_quina, rel=1e-5) == 0.3125

    # Lotofácil: 15/25
    probs_loto = compute_hypergeometric_probabilities(25, 15)
    assert len(probs_loto) == 16
    assert pytest.approx(sum(probs_loto), rel=1e-5) == 1.0
    exp_loto = sum(x * p for x, p in enumerate(probs_loto))
    assert pytest.approx(exp_loto, rel=1e-5) == 9.0000


def test_audit_game_execution():
    res = audit_game(
        game_id="br/mega-sena",
        draws_count=3,
        seed=42,
        fringe_names=["zeno_quantum", "sacred_grid"],
    )
    assert res.game_id == "br/mega-sena"
    assert res.draws_count == 3
    assert pytest.approx(res.theoretical_mean, rel=1e-5) == 0.6000
    assert len(res.metrics) == 4  # 2 fringe + 2 baselines

    for m in res.metrics:
        assert isinstance(m.mean_hits, float)
        assert isinstance(m.p_value_t_test, float)
        assert 0.0 <= m.p_value_t_test <= 1.0
        assert m.hypothesis_status in [
            "$H_0$ Não Rejeitada",
            "$H_0$ Rejeitada (Acima)",
            "$H_0$ Rejeitada (Abaixo)",
            "Linha de Base",
        ]


def test_cli_argument_parsing():
    args = parse_args(["--games", "br/mega-sena,br/quina", "--draws", "25", "--check-only"])
    assert args.games == "br/mega-sena,br/quina"
    assert args.draws == 25
    assert args.check_only is True


def test_cli_main_check_only_passes(tmp_path):
    report_file = tmp_path / "test_report.md"
    exit_code = main([
        "--games", "br/mega-sena",
        "--draws", "2",
        "--report", str(report_file),
        "--check-only",
        "--quiet",
    ])
    assert exit_code == 0
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Avaliação Estatística de Teorias Marginais" in content
    assert "Mega-Sena" in content
