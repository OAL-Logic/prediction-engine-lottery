"""
CaixaBaseAdapter
================
Shared fetch / parse / cache logic for all Caixa Econômica Federal lotteries.

Subclasses must set three class-level attributes:

    game_slug      : str   — Caixa API path segment  (e.g. "megasena", "lotofacil")
    community_slug : str   — Community mirror slug    (e.g. "mega-sena", "lotofacil")
    cache_file_name: str   — JSON cache filename      (e.g. "mega_sena_cache.json")

And the inherited:

    rules          : DrawRules

Data sources (tried in order)
------------------------------
  1. Community bulk mirror  — all draws as a JSON list
  2. Caixa incremental API  — per-concurso endpoint, newest → oldest
  3. Local JSON cache       — data/<cache_file_name>

Caixa API response shape (relevant fields)
-------------------------------------------
  numero           int          draw number  (also seen as "numeroConcurso")
  dataApuracao     str          "DD/MM/YYYY"
  listaDezenas     list[str]    winning numbers as strings

Community mirror shape
-----------------------
  concurso         int          draw number  (also "numeroConcurso")
  data             str          "DD/MM/YYYY" or "YYYY-MM-DD"
  dezenas          list[str]    winning numbers as strings
"""

from __future__ import annotations

import json
import logging
import sys
from abc import abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Dict, List

import httpx
import pandas as pd

from engine.adapters import Draw, DrawRules, LotteryAdapter
from engine.modules.storage import storage, DATA_DIR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# URL templates — {slug} filled by subclass
# ---------------------------------------------------------------------------

_COMMUNITY_BULK = "https://loteriascaixa-api.herokuapp.com/api/{slug}"
_CAIXA_LATEST   = "https://servicebus2.caixa.gov.br/portaldeloterias/api/{slug}"
_CAIXA_CONCURSO = "https://servicebus2.caixa.gov.br/portaldeloterias/api/{slug}/{n}"


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


