"""
Storage Module 🗄️
================
Handles persistence for draw data using DuckDB as the primary source of truth,
with automated partitioned JSON exports for human inspection.
"""

from __future__ import annotations

import csv
import os
import json
import logging
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Dict, Tuple
import pandas as pd

from engine._paths import PROJECT_ROOT

try:
    import duckdb
    _HAS_DUCKDB = True
except ImportError:
    _HAS_DUCKDB = False

logger = logging.getLogger(__name__)

# --- Paths ---
BASE_DIR = PROJECT_ROOT
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "lottery.db"
INSPECTION_DIR = DATA_DIR / "inspections"
WHEEL_CACHE_JSON = DATA_DIR / "wheel_cache.json"


@dataclass
class PrecomputedWheel:
    """Represents a cached combinatorial covering design C(v, k, t, m)."""
    lottery_id: str
    v: int  # Candidate pool size
    k: int  # Ticket size
    t: int  # Guaranteed match condition
    m: int  # Drawn numbers condition
    ticket_count: int
    tickets: List[List[int]]
    theoretical_coverage: float  # Percentage (e.g., 100.0)


class LotteryStorage:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        # Policy: 'cache' (JSON is truth, DB is speed) or 'primary' (DB is truth)
        self.policy = os.environ.get("LOTTERY_STORAGE_POLICY", "cache").lower()
        # Engine: 'duckdb' or 'json' (forces no-DB)
        self.engine_type = os.environ.get("LOTTERY_STORAGE_ENGINE", "duckdb").lower()
        
        self.use_duckdb = _HAS_DUCKDB and self.engine_type == "duckdb"
        
        if self.use_duckdb:
            self._init_db()
            logger.info(f"Storage using DuckDB (Policy: {self.policy})")
        else:
            logger.info("Storage using JSON-only mode.")

    def _init_db(self):
        """Initialise DuckDB schema."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with duckdb.connect(str(self.db_path)) as con:
                con.execute("""
                    CREATE TABLE IF NOT EXISTS draws (
                        lottery_id TEXT,
                        draw_id INTEGER,
                        draw_date DATE,
                        numbers INTEGER[],
                        bonus INTEGER[],
                        raw_json JSON,
                        PRIMARY KEY (lottery_id, draw_id)
                    )
                """)
                con.execute("CREATE INDEX IF NOT EXISTS idx_lottery_date ON draws (lottery_id, draw_date)")
                con.execute("""
                    CREATE TABLE IF NOT EXISTS wheel_cache (
                        lottery_id VARCHAR,
                        v INTEGER,
                        k INTEGER,
                        t INTEGER,
                        m INTEGER,
                        ticket_count INTEGER,
                        tickets_json TEXT,
                        theoretical_coverage DOUBLE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (lottery_id, v, k, t, m)
                    )
                """)
        except Exception as e:
            # Fall back to read-only DuckDB or JSON-only mode if filesystem is read-only
            try:
                with duckdb.connect(str(self.db_path), read_only=True) as con:
                    logger.info("Storage using DuckDB in read-only mode.")
            except Exception:
                logger.warning(f"Could not initialize DuckDB ({e}), falling back to JSON-only mode.")
                self.use_duckdb = False

    def _get_inspection_dir(self, lottery_id: str) -> Path:
        return INSPECTION_DIR / lottery_id.replace("/", "_")

    def save_draws(self, lottery_id: str, draws: List[Dict[str, Any]]):
        """
        Save draws according to policy.
        """
        if not draws: return

        # 1. Canonicalise
        rows = []
        for d in draws:
            rows.append({
                "lottery_id": lottery_id,
                "draw_id": d["draw_id"],
                "draw_date": d.get("draw_date") or d.get("date"),
                "numbers": d["numbers"],
                "bonus": d.get("bonus", []),
                "raw_json": json.dumps(d)
            })

        # 2. Write to DB if enabled
        if self.use_duckdb:
            try:
                df = pd.DataFrame(rows)
                with duckdb.connect(str(self.db_path)) as con:
                    con.execute("CREATE TEMP TABLE temp_draws AS SELECT * FROM df")
                    con.execute("""
                        INSERT INTO draws 
                        SELECT * FROM temp_draws
                        ON CONFLICT (lottery_id, draw_id) DO UPDATE SET
                            draw_date = excluded.draw_date,
                            numbers = excluded.numbers,
                            bonus = excluded.bonus,
                            raw_json = excluded.raw_json
                    """)
                    con.execute("DROP TABLE temp_draws")
            except Exception as e:
                logger.warning(f"Could not write draws to DuckDB ({e}), writing to JSON partition.")

        # 3. Handle JSON Persistence (Partitioned by Year)
        # Always do this if policy is 'cache' or if no-DB.
        if self.policy == "cache" or not self.use_duckdb:
            with self._lock:
                out_dir = self._get_inspection_dir(lottery_id)
                out_dir.mkdir(parents=True, exist_ok=True)
                
                # Group new draws by year
                by_year = {}
                for d in rows:
                    y = str(pd.to_datetime(d["draw_date"]).year)
                    if y not in by_year: by_year[y] = []
                    by_year[y].append(d)
                
                for year, year_draws in by_year.items():
                    path = out_dir / f"{year}.json"
                    existing = []
                    if path.exists():
                        with open(path, "r") as f: existing = json.load(f)
                    
                    # Merge and sort
                    ids = {x["draw_id"] for x in existing}
                    combined = existing + [json.loads(d["raw_json"]) for d in year_draws if d["draw_id"] not in ids]
                    combined.sort(key=lambda x: x["draw_id"])
                    
                    with open(path, "w") as f:
                        json.dump(combined, f, indent=2)

    def load_draws(self, lottery_id: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Load draws according to policy."""
        # If Primary policy, always use DB
        if self.policy == "primary" and self.use_duckdb:
            query = "SELECT * FROM draws WHERE lottery_id = ? ORDER BY draw_id ASC"
            if limit:
                query = f"SELECT * FROM ({query}) ORDER BY draw_id DESC LIMIT {limit}"
            with duckdb.connect(str(self.db_path), read_only=True) as con:
                df = con.execute(query, [lottery_id]).df()
                return df.sort_values("draw_id").reset_index(drop=True)

        # Cache policy: Try DB first for speed, fallback to Partitioned JSON
        if self.use_duckdb:
            try:
                with duckdb.connect(str(self.db_path), read_only=True) as con:
                    count = con.execute("SELECT COUNT(*) FROM draws WHERE lottery_id = ?", [lottery_id]).fetchone()[0]
                    if count > 0:
                        query = "SELECT * FROM draws WHERE lottery_id = ? ORDER BY draw_id ASC"
                        if limit: query = f"SELECT * FROM ({query}) ORDER BY draw_id DESC LIMIT {limit}"
                        return con.execute(query, [lottery_id]).df().sort_values("draw_id").reset_index(drop=True)
            except Exception:
                pass

        # Fallback: Load from yearly JSON partitions
        out_dir = self._get_inspection_dir(lottery_id)
        if not out_dir.exists():
            # Legacy check: single file in data/
            legacy = DATA_DIR / f"{lottery_id.replace('/', '_')}.json"
            if legacy.exists():
                df = pd.read_json(legacy)
                return df.tail(limit) if limit else df
            return pd.DataFrame(columns=["draw_id", "draw_date", "numbers", "bonus"])

        all_data = []
        for p in sorted(out_dir.glob("*.json")):
            with open(p, "r") as f:
                all_data.extend(json.load(f))
        
        df = pd.DataFrame(all_data)
        if df.empty: return df
        
        if "date" in df.columns and "draw_date" not in df.columns:
            df = df.rename(columns={"date": "draw_date"})
        
        df = df.sort_values("draw_id")
        if limit:
            df = df.tail(limit)
        return df.reset_index(drop=True)

    def export_to_json(self, lottery_id: str):
        """
        Export full history to partitioned JSON files (By Year).
        """
        if not self.use_duckdb: return
        
        out_dir = INSPECTION_DIR / lottery_id.replace("/", "_")
        out_dir.mkdir(parents=True, exist_ok=True)

        with duckdb.connect(str(self.db_path)) as con:
            years = con.execute("""
                SELECT DISTINCT EXTRACT(YEAR FROM draw_date) as year 
                FROM draws WHERE lottery_id = ?
            """, [lottery_id]).fetchall()

            for (year,) in years:
                if year is None: continue
                year_int = int(year)
                draws_df = con.execute("""
                    SELECT draw_id, draw_date, numbers, bonus
                    FROM draws 
                    WHERE lottery_id = ? AND EXTRACT(YEAR FROM draw_date) = ?
                    ORDER BY draw_id ASC
                """, [lottery_id, year_int]).df()
                
                draws_df['draw_date'] = draws_df['draw_date'].astype(str)
                file_path = out_dir / f"{year_int}.json"
                draws_df.to_json(file_path, orient="records", indent=2)
                
        logger.info(f"Exported {lottery_id} to {out_dir}")

    def _wheel_cache_json_path(self) -> Path:
        if self.db_path != DB_PATH:
            return self.db_path.with_suffix(".wheels.json")
        return WHEEL_CACHE_JSON

    def get_precomputed_wheel(
        self,
        lottery_id: str,
        v: int,
        k: int,
        t: int,
        m: int,
    ) -> Optional[PrecomputedWheel]:
        """Retrieve precomputed covering design from cache if available."""
        if self.use_duckdb and _HAS_DUCKDB:
            try:
                with duckdb.connect(str(self.db_path), read_only=True) as con:
                    row = con.execute("""
                        SELECT ticket_count, tickets_json, theoretical_coverage
                        FROM wheel_cache
                        WHERE lottery_id = ? AND v = ? AND k = ? AND t = ? AND m = ?
                    """, [lottery_id, v, k, t, m]).fetchone()
                    if row:
                        ticket_count, tickets_json, cov = row
                        return PrecomputedWheel(
                            lottery_id=lottery_id,
                            v=v,
                            k=k,
                            t=t,
                            m=m,
                            ticket_count=int(ticket_count),
                            tickets=json.loads(tickets_json),
                            theoretical_coverage=float(cov),
                        )
            except Exception as e:
                logger.debug(f"DuckDB wheel query note: {e}")

        json_path = self._wheel_cache_json_path()
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                key = f"{lottery_id}:{v}:{k}:{t}:{m}"
                if key in data:
                    entry = data[key]
                    return PrecomputedWheel(
                        lottery_id=lottery_id,
                        v=v,
                        k=k,
                        t=t,
                        m=m,
                        ticket_count=int(entry["ticket_count"]),
                        tickets=entry["tickets"],
                        theoretical_coverage=float(entry["theoretical_coverage"]),
                    )
            except Exception:
                pass
        return None

    def save_precomputed_wheel(self, wheel: PrecomputedWheel) -> None:
        """Store a precomputed covering design into the wheel cache."""
        tickets_json = json.dumps(wheel.tickets)
        if self.use_duckdb and _HAS_DUCKDB:
            try:
                with duckdb.connect(str(self.db_path)) as con:
                    con.execute("""
                        INSERT OR REPLACE INTO wheel_cache
                        (lottery_id, v, k, t, m, ticket_count, tickets_json, theoretical_coverage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        wheel.lottery_id,
                        wheel.v,
                        wheel.k,
                        wheel.t,
                        wheel.m,
                        wheel.ticket_count,
                        tickets_json,
                        wheel.theoretical_coverage,
                    ])
                return
            except Exception as e:
                logger.debug(f"DuckDB wheel save note: {e}")

        json_path = self._wheel_cache_json_path()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        data: Dict[str, Any] = {}
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        key = f"{wheel.lottery_id}:{wheel.v}:{wheel.k}:{wheel.t}:{wheel.m}"
        data[key] = {
            "ticket_count": wheel.ticket_count,
            "tickets": wheel.tickets,
            "theoretical_coverage": wheel.theoretical_coverage,
        }
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def ingest_file(
        self,
        file_path: Path,
        lottery_id: str,
        rules: Optional[Any] = None,
        dry_run: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Ingest historical data from JSON, CSV (comma or semicolon delimited),
        or flat TXT/DAT files into LotteryStorage.
        Respects universal game rules (number_range, pick_count, bonus_count).
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Historical file not found: {file_path}")

        lo, hi = rules.number_range if rules is not None else (0, 100)
        pick_count = rules.pick_count if rules is not None else None
        bonus_count = getattr(rules, "bonus_count", 0) if rules is not None else 0

        records: List[Dict[str, Any]] = []
        suffix = file_path.suffix.lower()

        if suffix == ".json":
            content = file_path.read_text(encoding="utf-8", errors="replace")
            data = json.loads(content)
            items = data if isinstance(data, list) else data.get("draws", [data])
            for item in items:
                draw_id = item.get("draw_id") or item.get("concurso") or item.get("numero")
                if draw_id is None:
                    continue
                d_date = str(item.get("draw_date") or item.get("date") or item.get("data") or item.get("dataApuracao") or "")
                if d_date and "/" in d_date:
                    parts = d_date.split("/")
                    if len(parts) == 3:
                        d_date = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                nums = item.get("numbers") or item.get("dezenas") or item.get("listaDezenas") or []
                nums_int = [int(n) for n in nums if str(n).lstrip("-").isdigit() and lo <= int(n) <= hi]
                bonus = item.get("bonus") or []
                bonus_int = [int(b) for b in bonus if str(b).lstrip("-").isdigit()]
                if nums_int:
                    records.append({
                        "draw_id": int(draw_id),
                        "draw_date": d_date[:10],
                        "numbers": sorted(nums_int),
                        "bonus": sorted(bonus_int),
                    })

        elif suffix == ".csv":
            with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
                first_line = f.readline()
                delim = ";" if ";" in first_line else ","
                f.seek(0)
                reader = csv.reader(f, delimiter=delim)
                header = [h.strip().lower() for h in next(reader, [])]
                concurso_idx = next((i for i, h in enumerate(header) if "concurso" in h or "draw" in h), 0)
                data_idx = next((i for i, h in enumerate(header) if "data" in h or "date" in h), 1)

                for row in reader:
                    if not row or len(row) <= 2:
                        continue
                    try:
                        draw_id = int(re.sub(r"\D", "", row[concurso_idx]))
                        raw_date = row[data_idx].strip()
                        if "/" in raw_date:
                            p = raw_date.split("/")
                            iso_date = f"{p[2]}-{p[1].zfill(2)}-{p[0].zfill(2)}"
                        else:
                            iso_date = raw_date[:10]

                        all_vals: List[int] = []
                        for col in row[data_idx + 1:]:
                            clean = re.sub(r"\D", "", col)
                            if clean:
                                all_vals.append(int(clean))

                        if pick_count:
                            main_nums = [v for v in all_vals[:pick_count] if lo <= v <= hi]
                            bonus_nums = all_vals[pick_count:pick_count + bonus_count] if bonus_count > 0 else []
                        else:
                            main_nums = [v for v in all_vals if lo <= v <= hi]
                            bonus_nums = []

                        if main_nums:
                            records.append({
                                "draw_id": draw_id,
                                "draw_date": iso_date,
                                "numbers": sorted(main_nums),
                                "bonus": sorted(bonus_nums),
                            })
                    except Exception:
                        continue

        elif suffix in [".txt", ".dat"]:
            from desktop.src.utils.converter import parse_studio_txt
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if pick_count:
                records = parse_studio_txt(
                    file_content=content,
                    pick_count=pick_count,
                    bonus_count=bonus_count,
                )
            else:
                draw_counter = 1
                for line in content.splitlines():
                    tokens = line.strip().split()
                    if len(tokens) < 2:
                        continue
                    d_token, nums_tokens = tokens[0], tokens[1:]
                    iso_date = d_token
                    if "/" in d_token:
                        dp = d_token.split("/")
                        if len(dp) == 3:
                            m_s, d_s, y_s = dp[0].zfill(2), dp[1].zfill(2), dp[2]
                            if len(y_s) == 2:
                                y_s = f"20{y_s}" if int(y_s) < 50 else f"19{y_s}"
                            iso_date = f"{y_s}-{m_s}-{d_s}"
                    nums_int = [int(x) for x in nums_tokens if x.isdigit() and lo <= int(x) <= hi]
                    if nums_int:
                        records.append({
                            "draw_id": draw_counter,
                            "draw_date": iso_date,
                            "numbers": sorted(nums_int),
                            "bonus": [],
                        })
                        draw_counter += 1

        if records and not dry_run:
            self.save_draws(lottery_id, records)
        return records

    def validate_environment(self, lottery_id: str) -> Tuple[bool, str]:
        """
        Validate that historical draw records exist for `lottery_id`.
        Returns (is_valid, diagnostic_message).
        """
        df = self.load_draws(lottery_id, limit=5)
        if not df.empty:
            return True, f"Found historical draws for {lottery_id} in storage ({self.db_path})."
        msg = (
            f"\n[!] DIAGNOSTIC ERROR: No historical draws found for '{lottery_id}' in local storage ({self.db_path}).\n"
            f"Remediation options via p4lottery:\n"
            f"  1. Fetch directly from official adapter sources:\n"
            f"     ./p4lottery fetch {lottery_id}\n"
            f"  2. Or import a local historical export (.csv, .json, .txt):\n"
            f"     ./p4lottery import-drawings {lottery_id} <path-to-file>\n"
        )
        return False, msg


# Global singleton
storage = LotteryStorage()
