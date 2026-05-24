"""
Storage Module 🗄️
================
Handles persistence for draw data using DuckDB as the primary source of truth,
with automated partitioned JSON exports for human inspection.
"""

from __future__ import annotations

import os
import json
import logging
import threading
from pathlib import Path
from typing import Any, List, Optional, Dict
import pandas as pd

try:
    import duckdb
    _HAS_DUCKDB = True
except ImportError:
    _HAS_DUCKDB = False

logger = logging.getLogger(__name__)

# --- Paths ---
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "lottery.db"
INSPECTION_DIR = DATA_DIR / "inspections"

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
            with duckdb.connect(str(self.db_path)) as con:
                df = con.execute(query, [lottery_id]).df()
                return df.sort_values("draw_id").reset_index(drop=True)

        # Cache policy: Try DB first for speed, fallback to Partitioned JSON
        if self.use_duckdb:
            try:
                with duckdb.connect(str(self.db_path)) as con:
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

# Global singleton
storage = LotteryStorage()