class CaixaBaseAdapter(LotteryAdapter):
    """
    Abstract base for all Caixa lotteries.

    Subclasses set class-level slots:

        game_slug       = "megasena"         # Caixa API path
        community_slug  = "mega-sena"        # community mirror path
        cache_file_name = "mega_sena.json"   # legacy local cache filename (ignored now)
        rules           = DrawRules(...)     # lottery rules
    """

    game_slug:       ClassVar[str]
    community_slug:  ClassVar[str]
    cache_file_name: ClassVar[str]

    # Subclasses may override
    timeout: float = 20.0
    max_concursos: int = 200   # cap for incremental fetch

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(self, limit: int | None = None) -> pd.DataFrame:
        """
        Fetch logic:
        0. Check Cooldown
        1. Query DB for max draw_id.
        2. Try community mirror if DB is empty.
        3. Try incremental Caixa fetch for missing draws.
        4. Return full history from DB (or limited).
        """
        # Resolve lottery ID for storage
        lottery_id = f"br/{self.community_slug}"
        
        # 0 — Check Cooldown
        cooldown_file = DATA_DIR / f".last_fetch_{self.game_slug}"
        cooldown_seconds = 4 * 3600
        import time
        now = time.time()
        
        if cooldown_file.exists():
            try:
                last_fetch = float(cooldown_file.read_text().strip())
                if now - last_fetch < cooldown_seconds:
                    remain = int((cooldown_seconds - (now - last_fetch)) / 60)
                    df = storage.load_draws(lottery_id, limit=limit)
                    if not df.empty:
                        max_cached = int(df["draw_id"].max())
                        latest_row = df[df["draw_id"] == max_cached].iloc[0]
                        latest_date = latest_row.get("draw_date") or "Unknown"
                        print(f"  Cache updated recently. Next check in {remain}m.", file=sys.stderr)
                        print(f"  Cache is up to date (Draw {max_cached} from {latest_date}).", file=sys.stderr)
                        df["date"] = pd.to_datetime(df["draw_date"], utc=True)
                        return df
            except Exception:
                pass

        # 1. Determine current state
        df_cached = storage.load_draws(lottery_id)
        max_cached = int(df_cached["draw_id"].max()) if not df_cached.empty else 0

        # 2. Try community bulk mirror if we have nothing
        if max_cached == 0:
            bulk_url = _COMMUNITY_BULK.format(slug=self.community_slug)
            try:
                print(f"  Trying community bulk mirror ({self.community_slug})…", file=sys.stderr)
                bulk_raw = self._get_json(bulk_url)
                if bulk_raw:
                    print(f"  ✓ {len(bulk_raw)} rows from bulk mirror", file=sys.stderr)
                    self._save_to_db(bulk_raw)
                    # Refresh cached state
                    df_cached = storage.load_draws(lottery_id)
                    max_cached = int(df_cached["draw_id"].max())
            except Exception as exc:
                logger.debug("Bulk mirror failed: %s", exc)

        # 3. Caixa incremental fetch (start from max_cached + 1)
        try:
            print(f"  Checking for new {self.game_slug} draws…", file=sys.stderr)
            new_draws = self._fetch_incremental(start_from=max_cached + 1)
            if new_draws:
                self._save_to_db(new_draws)
        except Exception as exc:
            print(f"  ✗ Incremental fetch failed: {exc}", file=sys.stderr)

        # 4. Final load from DB
        df = storage.load_draws(lottery_id, limit=limit)
        
        if df.empty:
            raise RuntimeError(
                f"0 draws found for {self.rules.name}. "
                "Check your internet connection and try again."
            )
            
        # Ensure correct types for the engine
        df["date"] = pd.to_datetime(df["draw_date"], errors="coerce", utc=True)
        # Drop rows with invalid/missing dates (prevents NaT errors in strategies)
        df = df.dropna(subset=["date"])
        
        return df

    def _save_to_db(self, raw_rows: List[Dict[str, Any]]):
        """Parse raw JSON rows and save to DuckDB."""
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
        
        lottery_id = f"br/{self.community_slug}"
        storage.save_draws(lottery_id, parsed)

    # ------------------------------------------------------------------
    # Incremental Fetch
    # ------------------------------------------------------------------

    def _fetch_incremental(self, start_from: int = 1) -> list[dict[str, Any]]:
        """Fetch latest draw, and walk forward from start_from."""
        latest_url = _CAIXA_LATEST.format(slug=self.game_slug)
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get(latest_url)
                resp.raise_for_status()
                latest = resp.json()
        except Exception as exc:
            logger.debug("Failed to fetch latest draw: %s", exc)
            return []

        current = int(latest.get("numero") or latest.get("numeroConcurso") or 0)
        if current == 0: return []
        
        if current < start_from:
            latest_date = latest.get("dataApuracao") or latest.get("data") or "Unknown"
            print(f"  Cache is up to date (Draw {current} from {latest_date}).", file=sys.stderr)
            return []

        # If we are missing too many draws, we cap it to max_draws to avoid 
        # long-running loops if the user hasn't fetched in years.
        fetch_start = max(start_from, current - self.max_concursos + 1)
        
        print(
            f"  Current draw: {current}. Fetching {current - fetch_start} new draws…",
            file=sys.stderr,
        )
        
        results = [latest]
        concurso_url = _CAIXA_CONCURSO.format(slug=self.game_slug, n="{n}")

        import concurrent.futures

        def fetch_draw(n: int) -> dict[str, Any] | None:
            try:
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    r = client.get(concurso_url.format(n=n))
                    r.raise_for_status()
                    return r.json()
            except Exception:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_n = {executor.submit(fetch_draw, n): n for n in range(fetch_start, current)}
            for future in concurrent.futures.as_completed(future_to_n):
                res = future.result()
                if res:
                    results.append(res)

        return results

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_draw(self, row: dict[str, Any]) -> Draw | None:
        """Normalise a Caixa or community mirror row into a Draw."""
        try:
            # ---- Format A (Bulk Mirror) ----
            if "dezenas" in row or "numbers" in row:
                draw_id = int(
                    row.get("draw_id")
                    or row.get("concurso")
                    or row.get("numeroConcurso")
                    or row.get("numero")
                    or 0
                )
                date = str(row.get("date") or row.get("data") or row.get("dataApuracao") or "1900-01-01")
                numbers = [int(n) for n in (row.get("numbers") or row.get("dezenas") or [])]

            # ---- Format B (Caixa API) ----
            elif "listaDezenas" in row:
                draw_id = int(
                    row.get("draw_id")
                    or row.get("numero")
                    or row.get("numeroConcurso")
                    or 0
                )
                date = str(row.get("date") or row.get("dataApuracao") or "1900-01-01")
                numbers = [int(n) for n in row["listaDezenas"]]


            else:
                logger.debug("Unknown row format — keys: %s", list(row.keys()))
                return None

            # Normalise Brazilian date DD/MM/YYYY → ISO YYYY-MM-DD
            if "/" in date:
                day, month, year = date.split("/")
                date = f"{year}-{month}-{day}"

            return Draw(draw_id=draw_id, date=date, numbers=numbers, bonus=[])

        except (KeyError, ValueError, TypeError) as exc:
            logger.debug("Parse error: %s — row keys: %s", exc, list(row.keys()))
            return None

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    @property
    def _cache_path(self) -> Path:
        return DATA_DIR / self.cache_file_name

    def _save_cache(self, raw: list[dict[str, Any]]) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2))
        logger.debug("Cache saved: %s (%d rows)", self._cache_path, len(raw))

    def _load_cache(self) -> list[dict[str, Any]]:
        if not self._cache_path.exists():
            return []
        try:
            return json.loads(self._cache_path.read_text())
        except json.JSONDecodeError as exc:
            logger.warning("Cache parse error: %s", exc)
            return []

    # ------------------------------------------------------------------
    # HTTP helper
    # ------------------------------------------------------------------

    def _get_json(self, url: str) -> list[dict[str, Any]]:
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        return []
