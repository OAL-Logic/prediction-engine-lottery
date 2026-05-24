"""
Dupla Sena Adapter 🎭
====================
Adapter for Dupla Sena (pick 6, pool 50, two draws per concurso).
"""

from __future__ import annotations
from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter

class DuplaSenaAdapter(CaixaBaseAdapter):
    game_slug = "duplasena"
    community_slug = "dupla-sena"
    cache_file_name = "dupla_sena.json"
    rules = DrawRules(
        name="Dupla Sena",
        pick_count=6,
        number_range=(1, 50),
        board_cols=10,
        ticket_price=2.5,
        currency="BRL"
    )

    # Note: CaixaBaseAdapter default fetch logic handles the latest draw.
    # Dupla Sena has two draws. Our current storage schema typically expects 
    # one set of numbers per draw_id. We usually map Concurso N Draw 1 to 
    # draw_id N and potentially handle Draw 2 as a separate entity or 
    # additional metadata. For now, we follow the primary draw for consistency.
