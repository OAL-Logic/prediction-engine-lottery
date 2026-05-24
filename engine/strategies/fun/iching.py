"""
I Ching Resonance Strategy ☯️
=============================
Casts a daily hexagram from the Book of Changes to find 'Transformative Numbers'.

Theory:
-------
The I Ching (Book of Changes) uses 64 hexagrams to describe the flow of 
universal states. Many lotteries (like Mega-Sena, 1-60) fit neatly within 
this 64-state space. By casting a hexagram for the draw date, we identify 
the 'Current State' and its 'Changing Lines' (the numbers it will transform into).

How it works:
-------------
1. Uses the draw date and the Intentional Seed to simulate the 'Yarrow Stalk' casting method.
2. Identifies the Primary Hexagram (1-64).
3. Identifies the Transformed Hexagram based on changing lines (Yin/Yang dynamics).
4. Boosts the numbers corresponding to these hexagrams and the specific changing lines.
"""

from __future__ import annotations

import pandas as pd
import hashlib
from datetime import date
import random

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

# Hexagram names for flavour
_HEXAGRAMS = {
    1: "Qian (The Creative)", 2: "Kun (The Receptive)", 3: "Chun (Difficulty at Beginning)",
    4: "Meng (Youthful Folly)", 5: "Xu (Waiting)", 6: "Song (Conflict)", 
    7: "Shi (The Army)", 8: "Bi (Holding Together)", 9: "Xiao Xu (Small Taming)", 
    10: "Lu (Treading)", 11: "Tai (Peace)", 12: "Pi (Standstill)", 
    13: "Tong Ren (Fellowship)", 14: "Da You (Great Possession)", 15: "Qian (Modesty)", 
    16: "Yu (Enthusiasm)", 17: "Sui (Following)", 18: "Gu (Work on Decay)", 
    19: "Lin (Approach)", 20: "Guan (Contemplation)", 21: "Shi He (Biting Through)", 
    22: "Bi (Grace)", 23: "Bo (Splitting Apart)", 24: "Fu (Return)", 
    25: "Wu Wang (Innocence)", 26: "Da Xu (Great Taming)", 27: "Yi (Corners of Mouth)", 
    28: "Da Guo (Preponderance of Great)", 29: "Kan (The Abysmal)", 30: "Li (The Clinging)", 
    31: "Xian (Influence)", 32: "Heng (Duration)", 33: "Dun (Retreat)", 
    34: "Da Zhuang (Great Power)", 35: "Jin (Progress)", 36: "Ming Yi (Darkening of Light)", 
    37: "Jia Ren (The Family)", 38: "Kui (Opposition)", 39: "Jian (Obstruction)", 
    40: "Jie (Deliverance)", 41: "Sun (Decrease)", 42: "Yi (Increase)", 
    43: "Guai (Breakthrough)", 44: "Gou (Coming to Meet)", 45: "Cui (Gathering Together)", 
    46: "Sheng (Pushing Upward)", 47: "Kun (Oppression)", 48: "Jing (The Well)", 
    49: "Ge (Revolution)", 50: "Ding (The Cauldron)", 51: "Zhen (The Arousing)", 
    52: "Gen (Keeping Still)", 53: "Jian (Development)", 54: "Gui Mei (Marrying Maiden)", 
    55: "Feng (Abundance)", 56: "Lu (The Wanderer)", 57: "Xun (The Gentle)", 
    58: "Dui (The Joyous)", 59: "Huan (Dispersion)", 60: "Jie (Limitation)", 
    61: "Zhong Fu (Inner Truth)", 62: "Xiao Guo (Preponderance of Small)", 
    63: "Ji Ji (After Completion)", 64: "Wei Ji (Before Completion)"
}

@register
class IChingStrategy(BaseStrategy):
    name = "iching"
    description = "☯️ I Ching Resonance — Hexagram casting and Transformative Lines"
    tier = "fun"
    requires_history = 1

    def __init__(self, draw_date: date | str | None = None) -> None:
        if isinstance(draw_date, str) and draw_date.strip() and draw_date != "None":
            self.draw_date = date.fromisoformat(draw_date[:10])
        else:
            self.draw_date = date.today()
        self._meta = {}

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Deterministic cast based on date (Yarrow stalk simulation)
        seed_str = f"iching_{self.draw_date.isoformat()}"
        cast_seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(cast_seed)
        
        # Yarrow stalk probabilities: 
        # 6 (Old Yin - Changing) : 1/16
        # 7 (Young Yang)         : 5/16
        # 8 (Young Yin)          : 7/16
        # 9 (Old Yang - Changing): 3/16
        lines = []
        for _ in range(6):
            r = rng.randint(1, 16)
            if r == 1: lines.append(6)
            elif r <= 6: lines.append(7)
            elif r <= 13: lines.append(8)
            else: lines.append(9)
            
        # Identify changing lines (6 and 9)
        changing_indices = [i + 1 for i, val in enumerate(lines) if val in (6, 9)]
        
        # Build Primary Hexagram (map binary to 1-64)
        # Yin (6, 8) = 0, Yang (7, 9) = 1
        binary_primary = "".join("1" if l in (7, 9) else "0" for l in lines)
        primary_val = int(binary_primary, 2) + 1 # 1 to 64
        
        # Build Transformed Hexagram
        # 6 becomes 7 (Yin -> Yang), 9 becomes 8 (Yang -> Yin)
        transformed_lines = [7 if l == 6 else 8 if l == 9 else l for l in lines]
        binary_transform = "".join("1" if l in (7, 9) else "0" for l in transformed_lines)
        transform_val = int(binary_transform, 2) + 1
        
        # Normalize to lottery range
        def _map_to_pool(val: int) -> int:
            return ((val - 1) % hi) + 1
            
        primary_num = _map_to_pool(primary_val)
        transform_num = _map_to_pool(transform_val)
        
        self._meta = {
            "primary_hexagram": f"{primary_val}. {_HEXAGRAMS.get(primary_val, 'Unknown')}",
            "transformed_hexagram": f"{transform_val}. {_HEXAGRAMS.get(transform_val, 'Unknown')}" if changing_indices else "No changing lines (Static State)",
            "changing_lines": changing_indices
        }
        
        scores = {n: 0.5 for n in all_numbers}
        
        # Boost primary and transformed hexagrams
        if primary_num in scores: scores[primary_num] += 0.4
        if transform_num in scores and changing_indices: scores[transform_num] += 0.3
        
        # Boost numbers related to the changing lines
        for line_idx in changing_indices:
            # Map the line index (1-6) to multiples across the pool
            for mult in range(1, (hi // 6) + 2):
                target = line_idx * mult
                if target in scores:
                    scores[target] += 0.1
                    
        # Normalize
        max_s = max(scores.values()) or 1.0
        return {n: min(v / max_s, 1.0) for n, v in scores.items()}

    def suggest(self, *args, **kwargs):
        result = super().suggest(*args, **kwargs)
        result.metadata.update(self._meta)
        return result
