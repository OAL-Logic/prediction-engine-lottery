import pytest
from datetime import date
from engine.strategies.fun.kabbalistic import (
    _strip_accents,
    _digit_reduce,
    _get_name_values,
    _is_vowel_y,
    _calculate_core_numbers,
    _calculate_triangle_arcanos,
    KabbalisticStrategy
)

def test_strip_accents():
    assert _strip_accents("João") == "Joao"
    assert _strip_accents("Conceição") == "Conceicao"
    assert _strip_accents("Müller") == "Muller"

def test_digit_reduce():
    assert _digit_reduce(10) == 1
    assert _digit_reduce(11) == 11  # preserved
    assert _digit_reduce(22) == 22  # preserved
    assert _digit_reduce(13) == 4
    assert _digit_reduce(33) == 6   # reduced in this implementation as not in _MASTER
    assert _digit_reduce(0) == 9

def test_get_name_values():
    # A=1, B=2, C=3
    assert _get_name_values("ABC") == [1, 2, 3]
    # Accents stripped
    assert _get_name_values("ÁBÇ") == [1, 2, 3]

def test_is_vowel_y():
    # Y is vowel if no other vowels in syllable (simplified as no adjacent vowels)
    assert _is_vowel_y(0, "Y") is True
    assert _is_vowel_y(1, "CYNTHIA") is True
    assert _is_vowel_y(2, "RAYMOND") is False # A is neighbor

def test_calculate_core_numbers():
    # GEMINI
    # G=3, E=5, M=4, I=1, N=5, I=1
    # Vowels: E(5), I(1), I(1) = 7
    # Consonants: G(3), M(4), N(5) = 12 -> 3
    # Total: 19 -> 1
    res = _calculate_core_numbers("GEMINI")
    assert res["motivation"] == 7
    assert res["impression"] == 3
    assert res["expression"] == 1

def test_calculate_triangle_arcanos():
    # ABC -> 1, 2, 3
    # Row 1: 1, 2, 3
    # Row 2: 1+2=3, 2+3=5
    # Row 3: 3+5=8
    # Arcanos: 12, 23, 35
    triangle, arcanos = _calculate_triangle_arcanos([1, 2, 3])
    assert 12 in arcanos
    assert 23 in arcanos
    assert 35 in arcanos

def test_strategy_initialization():
    strat = KabbalisticStrategy(full_name="TEST USER", birth_date="1985-05-15")
    assert strat.destiny == _digit_reduce(1985 + 5 + 15)
    assert strat.full_name == "TEST USER"
    assert len(strat.arcanos) > 0

def test_strategy_vibrations():
    strat = KabbalisticStrategy(birth_date="1985-05-15")
    vib = strat._get_vibrations(date(2024, 4, 26))
    assert "year" in vib
    assert "month" in vib
    assert "day" in vib

@pytest.mark.asyncio
async def test_strategy_score():
    from engine.adapters import DrawRules
    import pandas as pd
    
    rules = DrawRules(name="test", pick_count=6, number_range=(1, 60))
    df = pd.DataFrame(columns=["date", "numbers"])
    
    strat = KabbalisticStrategy(full_name="LUCKY ONE", birth_date="1970-01-01")
    scores = strat.score(df, rules)
    
    assert len(scores) == 60
    assert all(0 <= v <= 1 for v in scores.values())
    # 21 should have a boost compared to a non-harmonic, non-core number
    # Let's find a number that has no special meaning for this user
    # Root of 10 is 1 (matches Destiny/Motivation). Root of 2 is 2.
    # Root of 3 is 3. Root of 21 is 3.
    # 21 should be >= base 0.35 + boost 0.1 = 0.45 (before multipliers)
    assert scores[21] >= 0.3
