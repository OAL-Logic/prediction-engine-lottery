"""Swarm-based fractional Kelly sizer (Story 4.3).

Turns swarm consensus confidence into a "Confidence Leverage" signal: a bet
fraction and stake against the user's vault balance. Pure; no I/O. This is a
leverage signal, not the lottery-odds model (see ``engine/modules/kelly_bankroll.py``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

BASELINE_CONFIDENCE = 0.5
KELLY_FRACTION = 0.25
# Same safety ceiling as engine/modules/kelly_bankroll.py.
MAX_FRACTION = 0.10
DEFAULT_ODDS = 1.0


@dataclass(frozen=True)
class KellyLeverage:
    confidence: float
    full_kelly: float  # raw f*, floored at 0; 0 when below baseline
    fraction: float  # fractional, clamped share of the vault
    stake: float  # fraction * vault balance
    active: bool


def _finite(x: object) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def confidence_leverage(
    confidence: float,
    vault_balance: float,
    odds: float = DEFAULT_ODDS,
    baseline: float = BASELINE_CONFIDENCE,
    kelly_fraction: float = KELLY_FRACTION,
    max_fraction: float = MAX_FRACTION,
) -> KellyLeverage:
    """Size a bet from swarm confidence. Raises ValueError on invalid input."""
    for name, v in (
        ("confidence", confidence),
        ("vault_balance", vault_balance),
        ("odds", odds),
        ("baseline", baseline),
        ("kelly_fraction", kelly_fraction),
        ("max_fraction", max_fraction),
    ):
        if not _finite(v):
            raise ValueError(f"{name} must be a finite number")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be within [0, 1]")
    if odds <= 0:
        raise ValueError("odds must be > 0")
    if vault_balance < 0:
        raise ValueError("vault_balance must be >= 0")
    if kelly_fraction < 0 or max_fraction < 0:
        raise ValueError("kelly_fraction and max_fraction must be >= 0")

    if confidence <= baseline:
        return KellyLeverage(float(confidence), 0.0, 0.0, 0.0, False)

    full = max(0.0, (odds * confidence - (1.0 - confidence)) / odds)
    fraction = min(full * kelly_fraction, max_fraction)
    stake = fraction * vault_balance
    return KellyLeverage(float(confidence), full, fraction, stake, fraction > 0)
