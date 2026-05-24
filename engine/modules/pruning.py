"""
Performance Pruning Module (AutoML) 🧬
====================================
Systematically identifies and disables strategies that fail to provide 
statistical lift over a baseline (Random Walk).

Implements the "Three Layers of Pruning":
1. Performance Pruning (Hit Rate vs Random — implemented in `prune` command)
2. Redundancy Pruning (Jaccard Similarity — implemented in `prune --redundancy`)
3. Early-Exit Pruning (Heuristic branch-abort — implemented in `tune` optimizer)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd
    from engine.adapters import DrawAdapter, DrawRules
    from engine.strategies import SuggestionResult

@dataclass
class PruningMetrics:
    strategy_name: str
    lift_over_random: float
    avg_rank: float
    best_hit: int
    is_hibernated: bool = False

def calculate_random_baseline_accuracy(rules: DrawRules) -> float:
    """Expected hits for a purely random ticket."""
    pick = rules.pick_count
    pool = rules.number_range[1] - rules.number_range[0] + 1
    # Simplistic expectation: (pick * pick) / pool
    return (pick * pick) / pool

def run_pruning_audit(
    adapter: DrawAdapter,
    strategy_names: List[str],
    window: int = 50,
    threshold: float = 0.02 # 2% lift required
) -> List[PruningMetrics]:
    """
    Evaluates strategies and flags those that should be pruned.
    """
    import numpy as np
    from engine.strategies import get_strategy, STRATEGY_REGISTRY
    
    df = adapter.fetch()
    rules = adapter.rules
    baseline_acc = calculate_random_baseline_accuracy(rules)
    
    if len(df) < window + 10:
        logging.warning("Not enough history to run a reliable pruning audit.")
        return []

    results = []
    
    # Filter strategy_names to only those in the master registry
    available_names = [n for n in strategy_names if n in STRATEGY_REGISTRY]
    
    # Audit logic: simple backtest over last N draws
    target_draws = df.tail(window)
    
    for name in available_names:
        total_hits = 0
        all_ranks = []
        best_hit = 0
        
        try:
            strat = get_strategy(name)
            
            for _, row in target_draws.iterrows():
                draw_id = row["draw_id"]
                winning_numbers = set(row["numbers"])
                
                # Training data is everything before this draw
                train_df = df[df["draw_id"] < draw_id]
                
                # Generate 1 ticket deterministically (temp=0)
                res = strat.suggest(train_df, rules, count=1, temperature=0.0)
                ticket = set(res.tickets[0])
                
                hits = len(ticket & winning_numbers)
                total_hits += hits
                best_hit = max(best_hit, hits)
                
                # Rank tracking
                sorted_scores = sorted(res.scores.items(), key=lambda x: x[1], reverse=True)
                ranks = {num: r + 1 for r, (num, score) in enumerate(sorted_scores)}
                avg_r = sum(ranks.get(n, 0) for n in winning_numbers) / len(winning_numbers)
                all_ranks.append(avg_r)
                
            actual_acc = total_hits / window
            lift = (actual_acc - baseline_acc) / baseline_acc if baseline_acc > 0 else 0
            avg_rank = np.mean(all_ranks)
            
            is_hibernated = lift < threshold
            
            results.append(PruningMetrics(
                strategy_name=name,
                lift_over_random=lift,
                avg_rank=avg_rank,
                best_hit=best_hit,
                is_hibernated=is_hibernated
            ))
            
        except Exception as exc:
            logging.error(f"Error auditing strategy {name}: {exc}")
            
    return results

def calculate_redundancy_matrix(results: List[SuggestionResult]) -> Any:
    """Calculates Jaccard Similarity between strategy outputs."""
    import numpy as np
    n = len(results)
    matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            set_i = set(tuple(t) for t in results[i].tickets)
            set_j = set(tuple(t) for t in results[j].tickets)
            
            intersection = len(set_i & set_j)
            union = len(set_i | set_j)
            similarity = intersection / union if union > 0 else 0
            
            matrix[i, j] = similarity
            matrix[j, i] = similarity
            
    return matrix
