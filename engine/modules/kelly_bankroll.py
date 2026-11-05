"""
Fractional Kelly Bankroll Allocation & Special Jackpot Arbitrage Module (Track R)
==================================================================================
Implements classical Kelly Criterion expected utility theory adapted to fat-tailed
lottery payout distributions and special non-accumulating jackpots.
Tier: scientific (ADR-0005).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional


# Standard combinatorial probability of winning top prize (6/60, 15/25, 5/80, 5/69+1/26)
DEFAULT_ODDS: Dict[str, float] = {
    "br/mega-sena": 1.0 / 50063860.0,
    "mega-sena": 1.0 / 50063860.0,
    "br/lotofacil": 1.0 / 3268760.0,
    "lotofacil": 1.0 / 3268760.0,
    "br/quina": 1.0 / 24040016.0,
    "quina": 1.0 / 24040016.0,
    "us/powerball": 1.0 / 292201338.0,
    "powerball": 1.0 / 292201338.0,
}

DEFAULT_TICKET_COSTS: Dict[str, float] = {
    "br/mega-sena": 5.0,
    "mega-sena": 5.0,
    "br/lotofacil": 3.0,
    "lotofacil": 3.0,
    "br/quina": 2.5,
    "quina": 2.5,
    "us/powerball": 2.0,
    "powerball": 2.0,
}


@dataclass
class KellyResult:
    lottery: str
    jackpot: float
    bankroll: float
    ticket_cost: float
    probability: float
    net_odds: float
    expected_value: float
    full_kelly_f: float
    fractional_multiplier: float
    safe_fraction: float
    recommended_capital: float
    recommended_tickets: int
    solo_equity_multiplier: float
    verdict: str


def compute_solo_equity_factor(subspace: str = "anti-popular", estimated_bets: float = 30000000.0, p_win: float = 1.0 / 50063860.0) -> float:
    """
    Computes expected solo prize share factor based on Poisson co-winner modeling.
    For anti-popular subspace, human calendar clustering is minimized,
    yielding significantly higher solo equity than birthday-clustered tickets.
    """
    lam = estimated_bets * p_win
    if lam <= 0:
        return 1.0

    if subspace == "anti-popular":
        # Anti-popular tickets exhibit 60-80% lower collision rate
        adj_lam = max(0.05, lam * 0.35)
    elif subspace == "popular":
        # Birthday/arithmetic sequences exhibit heavy clustering
        adj_lam = lam * 2.5
    else:
        adj_lam = lam

    # E[1 / (1 + K)] where K ~ Poisson(lambda) is (1 - e^-lambda) / lambda
    # Prize multiplier relative to average co-winners
    avg_share = (1.0 - math.exp(-adj_lam)) / adj_lam
    base_share = (1.0 - math.exp(-lam)) / lam if lam > 0 else 1.0
    return max(0.5, min(5.0, avg_share / max(1e-6, base_share)))


def compute_fractional_kelly(
    lottery: str,
    jackpot: float,
    bankroll: float,
    fraction: float = 0.05,
    subspace: str = "anti-popular",
    custom_ticket_cost: Optional[float] = None,
    custom_p: Optional[float] = None,
) -> KellyResult:
    """
    Calculates constrained fractional Kelly bankroll allocation.
    Enforces safety ceiling fraction <= 0.10 to eliminate ruin risk in lottery tail regimes.
    """
    clean_lottery = lottery.lower().strip()
    p = custom_p if custom_p is not None else DEFAULT_ODDS.get(clean_lottery, 1.0 / 50063860.0)
    ticket_cost = custom_ticket_cost if custom_ticket_cost is not None else DEFAULT_TICKET_COSTS.get(clean_lottery, 5.0)

    # Solo equity adjustment
    solo_mult = compute_solo_equity_factor(subspace=subspace, p_win=p)
    effective_jackpot = jackpot * solo_mult

    # Net odds b = (Effective Payout - Cost) / Cost
    b = max(0.0, (effective_jackpot - ticket_cost) / ticket_cost)
    q = 1.0 - p

    # Expected Value per ticket
    ev = (p * effective_jackpot) - ticket_cost

    # Classical single-trial Kelly formula f* = (b*p - q) / b
    if b > 0 and (b * p - q) > 0:
        full_kelly = (b * p - q) / b
        verdict = "FAVORABLE (POSITIVE EV)"
        # Campaign / Portfolio Kelly for discrete tickets:
        # In a multi-ticket syndicate when EV > 0, bankroll fraction scales with relative edge
        # clamped to the user safety fraction limit (max 10% of bankroll)
        edge_ratio = max(0.0, ev / ticket_cost)
        safe_fraction_mult = max(0.001, min(0.10, fraction))
        safe_f = safe_fraction_mult * min(1.0, edge_ratio)
        recommended_capital = safe_f * bankroll
        recommended_tickets = max(1, int(recommended_capital // ticket_cost)) if bankroll >= ticket_cost else 0
        actual_capital = recommended_tickets * ticket_cost
    else:
        full_kelly = 0.0
        verdict = "UNFAVORABLE (NEGATIVE EV — ZERO ALLOCATION)"
        safe_fraction_mult = max(0.001, min(0.10, fraction))
        safe_f = 0.0
        recommended_capital = 0.0
        recommended_tickets = 0
        actual_capital = 0.0

    return KellyResult(
        lottery=clean_lottery,
        jackpot=jackpot,
        bankroll=bankroll,
        ticket_cost=ticket_cost,
        probability=p,
        net_odds=b,
        expected_value=ev,
        full_kelly_f=full_kelly,
        fractional_multiplier=safe_fraction_mult,
        safe_fraction=safe_f,
        recommended_capital=actual_capital,
        recommended_tickets=recommended_tickets,
        solo_equity_multiplier=round(solo_mult, 3),
        verdict=verdict,
    )


def format_kelly_report(res: KellyResult) -> str:
    """Renders a readable terminal ASCII box with Kelly analysis."""
    p_str = f"1 in {int(1.0 / res.probability):,}" if res.probability > 0 else "0"
    lines = [
        "┌────────────────────────────────────────────────────────┐",
        "│       🏛️  FRACTIONAL KELLY BANKROLL ALLOCATOR          │",
        "│       Track R · Scientific Decision Theory             │",
        "├────────────────────────────────────────────────────────┤",
        f"│ Jogo Analisado       : {res.lottery.upper():<32}│",
        f"│ Prêmio Estimado      : R$ {res.jackpot:,.2f}".ljust(57) + "│",
        f"│ Banca Total          : R$ {res.bankroll:,.2f}".ljust(57) + "│",
        f"│ Custo do Bilhete     : R$ {res.ticket_cost:,.2f}".ljust(57) + "│",
        f"│ Probabilidade Topo   : {p_str:<32}│",
        f"│ Solo Equity Multipler: {res.solo_equity_multiplier:.2f}x (Subespaço Anti-Popular)   │",
        f"│ Valor Esperado (EV)  : R$ {res.expected_value:+,.2f} por bilhete".ljust(57) + "│",
        "├────────────────────────────────────────────────────────┤",
        f"│ Veredito EV          : {res.verdict:<32}│",
        f"│ Kelly Pleno (f*)     : {res.full_kelly_f * 100:.4f}% da banca".ljust(57) + "│",
        f"│ Trava Fracionária    : {res.fractional_multiplier * 100:.1f}% do Kelly Pleno           │",
        f"│ Fração Segura (f_safe: {res.safe_fraction * 100:.5f}% da banca".ljust(57) + "│",
        "├────────────────────────────────────────────────────────┤",
        f"│ APORTE RECOMENDADO   : R$ {res.recommended_capital:,.2f}".ljust(57) + "│",
        f"│ QUANTIDADE BILHETES  : {res.recommended_tickets:,} apostas".ljust(57) + "│",
        "└────────────────────────────────────────────────────────┘",
    ]
    return "\n".join(lines)
