"""
Mais Milionária Adapter 🏆
==========================
Adapter for +Milionária (pick 6 from 50, plus 2 trevos from 6).
"""

from __future__ import annotations
from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter

class MaisMilionariaAdapter(CaixaBaseAdapter):
    game_slug = "maismilionaria"
    community_slug = "mais-milionaria"
    cache_file_name = "mais_milionaria.json"
    rules = DrawRules(
        name="+Milionária",
        pick_count=6,
        number_range=(1, 50),
        bonus_count=2,
        bonus_range=(1, 6),
        board_cols=10,
        ticket_price=6.0,
        currency="BRL"
    )
