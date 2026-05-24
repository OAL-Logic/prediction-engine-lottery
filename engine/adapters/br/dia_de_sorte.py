"""
Dia de Sorte Adapter 🍀
=======================
Adapter for Dia de Sorte (pick 7, pool 31, plus 1 month).
"""

from __future__ import annotations
from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter

class DiaDeSorteAdapter(CaixaBaseAdapter):
    game_slug = "diadesorte"
    community_slug = "dia-de-sorte"
    cache_file_name = "dia_de_sorte.json"
    rules = DrawRules(
        name="Dia de Sorte",
        pick_count=7,
        number_range=(1, 31),
        bonus_count=1,
        bonus_range=(1, 12),
        board_cols=7,
        ticket_price=2.5,
        currency="BRL"
    )
