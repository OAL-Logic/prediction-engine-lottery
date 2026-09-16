"""Random Baseline CLI Tests 🎲📏"""

from __future__ import annotations

from typer.testing import CliRunner

from engine.cli.main import app
from engine.cli.commands.random_baseline import generate_random_tickets, summarize
from engine.cli.utils import get_adapter

runner = CliRunner()
GAME = "br/mega-sena"


def test_generate_random_tickets_are_valid():
    adapter = get_adapter(GAME)
    lo, hi = adapter.rules.number_range
    tickets = generate_random_tickets(lo, hi, adapter.rules.pick_count, count=50, seed=1)
    assert len(tickets) == 50
    for t in tickets:
        assert len(t) == adapter.rules.pick_count
        assert len(set(t)) == len(t)  # no duplicates within a ticket
        assert all(lo <= n <= hi for n in t)


def test_generate_random_tickets_seed_reproducible():
    a = generate_random_tickets(1, 60, 6, count=20, seed=99)
    b = generate_random_tickets(1, 60, 6, count=20, seed=99)
    assert a == b


def test_summarize_odd_mean_near_half_for_large_sample():
    tickets = generate_random_tickets(1, 60, 6, count=3000, seed=7)
    stats = summarize(tickets, 1, 60)
    assert 2.5 < stats["odd_mean"] < 3.5  # ~half of 6, with sampling noise


def test_random_baseline_registered_and_runs():
    result = runner.invoke(app, ["random-baseline", GAME, "--count", "300", "--seed", "42"])
    assert result.exit_code == 0, result.output
    assert "RANDOM BASELINE" in result.output


def test_random_baseline_reproducible_with_same_seed():
    r1 = runner.invoke(app, ["random-baseline", GAME, "--count", "100", "--seed", "5"])
    r2 = runner.invoke(app, ["random-baseline", GAME, "--count", "100", "--seed", "5"])
    assert r1.output == r2.output
