"""
Quina Adapter 🪙
================
Adapter for Quina (pick 5, pool 80).
"""

from __future__ import annotations
from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter

class QuinaAdapter(CaixaBaseAdapter):
    game_slug = "quina"
    community_slug = "quina"
    cache_file_name = "quina.json"
    rules = DrawRules(
        name="Quina",
        pick_count=5,
        number_range=(1, 80),
        board_cols=10,
        ticket_price=2.5,
        currency="BRL"
    )
