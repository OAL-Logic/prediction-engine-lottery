"""
Global Lottery Registry 🌐
=========================
Loads and manages lottery definitions from data/registry.yaml.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from engine.adapters import DrawRules

DATA_DIR = Path(__file__).parent.parent.parent / "data"

@dataclass
class GameDefinition:
    id: str
    name: str
    pick_count: int
    pool_size: int
    bonus_count: int = 0
    bonus_pool: Optional[int] = None
    max_picks: Optional[int] = None
    ticket_price: float = 0.0
    currency: str = "USD"
    draw_days: List[str] = field(default_factory=list)
    draw_city: Optional[str] = None
    draw_lat: Optional[float] = None
    draw_lon: Optional[float] = None
    adapter: Optional[str] = None
    data_available: bool = False
    board_cols: int = 10

    def to_rules(self) -> DrawRules:
        return DrawRules(
            name=self.name,
            pick_count=self.pick_count,
            number_range=(1, self.pool_size),
            bonus_count=self.bonus_count,
            bonus_range=(1, self.bonus_pool) if self.bonus_pool else None,
            ticket_price=self.ticket_price,
            currency=self.currency,
            max_picks=self.max_picks,
            board_cols=self.board_cols
        )

class LotteryRegistry:
    _instance = None
    _games: Dict[str, GameDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        yaml_path = DATA_DIR / "registry.yaml"
        if not yaml_path.exists():
            return

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not data:
                return
            
            for item in data:
                game = GameDefinition(**item)
                self._games[game.id] = game
                # Also allow short-alias lookups if unique
                alias = game.id.split("/")[-1]
                if alias in self._games:
                    # If this is not the same game ID, we have a collision
                    if self._games[alias].id != game.id:
                        import logging
                        logging.warning(f"Alias collision: '{alias}' already points to {self._games[alias].id}. Skipping alias for {game.id}.")
                else:
                    self._games[alias] = game

    def get_game(self, slug: str) -> Optional[GameDefinition]:
        return self._games.get(slug)

    def list_games(self, only_available: bool = False) -> List[GameDefinition]:
        unique_games = {g.id: g for g in self._games.values()}
        games = list(unique_games.values())
        if only_available:
            return [g for g in games if g.data_available]
        return games

# Global singleton
registry = LotteryRegistry()
