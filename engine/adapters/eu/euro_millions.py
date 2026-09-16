"""
EuroMillions — Pan-European (FR/ES/UK/PT/BE/IE/LU/CH/AT/MC + others)
=====================================================================
Rules:
  Pick 5 main numbers from 1-50
  Pick 2 Lucky Stars from 1-12

Source: community-maintained draw archive (no official EuroMillions open-data
API exists — operators are national lotteries, not a single body). Updated by
a scheduled GitHub Actions job on every draw day (Tue/Fri).
  https://github.com/daowa89/lottery-archive
  Raw CSV: https://raw.githubusercontent.com/daowa89/lottery-archive/main/eu/euromillions/results.csv
  Columns: date,n1,n2,n3,n4,n5,s1,s2

Being a community mirror rather than an operator API, treat it the same way
`CaixaBaseAdapter` treats its own community bulk mirror: best-effort, with
the local DB cache as the fallback of record if it's ever unreachable or its
schema changes underneath us.
"""

import csv
import io
import logging
import sys
from typing import Any, List, Dict

import httpx
import pandas as pd

from engine.adapters import Draw, DrawRules, LotteryAdapter
from engine.modules.storage import storage

logger = logging.getLogger(__name__)

SOURCE_URL = "https://raw.githubusercontent.com/daowa89/lottery-archive/main/eu/euromillions/results.csv"

EURO_MILLIONS_RULES = DrawRules(
    name="EuroMillions",
    pick_count=5,
    number_range=(1, 50),
    bonus_count=2,
    bonus_range=(1, 12),
    prize_tiers=[2, 3, 4, 5],
    ticket_price=2.5,
    currency="EUR",
    # Jackpot tier only (C(50, 5) * C(12, 2)) — matches the convention every
    # other adapter uses for `odds` (see odds.py's _run_comparison(), which
    # needs at least the max tier to include a game in `lottery odds
    # --compare`). Real EuroMillions has 13 official prize tiers combining
    # main+star matches; only the jackpot one is cheap to state exactly right
    # from this adapter's own pick/pool/bonus numbers, so that's the one
    # modeled — the others aren't guessed at.
    odds={5: 139_838_160},
)


class EuroMillionsAdapter(LotteryAdapter):
    """EuroMillions data adapter — community CSV archive with local cache fallback."""

    rules = EURO_MILLIONS_RULES

    def __init__(self, cache_path: Any = None, timeout: float = 20.0) -> None:
        self.timeout = timeout

    def fetch(self, limit: int | None = None) -> pd.DataFrame:
        """
        Fetch logic:
        1. Try to download the full CSV archive.
        2. If success, save to DB (which updates partitions).
        3. If fail, load from DB.
        """
        lottery_id = "eu/euro-millions"

        try:
            print("  Fetching EuroMillions from community draw archive…", file=sys.stderr)
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get(SOURCE_URL)
                resp.raise_for_status()
                rows = list(csv.DictReader(io.StringIO(resp.text)))
            if rows:
                self._save_to_db(rows)
                print(f"  ✓ {len(rows)} rows fetched", file=sys.stderr)
        except Exception as exc:
            print(f"  ✗ Live fetch failed: {exc} — trying DB cache…", file=sys.stderr)

        df = storage.load_draws(lottery_id, limit=limit)

        if df.empty:
            raise RuntimeError(
                "Could not fetch EuroMillions data from any source.\n"
                "Check your internet connection and try again."
            )

        # Ensure correct types for the engine
        df["date"] = pd.to_datetime(df["draw_date"], errors="coerce", utc=True)
        # Drop rows with invalid/missing dates (prevents NaT errors in strategies)
        df = df.dropna(subset=["date"])

        return df

    def _save_to_db(self, raw_rows: List[Dict[str, Any]]):
        """Parse raw CSV dict-rows and save to DuckDB."""
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

        storage.save_draws("eu/euro-millions", parsed)

    def _parse_draw(self, row: dict[str, Any]) -> Draw | None:
        """
        CSV row shape (header: date,n1,n2,n3,n4,n5,s1,s2):
          date  "2026-09-12"     ← already ISO YYYY-MM-DD
          n1-n5 main numbers (1-50)
          s1-s2 Lucky Stars (1-12)
        """
        try:
            date = str(row["date"])[:10]
            main = sorted(int(row[f"n{i}"]) for i in range(1, 6))
            bonus = sorted(int(row[f"s{i}"]) for i in range(1, 3))
            draw_id = int(date.replace("-", ""))
            return Draw(draw_id=draw_id, date=date, numbers=main, bonus=bonus)
        except (KeyError, ValueError, TypeError) as exc:
            logger.debug("Parse error: %s — %s", exc, row)
            return None
