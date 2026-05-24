"""
Powerball — United States (multi-state)
========================================
Rules (post-Oct 2015 matrix):
  Pick 5 white balls from 1–69
  Pick 1 Powerball from 1–26
  Power Play multiplier is not modelled here (draw results only)

Source:   NY Lottery open-data Socrata API
Endpoint: https://data.ny.gov/resource/d6yy-54nr.json
Docs:     https://data.ny.gov/Government-Finance/Lottery-Powerball-Winning-Numbers-Beginning-2010/d6yy-54nr

Note on localized jackpot
--------------------------
Powerball is a multi-state game — jackpot is pooled nationally.
No city/state breakdown is relevant to draw analysis.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, List, Dict

import httpx
import pandas as pd

from engine.adapters import Draw, DrawRules, LotteryAdapter
from engine.modules.storage import storage

logger = logging.getLogger(__name__)

SOURCE_URL = (
    "https://data.ny.gov/resource/d6yy-54nr.json"
    "?$order=draw_date+DESC&$limit=5000"
)

POWERBALL_RULES = DrawRules(
    name="Powerball",
    pick_count=5,
    number_range=(1, 69),
    bonus_count=1,
    bonus_range=(1, 26),
    prize_tiers=[3, 4, 5],
    ticket_price=2.0,
    currency="USD",
    odds={
        3: 579,
        4: 36525,
        5: 292201338,
    }
)


class PowerballAdapter(LotteryAdapter):
    """Powerball data adapter — NY Lottery Socrata API with local cache fallback."""

    rules = POWERBALL_RULES

    def __init__(self, cache_path: Any = None, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def fetch(self, limit: int | None = None) -> pd.DataFrame:
        """
        Fetch logic:
        1. Try to fetch from NY Lottery API.
        2. If success, save to DB (which updates partitions).
        3. If fail, load from DB.
        """
        lottery_id = "us/powerball"
        
        try:
            print("  Fetching Powerball from NY Lottery open-data…", file=sys.stderr)
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get(SOURCE_URL)
                resp.raise_for_status()
                raw = resp.json()
            if raw:
                self._save_to_db(raw)
                print(f"  ✓ {len(raw)} rows fetched", file=sys.stderr)
        except Exception as exc:
            print(f"  ✗ Live fetch failed: {exc} — trying DB cache…", file=sys.stderr)

        df = storage.load_draws(lottery_id, limit=limit)
        
        if df.empty:
            raise RuntimeError(
                "Could not fetch Powerball data from any source.\n"
                "Check your internet connection and try again."
            )

        # Ensure correct types for the engine
        df["date"] = pd.to_datetime(df["draw_date"], errors="coerce", utc=True)
        # Drop rows with invalid/missing dates (prevents NaT errors in strategies)
        df = df.dropna(subset=["date"])
        
        return df

    def _save_to_db(self, raw_rows: List[Dict[str, Any]]):
        """Parse raw Socrata JSON rows and save to DuckDB."""
        parsed = []
        for row in raw_rows:
            d = self._parse_draw(row)
            if d:
                parsed.append({
                    "draw_id": d.draw_id,
                    "date": d.date,
                    "numbers": d.numbers,
                    "bonus": d.bonus
                })
        
        storage.save_draws("us/powerball", parsed)

    def _parse_draw(self, row: dict[str, Any]) -> Draw | None:
        """
        Socrata row shape:
          draw_date       "2024-01-06T00:00:00.000"
          winning_numbers "12 34 45 56 67"   ← last number is the Powerball
          multiplier      "3X"               ← ignored
        """
        try:
            date = str(row["draw_date"])[:10]
            parts = [int(n) for n in str(row["winning_numbers"]).split()]
            if len(parts) < 2:
                return None
            main  = sorted(parts[:-1])
            bonus = [parts[-1]]
            draw_id = int(date.replace("-", ""))
            return Draw(draw_id=draw_id, date=date, numbers=main, bonus=bonus)
        except (KeyError, ValueError, TypeError) as exc:
            logger.debug("Parse error: %s — %s", exc, row)
            return None

