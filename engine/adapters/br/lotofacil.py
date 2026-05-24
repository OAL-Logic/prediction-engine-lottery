"""
Lotofácil — Brazil (Caixa Econômica Federal)
=============================================
Rules:  pick 15 numbers from 1–25
Draws:  Monday through Saturday (6× / week — most frequent Caixa game)
Prizes: match 11 / 12 / 13 / 14 / 15 numbers
        - prizes at 11+ make this the lottery with the highest win-rate in BR
        - jackpot always pays out (no rollover tier for 15-match)
        - every final 0 is a special draw that accumulates prizes from previous draws
Source: CaixaBaseAdapter (br/caixa_base.py)

Note on "localized jackpot"
-----------------------------
Lotofácil does NOT have a localized (city/state) jackpot split — winners
share the prize pool equally regardless of location. Regional breakdowns
exist in the raw Caixa API response (listaMunicipioUFGanhadores) but are
not relevant to draw analysis; they are ignored here.
"""

from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter


class LotofacilAdapter(CaixaBaseAdapter):
    game_slug       = "lotofacil"
    community_slug  = "lotofacil"
    cache_file_name = "br_lotofacil.json"

    rules = DrawRules(
        name="Lotofácil",
        pick_count=15,
        number_range=(1, 25),
        prize_tiers=[11, 12, 13, 14, 15],
        ticket_price=3.0,
        currency="BRL",
        max_picks=20,
        odds={
            11: 11,
            12: 59,
            13: 691,
            14: 21791,
            15: 3268760,
        },
        board_cols=5
    )
