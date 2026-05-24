"""
Decision Matrix Module 🧠
========================
Synthesizes high-fidelity strategic snapshots for daily briefings.
Combines performance metrics, risk assessment, and logic assumptions.
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

from engine.adapters import DrawRules, LotteryAdapter
from engine.modules.pruning import run_pruning_audit, PruningMetrics
from engine.strategies import STRATEGY_REGISTRY

@dataclass
class StrategicDecision:
    sentiment: str # Strong Buy, Buy, Neutral, Sell, Strong Sell
    lift: float
    avg_rank: float
    is_hibernated: bool

def get_sentiment_label(lift: float, is_hibernated: bool) -> str:
    if lift > 0.10: return "[bold green]Strong Buy[/bold green]"
    if lift > 0.02: return "[green]Buy[/green]"
    if lift > -0.02: return "[yellow]Neutral[/yellow]"
    if is_hibernated: return "[red]Strong Sell[/red]"
    return "[orange1]Sell[/orange1]"

def get_full_strategy_matrix(adapter: LotteryAdapter, window: int = 10) -> Dict[str, StrategicDecision]:
    """
    Audits registered strategies and returns a sentiment matrix.
    v10.0 Note: Only audits 'statistical' and 'fun' tiers by default 
    to ensure completion within global 30-minute timeout. ML/Deep 
    tiers require too much training time for exhaustive backtests.
    """
    all_strategies = [name for name, cfg in STRATEGY_REGISTRY.items() 
                     if cfg["tier"] in ("statistical", "fun")]
    
    metrics = run_pruning_audit(adapter, all_strategies, window=window)
    
    matrix = {}
    for m in metrics:
        # v10.0: Mandatory hibernation if lift is extremely negative (e.g. -10%)
        is_hibernated = m.is_hibernated or (m.lift_over_random < -0.10)
        
        matrix[m.strategy_name] = StrategicDecision(
            sentiment=get_sentiment_label(m.lift_over_random, is_hibernated),
            lift=m.lift_over_random,
            avg_rank=m.avg_rank,
            is_hibernated=is_hibernated
        )
    return matrix

def get_risk_ledger(df: pd.DataFrame, rules: DrawRules, scan_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identifies specific systemic risks based on current data.
    """
    risks = []
    
    # 1. Regime Risk
    js = scan_results.get("regime", {}).get("js", 0)
    if js > 0.05:
        risks.append({
            "risk": "Regime Shift",
            "impact": "High",
            "description": "Historical patterns are decoupling from current draw physics."
        })
    elif js > 0.02:
        risks.append({
            "risk": "Signal Drift",
            "impact": "Medium",
            "description": "Subtle changes in distribution detected. Strategy accuracy may degrade."
        })

    # 2. Entropy Risk
    from engine.modules import frequency
    f_res = frequency.analyze(df.tail(50), rules)
    if f_res.chi2_p_value < 0.05:
        risks.append({
            "risk": "Machine Bias",
            "impact": "Medium",
            "description": "Non-uniform distribution detected. Possible mechanical or algorithmic bias."
        })

    # 3. Strategy Risk
    if scan_results.get("scan", {}).get("verdict") == "NO-GO":
        risks.append({
            "risk": "Low Signal-to-Noise",
            "impact": "Extreme",
            "description": "No clear statistical edge found in current window."
        })

    return risks

def get_logic_assumptions(df: pd.DataFrame, rules: DrawRules) -> List[str]:
    """
    Defines the 'Mental Model' the engine is using for today's forecast.
    """
    assumptions = []
    
    # Check if we are in a hot-streak regime
    from engine.modules import frequency
    f_res = frequency.analyze(df.tail(30), rules)
    top_z = f_res.table["z_score"].max()
    
    if top_z > 3.0:
        assumptions.append("Positive: Hot-streak persistence is the dominant signal.")
    else:
        assumptions.append("Neutral: Mean reversion is assumed for outliers.")
        
    assumptions.append("Technical: Assuming the 50-draw rolling window is representative of the current regime.")
    
    if len(df) < 500:
        assumptions.append("Negative: Small sample size (<500 draws) increases model variance.")
    
    return assumptions
