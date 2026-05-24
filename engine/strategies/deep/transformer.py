"""
Transformer Strategy  🤖
=========================
Uses a GPT-style decoder-only Transformer to model the sequence of lottery draws
and predict the probability distribution over numbers for the next draw.

Architecture
------------
  Input       : sequence of last N draws, each encoded as a multi-hot vector
                of size `pool_size` (e.g. 60 for Mega-Sena)
  Embedding   : linear projection → d_model
  Transformer : L decoder layers, each with:
                  - Multi-head self-attention (causal mask so position t only
                    attends to positions ≤ t, preventing data leakage)
                  - Feed-forward block (d_model → 4×d_model → d_model)
                  - Layer norm + residual connections
  Output head : linear → pool_size, sigmoid activation
                → per-number appearance probability for draw t+1

Temperature sampling
--------------------
At inference, we apply temperature T to the logits before softmax so the
model doesn't collapse to always picking the same numbers:
  p_i = softmax(logits / T)

T < 1 → sharper (more confident)
T = 1 → standard
T > 1 → flatter (more exploratory)

Training
--------
  Loss     : Binary cross-entropy (multi-label, one loss per number)
  Optimizer: AdamW with cosine LR schedule
  Data aug : random draw-order shuffle within a window (helps generalisation)

Requires: pip install "lottery-engine[deep]"
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register


def _get_model_classes():
    """Deferred loading of torch-dependent classes."""
    import torch
    import torch.nn as nn

    class _DrawEmbedding(nn.Module):
        def __init__(self, pool_size: int, d_model: int) -> None:
            super().__init__()
            self.proj = nn.Linear(pool_size, d_model)
            self.norm = nn.LayerNorm(d_model)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.norm(self.proj(x))

    class _LotteryTransformer(nn.Module):
        def __init__(
            self,
            pool_size: int,
            d_model:   int = 128,
            n_heads:   int = 4,
            n_layers:  int = 3,
            dropout:   float = 0.1,
        ) -> None:
            super().__init__()
            self.embed = _DrawEmbedding(pool_size, d_model)
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model,
                nhead=n_heads,
                dim_feedforward=d_model * 4,
                dropout=dropout,
                batch_first=True,
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
            self.head = nn.Linear(d_model, pool_size)

        def forward(self, x: torch.Tensor, causal_mask: bool = True) -> torch.Tensor:
            e = self.embed(x)
            seq_len = e.shape[1]
            mask = None
            if causal_mask:
                import torch
                mask = torch.triu(
                    torch.ones(seq_len, seq_len, device=e.device) * float("-inf"),
                    diagonal=1,
                )
            out  = self.transformer(e, mask=mask)
            logits = self.head(out[:, -1, :])
            return logits
            
    return _DrawEmbedding, _LotteryTransformer


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@register
class TransformerStrategy(BaseStrategy):
    name        = "transformer"
    description = "🤖 Transformer (multi-head attention) — sequence modelling of draw history"
    tier        = "deep"
    requires_history = 200

    def __init__(
        self,
        seq_len:    int   = 32,
        d_model:    int   = 128,
        n_heads:    int   = 4,
        n_layers:   int   = 3,
        epochs:     int   = 50,
        lr:         float = 1e-3,
        dropout:    float = 0.1,
        infer_temp: float = 1.0,
    ) -> None:
        self.seq_len    = seq_len
        self.d_model    = d_model
        self.n_heads    = n_heads
        self.n_layers   = n_layers
        self.epochs     = epochs
        self.lr         = lr
        self.dropout    = dropout
        self.infer_temp = infer_temp

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        try:
            import torch
            import torch.nn as nn
        except ImportError:
            raise ImportError("pip install 'lottery-engine[deep]'")

        _DrawEmbedding, _LotteryTransformer = _get_model_classes()

        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        idx  = {n: i for i, n in enumerate(all_numbers)}

        df = df.sort_values("draw_id").reset_index(drop=True)

        # Encode draws as multi-hot vectors
        def encode(nums: list[int]) -> torch.Tensor:
            v = torch.zeros(pool)
            for n in nums:
                if n in idx:
                    v[idx[n]] = 1.0
            return v

        sequences = [encode(row["numbers"]) for _, row in df.iterrows()]
        T = len(sequences)

        # Build (input_seq, target) pairs
        X_list, y_list = [], []
        for t in range(self.seq_len, T - 1):
            X_list.append(torch.stack(sequences[t - self.seq_len: t]))
            y_list.append(sequences[t + 1])

        if not X_list:
            return {n: 1.0 / pool for n in all_numbers}

        X = torch.stack(X_list)   # (N, seq_len, pool)
        y = torch.stack(y_list)   # (N, pool)

        # Train
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model  = _LotteryTransformer(pool, self.d_model, self.n_heads, self.n_layers, self.dropout).to(device)
        
        # --- Caching Logic ---
        import hashlib
        from pathlib import Path
        slug = rules.name.replace(" ", "_").lower()
        last_draw_str = str(df.iloc[-1]["numbers"])
        last_draw_hash = hashlib.md5(pd.util.hash_pandas_object(df["draw_id"]).values).hexdigest()
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        params_str = f"{self.epochs}_{self.lr}_{self.seq_len}_{self.d_model}_{self.n_heads}_{self.n_layers}"
        cache_key = f"{self.name}_{slug}_{last_draw_hash}_{params_str}.pt"

        cache_path = cache_dir / cache_key

        if cache_path.exists():
            model.load_state_dict(torch.load(cache_path, map_location=device))
        else:
            opt    = torch.optim.AdamW(model.parameters(), lr=self.lr)
            sched  = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=self.epochs)
            loss_fn = nn.BCEWithLogitsLoss()

            X, y = X.to(device), y.to(device)
            model.train()
            for _ in range(self.epochs):
                opt.zero_grad()
                logits = model(X)
                loss   = loss_fn(logits, y)
                loss.backward()
                opt.step()
                sched.step()
                
            torch.save(model.state_dict(), cache_path)

        # Inference on last seq_len draws
        model.eval()
        with torch.no_grad():
            last_seq   = torch.stack(sequences[-self.seq_len:]).unsqueeze(0).to(device)
            logits_out = model(last_seq).squeeze(0)
            # Temperature scaling
            probs = torch.sigmoid(logits_out / max(self.infer_temp, 1e-3)).cpu().numpy()

        return {n: float(probs[i]) for i, n in enumerate(all_numbers)}
