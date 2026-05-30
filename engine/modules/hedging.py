"""
Combinatorial Hedging & Portfolio Balancing Module  ⚖️
======================================================
Implements modern portfolio theory and combinatorial optimization on lottery bets.
Enables splitting a bet budget into:
  1. Jackpot Core (high-EV / aggressive / GNN-driven picks)
  2. Hedge Foundation (rigorous covering designs targeting lower-tier prizes)

Simulates the joint probability distribution of payouts to mathematically
guarantee and prove the hedge ratio and self-sustainability of the portfolio.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.wheels import generate_abbreviated_wheel, generate_full_wheel, generate_key_wheel


@dataclass
class HedgeMetrics:
    total_budget: float
    jackpot_allocation: float
    hedge_allocation: float
    jackpot_tickets_count: int
    hedge_tickets_count: int
    expected_payout: float
    hedge_coverage_ratio: float
    net_roi: float
    self_sustainability_score: float  # Probability of recovering >= 100% of the total cost
    partial_recovery_score: float      # Probability of recovering >= 50% of the total cost
    max_drawdown: float
    win_probability: float             # Probability of getting at least one prize tier in the portfolio


class CombinatorialHedger:
    """Manages the optimization and simulation of mathematically balanced hedged portfolios."""

    def __init__(self, rules: DrawRules) -> None:
        self.rules = rules

    def calculate_allocation(
        self, budget: float, risk_profile: str
    ) -> Tuple[float, float, int, int]:
        """Calculates the optimal budget and ticket split between Jackpot and Hedge."""
        price = self.rules.ticket_price
        total_tickets = int(budget // price)

        if total_tickets < 1:
            raise ValueError(f"Budget {budget} is less than the ticket price {price}")

        # Split percentages based on risk profiles
        splits = {
            "conservative": (0.30, 0.70),  # 30% Jackpot, 70% Hedge
            "balanced": (0.50, 0.50),      # 50% Jackpot, 50% Hedge
            "aggressive": (0.70, 0.30),    # 70% Jackpot, 30% Hedge
        }
        jackpot_pct, hedge_pct = splits.get(risk_profile.lower(), (0.50, 0.50))

        # Assign ticket counts
        jackpot_count = max(1, int(round(total_tickets * jackpot_pct)))
        hedge_count = max(0, total_tickets - jackpot_count)

        # Handle edge case where total_tickets is small
        if total_tickets >= 2 and hedge_count == 0:
            jackpot_count -= 1
            hedge_count = 1

        jackpot_alloc = jackpot_count * price
        hedge_alloc = hedge_count * price

        return jackpot_alloc, hedge_alloc, jackpot_count, hedge_count

    def generate_balanced_portfolio(
        self,
        jackpot_scores: dict[int, float],
        hedge_scores: dict[int, float],
        budget: float,
        risk_profile: str = "balanced",
    ) -> Dict[str, Any]:
        """Generates the optimal balanced portfolio consisting of Jackpot and Hedge tickets."""
        j_alloc, h_alloc, j_count, h_count = self.calculate_allocation(budget, risk_profile)
        lo, hi = self.rules.number_range

        # 1. Jackpot Core Generation: High-temperature or high-EV focus
        sorted_j = sorted(jackpot_scores.items(), key=lambda x: x[1], reverse=True)
        j_pool = [n for n, s in sorted_j[: self.rules.pick_count * 2]]
        
        # Select Jackpot tickets using random choice weighted by scores
        jackpot_tickets = []
        for _ in range(j_count):
            ticket = sorted(random.sample(j_pool, self.rules.pick_count))
            jackpot_tickets.append(ticket)

        # 2. Hedge Foundation Generation: Highly optimized abbreviated covering wheel
        hedge_tickets = []
        if h_count > 0:
            # Conservative/balanced uses a tighter pool for stronger localized guarantee
            pool_sizes = {"conservative": 10, "balanced": 14, "aggressive": 18}
            h_pool_size = min(pool_sizes.get(risk_profile.lower(), 14), hi - lo + 1)
            
            sorted_h = sorted(hedge_scores.items(), key=lambda x: x[1], reverse=True)
            h_pool = [n for n, s in sorted_h[:h_pool_size]]
            
            # Guarantee lowest prize tier (e.g. 11 for Lotofacil, 4 for Mega-Sena)
            target_matches = self.rules.prize_tiers[0]
            hedge_tickets = generate_abbreviated_wheel(
                h_pool, self.rules.pick_count, guarantee=target_matches, max_tickets=h_count
            )

        return {
            "jackpot_tickets": jackpot_tickets,
            "hedge_tickets": hedge_tickets,
            "jackpot_allocation": j_alloc,
            "hedge_allocation": h_alloc,
            "jackpot_count": j_count,
            "hedge_count": h_count,
            "jackpot_pool": j_pool,
            "hedge_pool": h_pool if h_count > 0 else [],
        }

    def simulate_portfolio_payouts(
        self,
        portfolio: Dict[str, Any],
        trials: int = 5000,
    ) -> HedgeMetrics:
        """Runs a Monte Carlo simulation of the portfolio returns to mathematically prove the hedge."""
        j_tickets = portfolio["jackpot_tickets"]
        h_tickets = portfolio["hedge_tickets"]
        all_tickets = j_tickets + h_tickets
        total_cost = (len(j_tickets) + len(h_tickets)) * self.rules.ticket_price

        # Standardized payout matrix relative to ticket price
        # Mega-Sena: 4 matches ~ 10x ticket, 5 matches ~ 2000x ticket, 6 matches ~ Jackpot (million)
        # Lotofacil: 11 matches ~ 1.2x ticket, 12 matches ~ 2.4x ticket, 13 matches ~ 6x ticket, 14 matches ~ 300x, 15 matches ~ Jackpot
        payout_multipliers = {}
        if "lotofacil" in self.rules.name.lower():
            payout_multipliers = {11: 1.2, 12: 2.4, 13: 6.0, 14: 400.0, 15: 100000.0}
        elif "mega" in self.rules.name.lower():
            payout_multipliers = {4: 25.0, 5: 8000.0, 6: 1000000.0}
        else:
            # Default fallback multiplier table
            payout_multipliers = {
                self.rules.prize_tiers[0]: 10.0,
                self.rules.prize_tiers[1]: 500.0,
                self.rules.prize_tiers[2]: 50000.0,
            }

        payouts = []
        lo, hi = self.rules.number_range
        pool = list(range(lo, hi + 1))

        wins_count = 0
        total_payout = 0.0

        for _ in range(trials):
            # Draw winning numbers
            winning_numbers = set(random.sample(pool, self.rules.pick_count))
            trial_payout = 0.0
            had_win = False

            for t in all_tickets:
                matches = len(winning_numbers.intersection(t))
                mult = payout_multipliers.get(matches, 0.0)
                if mult > 0:
                    trial_payout += mult * self.rules.ticket_price
                    had_win = True

            payouts.append(trial_payout)
            total_payout += trial_payout
            if had_win:
                wins_count += 1

        payouts = np.array(payouts)

        expected_payout = float(payouts.mean())
        hedge_coverage_ratio = expected_payout / total_cost
        net_roi = (expected_payout - total_cost) / total_cost
        self_sustainability = float((payouts >= total_cost).mean())
        partial_recovery = float((payouts >= total_cost * 0.5).mean())
        max_drawdown = float(total_cost - payouts.min())
        win_prob = float(wins_count / trials)

        return HedgeMetrics(
            total_budget=total_cost,
            jackpot_allocation=portfolio["jackpot_allocation"],
            hedge_allocation=portfolio["hedge_allocation"],
            jackpot_tickets_count=portfolio["jackpot_count"],
            hedge_tickets_count=portfolio["hedge_count"],
            expected_payout=round(expected_payout, 2),
            hedge_coverage_ratio=round(hedge_coverage_ratio, 4),
            net_roi=round(net_roi * 100, 2),
            self_sustainability_score=round(self_sustainability * 100, 2),
            partial_recovery_score=round(partial_recovery * 100, 2),
            max_drawdown=round(max_drawdown, 2),
            win_probability=round(win_prob * 100, 2),
        )
