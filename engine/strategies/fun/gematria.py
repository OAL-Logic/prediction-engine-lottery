"""
Gematria Resonance Strategy 🔤
============================
Scores numbers by the Gematria value of their names (One, Two, Three...).

Theory:
-------
Words have numerical power. By mapping a number's name to its Chaldean or 
Pythagorean value, we can correlate it with the user's name or the 
contextual 'topic' of the day.
"""

from __future__ import annotations

import pandas as pd
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class GematriaStrategy(BaseStrategy):
    name = "gematria"
    description = "🔤 Gematria Resonance — linguistic mapping of number names to personal vibrations"
    tier = "fun"
    requires_history = 0

    def __init__(self, language: str = "en") -> None:
        self.language = language.lower()
        
    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # 1. Get Target Vibration (Topic or Full Name)
        target = kwargs.get("topic") or kwargs.get("full_name") or "LOTTERY"
        target_vibe = self._get_gematria(target)
        
        # 2. Score each number based on its name resonance
        scores = {}
        for n in all_numbers:
            name = self._num_to_name(n)
            vibe = self._get_gematria(name)
            
            # Resonance = inverse distance between vibrations (1-9 reduced)
            diff = abs(target_vibe - vibe)
            scores[n] = 1.0 / (diff + 1)
            
        return scores

    def _get_gematria(self, text: str) -> int:
        """Chaldean Mapping (1-8)"""
        mapping = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5,
            'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8,
            'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5,
            'Y': 1, 'Z': 7
        }
        total = sum(mapping.get(c.upper(), 0) for c in text if c.isalpha())
        # Reduce to root (1-9)
        while total > 9:
            total = sum(int(d) for d in str(total))
        return total

    def _num_to_name(self, n: int) -> str:
        """Crude conversion for 1-100"""
        if self.language == "pt":
            names = {
                1: "um", 2: "dois", 3: "tres", 4: "quatro", 5: "cinco",
                6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez",
                11: "onze", 12: "doze", 13: "treze", 14: "quatorze", 15: "quinze",
                16: "dezesseis", 17: "dezessete", 18: "dezoito", 19: "dezenove", 20: "vinte",
                30: "trinta", 40: "quarenta", 50: "cinquenta", 60: "sessenta", 70: "setenta",
                80: "oitenta", 90: "noventa", 100: "cem"
            }
        else:
            names = {
                1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
                11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
                16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
                30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy",
                80: "eighty", 90: "ninety", 100: "hundred"
            }
            
        if n in names:
            return names[n]
        
        # Compound names (21-99)
        tens = (n // 10) * 10
        ones = n % 10
        if tens in names and ones in names:
            sep = " e " if self.language == "pt" else "-"
            return f"{names[tens]}{sep}{names[ones]}"
            
        return str(n)
