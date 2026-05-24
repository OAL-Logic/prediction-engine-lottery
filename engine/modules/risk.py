"""
Risk Management Module ⚖️
=========================
Implements the Kelly Criterion and bankroll optimization logic.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class KellyResult:
    fraction: float
    bet_amount: float
    tickets: int
    confidence: float
    is_safe: bool

def calculate_kelly_bet(
    bankroll: float,
    ticket_price: float,
    jackpot_odds: float,
    confidence: float,
    fractional_factor: float = 0.25, # Quarter Kelly as default
    min_confidence: float = 0.2
) -> KellyResult:
    """
    Calculates the optimal bet size using the Kelly Criterion.
    
    Formula: f* = (p * b - q) / b
    b = Net Odds (Decimal Odds - 1)
    p = Probability of winning
    q = Probability of losing (1 - p)
    """
    # 1. Base Probability (Random)
    p_base = 1.0 / jackpot_odds
    
    # 2. Adjusted Probability (System Edge)
    # We treat confidence as a lift factor. 
    # High confidence (1.0) might double the base probability or provide a fixed boost.
    # For lotteries, even a 100x lift is still a small p.
    # Simplified approach for v10.0:
    p_adjusted = p_base * (1.0 + (confidence * 10.0)) # Assuming system can provide up to 10x lift
    
    q = 1.0 - p_adjusted
    
    # b = Net Odds (e.g. if jackpot is 1M and price is 5, odds are 200,000:1)
    # In lottery, b is huge.
    b = jackpot_odds - 1.0
    
    # Kelly Fraction
    if b <= 0:
        return KellyResult(0.01, ticket_price, 1, confidence, False)
        
    f_star = (p_adjusted * b - q) / b
    
    # Apply fractional Kelly (conservative)
    safe_fraction = max(0.001, f_star * fractional_factor)
    
    # Calculate amounts
    bet_amount = bankroll * safe_fraction
    # Ensure at least 1 ticket if we are betting
    num_tickets = max(1, math.floor(bet_amount / ticket_price))
    
    return KellyResult(
        fraction=safe_fraction,
        bet_amount=num_tickets * ticket_price,
        tickets=num_tickets,
        confidence=confidence,
        is_safe=(confidence >= min_confidence)
    )
