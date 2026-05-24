"""
Adapter interface — every lottery implements this contract.

A LotteryAdapter knows:
  - the rules of its lottery (ball count, ranges, bonus balls)
  - how to fetch historical draw data from its source
  - how to validate a candidate ticket

All adapters return a canonical DataFrame with columns:
    draw_id   int       sequential draw number
    date      datetime  draw date (UTC)
    numbers   list[int] main numbers drawn (sorted)
    bonus     list[int] bonus/powerball numbers (may be empty)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True)
class DrawRules:
    """Immutable lottery rule definition."""

    name: str
    pick_count: int          # standard pick count (base bet)
    number_range: tuple[int, int]   # (min, max) inclusive
    bonus_count: int = 0
    bonus_range: tuple[int, int] | None = None
    prize_tiers: list[int] = field(default_factory=lambda: [4, 5, 6]) # Default for most games
    board_cols: int = 10     # standard visual board width (for patterns/mapping)
    
    # Financials & Odds (New in Sprint 1.1)
    ticket_price: float = 0.0
    currency: str = "USD"
    odds: dict[int, int] = field(default_factory=dict) # tier -> 1 in X odds (for base bet)
    
    # Multiple Bet support
    max_picks: int | None = None  # max numbers allowed in a single ticket

    @property
    def allowed_picks(self) -> list[int]:
        """Return list of allowed number of picks for a single ticket."""
        if self.max_picks:
            return list(range(self.pick_count, self.max_picks + 1))
        return [self.pick_count]

    def calculate_bet_cost(self, n_picked: int) -> float:
        """Calculate the price of a multiple bet with n numbers."""
        from math import comb
        if n_picked not in self.allowed_picks:
            raise ValueError(f"{n_picked} is not an allowed pick count for {self.name}")
        # A multiple bet of size N is equivalent to C(N, pick_count) base bets
        n_combinations = comb(n_picked, self.pick_count)
        return n_combinations * self.ticket_price

    @property
    def jackpot_odds(self) -> int:
        """Return the '1 in X' odds for the highest prize tier."""
        if not self.odds:
            return 0
        return self.odds[max(self.odds.keys())]

    @staticmethod
    def calculate_combination_odds(n: int, k: int) -> int:
        """Helper to calculate C(n, k) — the '1 in X' odds for pick-k-from-n."""
        from math import comb
        return comb(n, k)

    def validate(self, numbers: list[int], bonus: list[int] | None = None) -> bool:
        """Return True if the ticket is valid under these rules."""
        lo, hi = self.number_range
        n_picked = len(numbers)
        
        if n_picked not in self.allowed_picks:
            return False
        if len(set(numbers)) != n_picked:
            return False  # duplicates
        if not all(lo <= n <= hi for n in numbers):
            return False
        if self.bonus_count > 0:
            bonus = bonus or []
            if len(bonus) != self.bonus_count:
                return False
            blo, bhi = self.bonus_range  # type: ignore[misc]
            if not all(blo <= b <= bhi for b in bonus):
                return False
        return True


@dataclass
class Draw:
    """A single historical draw result."""

    draw_id: int
    date: str                   # ISO-8601 date string
    numbers: List[int]
    bonus: List[int] = field(default_factory=list)


class LotteryAdapter(ABC):
    """Base class for all lottery data adapters."""

    rules: DrawRules

    # ------------------------------------------------------------------
    # Required overrides
    # ------------------------------------------------------------------

    @abstractmethod
    def fetch(self, limit: int | None = None) -> pd.DataFrame:
        """
        Fetch historical draws from the lottery's data source.

        Parameters
        ----------
        limit : int | None
            If set, return only the *limit* most recent draws.

        Returns
        -------
        pd.DataFrame with columns:
            draw_id (int), date (datetime64[ns, UTC]), numbers (object/list[int]),
            bonus (object/list[int])
        """
        ...

    # ------------------------------------------------------------------
    # Helpers available to all adapters
    # ------------------------------------------------------------------

    def validate(self, numbers: list[int], bonus: list[int] | None = None) -> bool:
        return self.rules.validate(numbers, bonus)

    def to_dataframe(self, draws: list[Draw]) -> pd.DataFrame:
        """Convert a list of Draw objects into the canonical DataFrame."""
        import pandas as pd
        rows = [
            {
                "draw_id": d.draw_id,
                "date": pd.to_datetime(d.date, utc=True),
                "numbers": sorted(d.numbers),
                "bonus": d.bonus,
            }
            for d in draws
        ]
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("draw_id").reset_index(drop=True)
        return df
