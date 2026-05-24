"""
Mega-Sena — Brazil (Caixa Econômica Federal)
============================================
Rules:  pick 6 numbers from 1–60
Draws:  Tuesday, Thursday & Saturday (3 times a week) (+ special Mega da Virada on 31 Dec)
Prize:  match 4 / 5 / 6 — jackpot rolls over until someone matches all 6 (every final 0 is a special draw that accumulates prizes from previous draws)
Source: CaixaBaseAdapter (br/caixa_base.py)

# Download the official Caixa CSV directly
curl -L "https://loteriascaixa-api.herokuapp.com/api/mega-sena" -o data/mega_sena_cache.json
# or wake up the Heroku dyno by just hitting it
curl -s "https://loteriascaixa-api.herokuapp.com/api/mega-sena" | wc -c
"""

from engine.adapters import DrawRules
from engine.adapters.br.caixa_base import CaixaBaseAdapter


class MegaSenaAdapter(CaixaBaseAdapter):
    game_slug       = "megasena"
    community_slug  = "mega-sena"
    cache_file_name = "br_mega_sena.json"

    rules = DrawRules(
        name="Mega-Sena",
        pick_count=6,
        number_range=(1, 60),
        prize_tiers=[4, 5, 6],
        ticket_price=5.0,
        currency="BRL",
        max_picks=20,
        odds={
            4: 2332,
            5: 154518,
            6: 50063860,
        }
    )
