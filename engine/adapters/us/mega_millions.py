"""
Mega Millions — United States (multi-state)
=============================================
Rules (post-Apr 2025 matrix):
  Pick 5 white balls from 1-70
  Pick 1 Mega Ball from 1-25
  Megaplier multiplier is not modelled here (draw results only)

Source:   NY Lottery open-data Socrata API
Endpoint: https://data.ny.gov/resource/5xaw-6ayf.json
Docs:     https://data.ny.gov/Government-Finance/Lottery-Mega-Millions-Winning-Numbers-Beginning-20/5xaw-6ayf

Note on localized jackpot
--------------------------
Mega Millions is a multi-state game — jackpot is pooled nationally.
No city/state breakdown is relevant to draw analysis.
"""

import logging
import sys
from typing import Any, List, Dict

import httpx
import pandas as pd

from engine.adapters import Draw, DrawRules, LotteryAdapter
from engine.modules.storage import storage

logger = logging.getLogger(__name__)

SOURCE_URL = (
    "https://data.ny.gov/resource/5xaw-6ayf.json"
    "?$order=draw_date+DESC&$limit=5000"
)

MEGA_MILLIONS_RULES = DrawRules(
    name="Mega Millions",
    pick_count=5,
    number_range=(1, 70),
    bonus_count=1,
    bonus_range=(1, 25),
    prize_tiers=[3, 4, 5],
    ticket_price=2.0,
    currency="USD",
    odds={
        3: 606,
        4: 14547,
        5: 302575350,
    }
)


class MegaMillionsAdapter(LotteryAdapter):
    """Mega Millions data adapter — NY Lottery Socrata API with local cache fallback."""

    rules = MEGA_MILLIONS_RULES

    def __init__(self, cache_path: Any = None, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def fetch(self, limit: int | None = None) -> pd.DataFrame:
        """
        Fetch logic:
        1. Try to fetch from NY Lottery API.
        2. If success, save to DB (which updates partitions).
        3. If fail, load from DB.
        """
        lottery_id = "us/mega-millions"

        try:
            print("  Fetching Mega Millions from NY Lottery open-data…", file=sys.stderr)
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
                "Could not fetch Mega Millions data from any source.\n"
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

        storage.save_draws("us/mega-millions", parsed)

    def _parse_draw(self, row: dict[str, Any]) -> Draw | None:
        """
        Socrata row shape:
          draw_date       "2026-09-15T00:00:00.000"
          winning_numbers "27 36 43 57 58"   ← the 5 white balls only
          mega_ball       "16"               ← bonus ball, its own field
        """
        try:
            date = str(row["draw_date"])[:10]
            main = sorted(int(n) for n in str(row["winning_numbers"]).split())
            if len(main) != 5:
                return None
            bonus = [int(row["mega_ball"])]
            draw_id = int(date.replace("-", ""))
            return Draw(draw_id=draw_id, date=date, numbers=main, bonus=bonus)
        except (KeyError, ValueError, TypeError) as exc:
            logger.debug("Parse error: %s — %s", exc, row)
            return None
