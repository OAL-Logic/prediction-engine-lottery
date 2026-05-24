"""
Lotomania Adapter 🎡
====================
Adapter for Lotomania (pick 50, pool 100).
"""

from __future__ import annotations
from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter

class LotomaniaAdapter(CaixaBaseAdapter):
    game_slug = "lotomania"
    community_slug = "lotomania"
    cache_file_name = "lotomania.json"
    rules = DrawRules(
        name="Lotomania",
        pick_count=50,
        number_range=(0, 99),
        board_cols=10,
        ticket_price=3.0,
        currency="BRL"
    )
