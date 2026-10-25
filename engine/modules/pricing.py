"""
Lottery Pricing & Multiple Bets Module 🏷️
==========================================
Provides unified access to official Caixa lottery ticket pricing, multiple bets scaling,
combinatorial expansions, and Teimosinha cost structures.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from engine._paths import PROJECT_ROOT

PRICING_FILE = PROJECT_ROOT / "data" / "pricing_and_multiple_bets.yaml"

_PRICING_CACHE: Optional[Dict[str, Any]] = None


def _load_pricing_data() -> Dict[str, Any]:
    global _PRICING_CACHE
    if _PRICING_CACHE is not None:
        return _PRICING_CACHE

    if not PRICING_FILE.exists():
        return {}

    with open(PRICING_FILE, "r", encoding="utf-8") as f:
        _PRICING_CACHE = yaml.safe_load(f) or {}

    return _PRICING_CACHE


def get_lottery_pricing(lottery_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve full pricing specification for a specific lottery id."""
    data = _load_pricing_data()
    lotteries = data.get("lotteries", {})
    return lotteries.get(lottery_id)


def get_multiple_bets(lottery_id: str) -> List[Dict[str, Any]]:
    """Return the list of multiple bet configurations for a given lottery."""
    info = get_lottery_pricing(lottery_id)
    if not info:
        return []
    return info.get("multiple_bets", [])


def get_teimosinha_rules(lottery_id: str) -> Dict[str, Any]:
    """Return Teimosinha configurations (allowed draws, default, draw days)."""
    info = get_lottery_pricing(lottery_id)
    if not info:
        return {"allowed_draws": [1], "default_draws": 1, "draw_days": []}
    return info.get("teimosinha", {})


def calculate_bet_cost(
    lottery_id: str,
    n_numbers: int,
    consecutive_draws: int = 1,
    n_trevos: int = 2,
) -> float:
    """
    Calculate the exact official cost of a bet given number count and consecutive draws.
    Falls back to combinatorics formula if not explicitly listed in YAML.
    """
    info = get_lottery_pricing(lottery_id)
    if not info:
        return 0.0

    base_price = info["single_bet"]["price"]
    k = info["single_bet"]["numbers"]

    # Check explicit table
    multiples = info.get("multiple_bets", [])
    for row in multiples:
        if row.get("numbers") == n_numbers:
            if "trevos" in row:
                if row["trevos"] == n_trevos:
                    return float(row["price_single_draw"] * consecutive_draws)
            else:
                return float(row["price_single_draw"] * consecutive_draws)

    # Mathematical fallback
    combs = math.comb(n_numbers, k)
    if "+milionaria" in lottery_id or "milionaria" in lottery_id:
        trevo_combs = math.comb(n_trevos, 2)
        combs *= trevo_combs

    return float(round(combs * base_price * consecutive_draws, 2))
