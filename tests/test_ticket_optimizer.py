"""
Unit tests for SamLotto Ticket Optimizer Engine ✂️
==================================================
Tests same-number reduction (AC-T4) and reserve-per-block reduction (AC-T3).
"""

from engine.modules.ticket_optimizer import (
    same_number_reduction,
    reserve_per_block,
    OptimizationReport,
)


def test_reserve_per_block_ac_t3():
    """
    AC-T3: 'Each of 10 reserve 3' reduces every block of 10 lines to 3.
    Verifies that a 60-ticket pool is reduced to exactly 18 lines.
    """
    tickets = [[i, i + 1, i + 2, i + 3, i + 4, i + 5] for i in range(1, 61)]
    assert len(tickets) == 60

    report = reserve_per_block(tickets, reserve_count=3, block_size=10)

    assert report.initial_count == 60
    assert report.kept_count == 18
    assert report.eliminated_count == 42
    assert report.reduction_pct == 70.0
    assert len(report.kept_tickets) == 18

    # Block 1 kept: tickets[0], tickets[1], tickets[2]
    assert report.kept_tickets[0] == tickets[0]
    assert report.kept_tickets[1] == tickets[1]
    assert report.kept_tickets[2] == tickets[2]
    # Block 2 kept: tickets[10], tickets[11], tickets[12]
    assert report.kept_tickets[3] == tickets[10]
    assert report.kept_tickets[4] == tickets[11]
    assert report.kept_tickets[5] == tickets[12]


def test_reserve_per_block_edge_cases():
    # Empty set
    report = reserve_per_block([], reserve_count=3, block_size=10)
    assert report.initial_count == 0
    assert report.kept_count == 0

    # Incomplete final block: 15 tickets, reserve 3 of 10 -> 3 from first block + 3 from second block = 6
    tickets = [[i, i + 1, i + 2] for i in range(15)]
    report = reserve_per_block(tickets, reserve_count=3, block_size=10)
    assert report.initial_count == 15
    assert report.kept_count == 6

    # Invalid arguments
    caught_1 = False
    try:
        reserve_per_block(tickets, reserve_count=0)
    except ValueError:
        caught_1 = True
    assert caught_1

    caught_2 = False
    try:
        reserve_per_block(tickets, reserve_count=12, block_size=10)
    except ValueError:
        caught_2 = True
    assert caught_2


def test_same_number_reduction_ac_t4():
    """
    AC-T4: Lines sharing >= X identical numbers collapse to one representative.
    """
    t1 = [1, 2, 3, 4, 5, 6]
    t2 = [1, 2, 3, 4, 10, 11]  # Shares 4 numbers with t1: {1, 2, 3, 4}
    t3 = [1, 2, 10, 11, 20, 21]  # Shares 2 numbers with t1, 4 numbers with t2
    t4 = [30, 31, 32, 33, 34, 35]  # Completely disjoint

    tickets = [t1, t2, t3, t4]

    # With max_shared=4:
    # - t1 is kept.
    # - t2 shares 4 with t1 -> eliminated!
    # - t3 shares 2 with t1 -> kept!
    # - t4 shares 0 with both -> kept!
    report = same_number_reduction(tickets, max_shared=4)
    assert report.initial_count == 4
    assert report.kept_count == 3
    assert report.eliminated_count == 1
    assert report.kept_tickets == [t1, t3, t4]

    # With max_shared=3:
    # - t1 is kept.
    # - t2 shares 4 >= 3 -> eliminated!
    # - t3 shares 2 with t1 -> kept!
    # - t4 shares 0 -> kept!
    report_t3 = same_number_reduction(tickets, max_shared=3)
    assert report_t3.kept_count == 3


def test_same_number_reduction_positions():
    """
    Same number reduction restricted to specific slot positions.
    """
    t1 = [10, 20, 30, 40]
    t2 = [10, 20, 35, 45]  # Matches positions 0 and 1
    t3 = [30, 40, 88, 99]  # Different numbers at positions 0 and 1

    # Check only positions 0 and 1: t1 and t2 share 2 numbers at those positions
    report = same_number_reduction([t1, t2, t3], max_shared=2, positions=[0, 1])
    assert report.kept_tickets == [t1, t3]


def test_cli_ticket_optimize_smoke():
    from typer.testing import CliRunner
    from engine.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, [
        "ticket-optimize", "br/lotofacil",
        "--gen-count", "20",
        "--strategy", "reserve-per-block",
        "--reserve", "3",
        "--block-size", "10",
    ])
    assert result.exit_code == 0
    assert "Optimization Funnel" in result.output
    assert "reserve_per_block" in result.output
    assert "Kept Ticket Count" in result.output
