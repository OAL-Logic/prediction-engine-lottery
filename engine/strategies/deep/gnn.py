"""
Graph Convolutional Network (GCN) Strategy  🕸️
==============================================
Treats the lottery ticket as a 2D spatial graph where nodes are numbers
and edges are physical adjacencies on the bet slip.

It learns spatial propagation dynamics — how recent winning numbers
influence the likelihood of adjacent numbers being drawn, capturing
geographic clusters and grid-based patterns.

Requires: pip install "lottery-engine[deep]"
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

try:
    import torch
    import torch.nn as nn
    _TORCH = True
except ImportError:
    _TORCH = False


# ---------------------------------------------------------------------------
# GCN Layers & Model
# ---------------------------------------------------------------------------

if _TORCH:
    class GCNConv(nn.Module):
        """Basic Graph Convolutional Network (GCN) layer."""

        def __init__(self, in_features: int, out_features: int) -> None:
            super().__init__()
            self.linear = nn.Linear(in_features, out_features, bias=False)
            self.bias = nn.Parameter(torch.zeros(out_features))

        def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
            # x: (num_nodes, in_features)
            # adj: (num_nodes, num_nodes) symmetric normalized adjacency matrix
            out = torch.matmul(adj, x)
            out = self.linear(out)
            return out + self.bias


    class LotteryGCN(nn.Module):
        """2-layer GCN model for lottery node classification (drawn vs not drawn)."""

        def __init__(self, in_features: int, hidden_features: int = 32) -> None:
            super().__init__()
            self.conv1 = GCNConv(in_features, hidden_features)
            self.act = nn.ReLU()
            self.conv2 = GCNConv(hidden_features, 1)  # output a single logit per node

        def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
            # x: (num_nodes, in_features)
            # adj: (num_nodes, num_nodes)
            h = self.conv1(x, adj)
            h = self.act(h)
            h = self.conv2(h, adj)
            return h.squeeze(-1)  # (num_nodes,)


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------

@register
class GNNStrategy(BaseStrategy):
    name = "gnn"
    description = "🕸️ Graph Neural Network (GCN) — models spatial grid propagation & neighborhood influence"
    tier = "deep"
    requires_history = 100

    def __init__(
        self,
        epochs: int = 80,
        lr: float = 1e-2,
        hidden_dim: int = 32,
        infer_temp: float = 1.0,
    ) -> None:
        self.epochs = epochs
        self.lr = lr
        self.hidden_dim = hidden_dim
        self.infer_temp = infer_temp

    def _build_grid_adj(self, pool_size: int) -> torch.Tensor:
        """Builds a symmetric, self-loop normalized adjacency matrix based on a grid slip."""
        # Find sensible column count based on pool size
        if pool_size <= 25:
            cols = 5
        elif pool_size <= 50:
            cols = 5 if pool_size % 5 == 0 else 10
        else:
            cols = 10

        adj = torch.zeros((pool_size, pool_size))
        
        # Coordinates mapping
        coords = {}
        for i in range(pool_size):
            r = i // cols
            c = i % cols
            coords[i] = (r, c)

        # Adjacency check (horizontal, vertical, diagonal)
        for i in range(pool_size):
            r_i, c_i = coords[i]
            for j in range(pool_size):
                r_j, c_j = coords[j]
                # Distance threshold of 1.5 matches adjacent cells (dist <= sqrt(2))
                dist = np.sqrt((r_i - r_j) ** 2 + (c_i - c_j) ** 2)
                if dist <= 1.5:
                    adj[i, j] = 1.0

        # Self-loops are already added by distance threshold (dist = 0.0 <= 1.5)
        # Degree normalization: D^-1/2 * A * D^-1/2
        rowsum = adj.sum(dim=1)
        d_inv_sqrt = torch.pow(rowsum, -0.5)
        d_inv_sqrt[torch.isinf(d_inv_sqrt)] = 0.0
        d_mat_inv_sqrt = torch.diag(d_inv_sqrt)
        
        normalized_adj = torch.matmul(torch.matmul(d_mat_inv_sqrt, adj), d_mat_inv_sqrt)
        return normalized_adj

    def _extract_node_features(
        self, df: pd.DataFrame, pool_size: int, idx: dict[int, int], all_numbers: list[int]
    ) -> torch.Tensor:
        """Extracts rich node features for each ball in the pool."""
        features = []
        T = len(df)

        # Compute frequencies over different rolling windows
        last_5 = df.tail(5)
        last_15 = df.tail(15)
        last_50 = df.tail(50)

        # Pre-count occurrences
        counts_5 = {num: 0 for num in all_numbers}
        counts_15 = {num: 0 for num in all_numbers}
        counts_50 = {num: 0 for num in all_numbers}
        gaps = {num: T for num in all_numbers}

        # Gap calculation
        for t_idx, row in df.reset_index(drop=True).iterrows():
            for num in row["numbers"]:
                if num in gaps:
                    gaps[num] = T - 1 - t_idx

        for _, row in last_5.iterrows():
            for num in row["numbers"]:
                if num in counts_5:
                    counts_5[num] += 1

        for _, row in last_15.iterrows():
            for num in row["numbers"]:
                if num in counts_15:
                    counts_15[num] += 1

        for _, row in last_50.iterrows():
            for num in row["numbers"]:
                if num in counts_50:
                    counts_50[num] += 1

        # Columns layout for coordinate features
        if pool_size <= 25:
            cols = 5
        elif pool_size <= 50:
            cols = 5 if pool_size % 5 == 0 else 10
        else:
            cols = 10

        for i, num in enumerate(all_numbers):
            # Positional features
            r = i // cols
            c = i % cols
            
            feat = [
                float(counts_5[num]) / 5.0,
                float(counts_15[num]) / 15.0,
                float(counts_50[num]) / 50.0,
                float(gaps[num]) / float(T + 1),
                float(r) / float(pool_size // cols + 1),
                float(c) / float(cols)
            ]
            features.append(feat)

        return torch.tensor(features, dtype=torch.float32)

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        if not _TORCH:
            raise ImportError("pip install 'lottery-engine[deep]'")

        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        idx = {n: i for i, n in enumerate(all_numbers)}

        df = df.sort_values("draw_id").reset_index(drop=True)

        if len(df) < 20:
            return {n: 1.0 / pool for n in all_numbers}

        # Build grid adjacency matrix
        adj = self._build_grid_adj(pool)

        # -------------------------------------------------------------------
        # Build training targets & features
        # -------------------------------------------------------------------
        # We can predict the outcomes of the last 15 draws for training
        # target_t: drawn/not drawn in draw t
        # features_t: features computed up to draw t-1
        X_train_list, y_train_list = [], []
        
        train_window = min(15, len(df) - 10)
        for t in range(len(df) - train_window, len(df)):
            df_hist = df.iloc[:t]
            target_draw = df.iloc[t]
            
            # Node features at time t-1
            feat = self._extract_node_features(df_hist, pool, idx, all_numbers)
            
            # Target labels at time t (drawn = 1.0, not drawn = 0.0)
            target = torch.zeros(pool)
            for n in target_draw["numbers"]:
                if n in idx:
                    target[idx[n]] = 1.0
                    
            X_train_list.append(feat)
            y_train_list.append(target)

        # -------------------------------------------------------------------
        # Model & Training
        # -------------------------------------------------------------------
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Grid Adjacency is stationary
        adj = adj.to(device)
        
        in_features = 6  # our node feature dimension
        model = LotteryGCN(in_features, self.hidden_dim).to(device)

        # --- Caching Logic ---
        import hashlib
        from pathlib import Path
        slug = rules.name.replace(" ", "_").lower()
        last_draw_hash = hashlib.md5(pd.util.hash_pandas_object(df["draw_id"]).values).hexdigest()
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        params_str = f"{self.epochs}_{self.lr}_{self.hidden_dim}"
        cache_key = f"{self.name}_{slug}_{last_draw_hash}_{params_str}.pt"
        cache_path = cache_dir / cache_key

        if cache_path.exists():
            model.load_state_dict(torch.load(cache_path, map_location=device))
        else:
            opt = torch.optim.AdamW(model.parameters(), lr=self.lr, weight_decay=1e-4)
            loss_fn = nn.BCEWithLogitsLoss()

            model.train()
            for _ in range(self.epochs):
                opt.zero_grad()
                total_loss = torch.tensor(0.0, device=device)
                for feat, target in zip(X_train_list, y_train_list):
                    feat, target = feat.to(device), target.to(device)
                    logits = model(feat, adj)
                    total_loss += loss_fn(logits, target)
                
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()

            torch.save(model.state_dict(), cache_path)

        # -------------------------------------------------------------------
        # Inference
        # -------------------------------------------------------------------
        model.eval()
        with torch.no_grad():
            feat_latest = self._extract_node_features(df, pool, idx, all_numbers).to(device)
            logits_out = model(feat_latest, adj)
            probs = torch.sigmoid(logits_out / max(self.infer_temp, 1e-3)).cpu().numpy()

        return {n: float(probs[i]) for i, n in enumerate(all_numbers)}
