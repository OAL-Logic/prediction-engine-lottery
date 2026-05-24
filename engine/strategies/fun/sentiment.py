"""
Sentiment Analysis Strategy 🎭
============================
Simulates 'Social Pulse' or digital popularity of numbers.

Theory:
-------
Numbers that are frequently discussed or 'trending' in social media 
simulations (based on current events, memes, or news dates) often see 
increased public betting volume. This strategy identifies these 'hot' 
public numbers to either follow (Sentiment mode) or avoid (Anti-Popular mode).
"""

from __future__ import annotations

import hashlib
import pandas as pd
from datetime import date
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


@register
class SentimentStrategy(BaseStrategy):
    name = "sentiment"
    description = "🎭 Social Sentiment — simulated digital popularity based on current trends/dates"
    tier = "fun"
    requires_history = 0

    def __init__(self, topic: str = "lottery", mode: str = "follow") -> None:
        """
        Parameters
        ----------
        topic
            A keyword or phrase to seed the sentiment simulation.
        mode
            'follow' (boost popular) or 'avoid' (penalize popular).
        """
        self.topic = topic
        self.mode = mode

    def score(self, df: pd.DataFrame, rules: DrawRules, **kwargs: Any) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        # Use the draw_date or current date to jitter the sentiment
        target_date = kwargs.get("draw_date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date[:10])
            
        # 1. Simulate "Trending Numbers" via deterministic hashing
        # SHA256(topic + date) -> used to pick a few 'viral' numbers
        seed_base = f"{self.topic}{target_date}"
        viral_hash = hashlib.sha256(seed_base.encode()).hexdigest()
        
        # Extract a few numbers from the hash
        viral_indices = [int(viral_hash[i:i+2], 16) % (hi - lo + 1) + lo for i in range(0, 10, 2)]
        viral_set = set(viral_indices)
        
        scores = {}
        for n in all_numbers:
            # Base sentiment: neutral 0.5
            s = 0.5
            
            # Viral boost
            if n in viral_set:
                s += 0.4
                
            # Date-related sentiment (today's day/month are always trending)
            if n == target_date.day or n == target_date.month:
                s += 0.2
                
            # Mode adjustment
            if self.mode == "avoid":
                s = 1.0 - s
                
            scores[n] = max(min(s, 1.0), 0.0)
            
        return scores
