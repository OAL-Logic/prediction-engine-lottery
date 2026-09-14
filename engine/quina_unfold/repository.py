"""
DrawRepository — ingestion interface for Quina history + the prior draw.
==========================================================================
Thin adapter over the existing `QuinaAdapter` / `storage` singleton so the
rest of the pipeline never touches fetch/cache/DB details directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from engine.adapters import Draw, DrawRules
from engine.adapters.br.quina import QuinaAdapter
from engine.adapters.registry import registry
from engine.modules.storage import storage


@dataclass
class PriorDraw:
    draw_id: int
    date: str
    numbers: List[int]


class DrawRepository:
    """
    Ingestion interface for historical Quina draws and the immediate prior draw.

    Autonomously ingests via QuinaAdapter.fetch() (community mirror -> Caixa
    incremental API -> local DuckDB/JSON cache, in that order — see
    CaixaBaseAdapter), so callers never need to know where the data lives.
    """

    def __init__(self, adapter: Optional[QuinaAdapter] = None):
        self.adapter = adapter or QuinaAdapter()
        self.rules: DrawRules = self.adapter.rules
        self._df: Optional[pd.DataFrame] = None

    def load_history(self, refresh: bool = True, limit: Optional[int] = None, source: str = "auto") -> pd.DataFrame:
        """
        Return the canonical draw history (draw_id, date, numbers, bonus),
        sorted ascending.

        source="auto"  : full production path — community mirror -> Caixa
                          incremental API -> local cache (QuinaAdapter.fetch).
        source="cache" : skip network entirely, read straight from the
                          existing DuckDB/JSON store (offline / CI / repeated
                          pipeline runs where a fresher fetch already ran).
        """
        if self._df is not None and not refresh:
            return self._df

        if source == "cache":
            df = storage.load_draws(f"br/{self.adapter.community_slug}", limit=limit)
            df["date"] = pd.to_datetime(df["draw_date"], errors="coerce", utc=True)
            df = df.dropna(subset=["date"]).sort_values("draw_id").reset_index(drop=True)
        else:
            df = self.adapter.fetch(limit=limit)

        self._df = df
        return self._df

    def get_prior_draw(self) -> PriorDraw:
        """The single most recent official draw — the anchor for repeat/adjacency telemetry."""
        df = self.load_history(refresh=False)
        if df.empty:
            raise RuntimeError("No Quina history available — cannot resolve prior draw.")
        row = df.sort_values("draw_id").iloc[-1]
        return PriorDraw(draw_id=int(row["draw_id"]), date=str(row["date"]), numbers=sorted(row["numbers"]))

    def get_target_draw_id(self, explicit: Optional[int] = None) -> int:
        """
        The draw this pool is being built for. If not given explicitly, it is
        the prior draw's id + 1 — i.e. "the next draw to be played".
        """
        if explicit is not None:
            return explicit
        return self.get_prior_draw().draw_id + 1

    def game_definition(self):
        return registry.get_game("quina")
