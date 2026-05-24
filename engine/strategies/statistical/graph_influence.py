"""
Graph Influence Strategy 🕸️
===========================
Treats the lottery pool as a network where:
- Nodes are numbers.
- Edges exist between physical neighbors on the bet slip.
- Edges also exist between numbers that co-occur in the same draw.
Uses PageRank centrality to identify the most 'influential' numbers
in the current network topology.
"""

from __future__ import annotations

import networkx as nx
import pandas as pd
import numpy as np

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

@register
class GraphInfluenceStrategy(BaseStrategy):
    name = "graph_influence"
    description = "🕸️ Network Influence (PageRank Centrality on Hybrid Graph)"
    tier = "statistical"

    requires_history = 50

    def __init__(self, physical_weight: float = 0.3, co_occur_weight: float = 0.7) -> None:
        self.physical_weight = physical_weight
        self.co_occur_weight = co_occur_weight

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        
        G = nx.Graph()
        G.add_nodes_from(all_numbers)
        
        # 1. Add Physical Edges (Grid Adjacency)
        width = rules.board_cols or 10
        for n in all_numbers:
            row = (n - 1) // width
            col = (n - 1) % width
            
            # Check neighbors (up, down, left, right)
            neighbors = []
            if col > 0: neighbors.append(n - 1) # Left
            if col < width - 1: neighbors.append(n + 1) # Right
            if row > 0: neighbors.append(n - width) # Up
            if row < (hi // width): neighbors.append(n + width) # Down
            
            for m in neighbors:
                if lo <= m <= hi:
                    if G.has_edge(n, m):
                        G[n][m]['weight'] += self.physical_weight
                    else:
                        G.add_edge(n, m, weight=self.physical_weight)

        # 2. Add Historical Co-occurrence Edges
        # We only look at the recent history
        n_draws = len(df)
        for i, row in enumerate(df.itertuples()):
            # Weight co-occurrence by recency
            recency_boost = (i + 1) / n_draws
            nums = row.numbers
            for idx1, n in enumerate(nums):
                for idx2, m in enumerate(nums):
                    if idx1 >= idx2: continue
                    if lo <= n <= hi and lo <= m <= hi:
                        w = self.co_occur_weight * recency_boost
                        if G.has_edge(n, m):
                            G[n][m]['weight'] += w
                        else:
                            G.add_edge(n, m, weight=w)
                            
        # 3. Calculate PageRank Centrality
        # PageRank with edge weights
        try:
            pagerank = nx.pagerank(G, weight='weight')
        except Exception:
            # Fallback to degree centrality if PR fails
            pagerank = nx.degree_centrality(G)
            
        # Normalize scores
        max_pr = max(pagerank.values()) if pagerank else 1.0
        if max_pr == 0: max_pr = 1.0
        
        return {n: pagerank.get(n, 0.0) / max_pr for n in all_numbers}
