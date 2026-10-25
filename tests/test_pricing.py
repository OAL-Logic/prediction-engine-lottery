"""
Unit tests for Lottery Pricing & Multiple Bets Module 🏷️
"""

import pytest
from engine.modules.pricing import (
    get_lottery_pricing,
    get_multiple_bets,
    get_teimosinha_rules,
    calculate_bet_cost,
)


def test_mega_sena_pricing_and_multiples():
    pricing = get_lottery_pricing("br/mega-sena")
    assert pricing is not None
    assert pricing["currency"] == "BRL"
    assert pricing["single_bet"]["numbers"] == 6
    assert pricing["single_bet"]["price"] == 6.0

    multiples = get_multiple_bets("br/mega-sena")
    assert len(multiples) == 15  # 6 to 20 numbers

    # 7 numbers: 7 combinations * 6.0 = 42.0
    cost_7 = calculate_bet_cost("br/mega-sena", 7)
    assert cost_7 == 42.0

    # 8 numbers: 28 combinations * 6.0 = 168.0
    cost_8 = calculate_bet_cost("br/mega-sena", 8)
    assert cost_8 == 168.0

    # 10 numbers Teimosinha 3x: 210 * 6.0 * 3 = 3780.0
    cost_10_3x = calculate_bet_cost("br/mega-sena", 10, consecutive_draws=3)
    assert cost_10_3x == 3780.0

    teimosinha = get_teimosinha_rules("br/mega-sena")
    assert teimosinha["default_draws"] == 3
    assert 12 in teimosinha["allowed_draws"]


def test_lotofacil_pricing_and_multiples():
    pricing = get_lottery_pricing("br/lotofacil")
    assert pricing is not None
    assert pricing["single_bet"]["price"] == 3.5

    # 16 numbers: 16 * 3.5 = 56.0
    cost_16 = calculate_bet_cost("br/lotofacil", 16)
    assert cost_16 == 56.0

    # 16 numbers Teimosinha 6x: 16 * 3.5 * 6 = 336.0
    cost_16_6x = calculate_bet_cost("br/lotofacil", 16, consecutive_draws=6)
    assert cost_16_6x == 336.0

    # 17 numbers: 136 * 3.5 = 476.0
    cost_17 = calculate_bet_cost("br/lotofacil", 17)
    assert cost_17 == 476.0


def test_quina_pricing_and_multiples():
    pricing = get_lottery_pricing("br/quina")
    assert pricing is not None
    assert pricing["single_bet"]["price"] == 3.0

    # 6 numbers: 6 * 3.0 = 18.0
    cost_6 = calculate_bet_cost("br/quina", 6)
    assert cost_6 == 18.0

    # 7 numbers: 21 * 3.0 = 63.0
    cost_7 = calculate_bet_cost("br/quina", 7)
    assert cost_7 == 63.0


def test_mais_milionaria_pricing():
    pricing = get_lottery_pricing("br/mais-milionaria")
    assert pricing is not None
    assert pricing["single_bet"]["price"] == 6.0

    # 6 numbers + 3 trevos: C(6,6)*C(3,2) = 1*3 = 3 * 6.0 = 18.0
    cost_6_3t = calculate_bet_cost("br/mais-milionaria", 6, n_trevos=3)
    assert cost_6_3t == 18.0
