"""
1D Dilated CNN Strategy  🔬
============================
Treats the draw history as a 1D signal and applies causal dilated
convolutions to detect local sequential patterns at multiple time scales.

Why CNN alongside LSTM and Transformer?
----------------------------------------
Each architecture has a different inductive bias:

  LSTM/GRU     Sequential recurrence — good at tracking running state,
               forgets distant context over long sequences.

  Transformer  Global attention — sees every pair of positions but
               can overfit on small datasets.

  CNN (1D)     Local pattern detection — a kernel of size K reads
               K consecutive draws at once. Dilation multiplies the
               effective receptive field exponentially without adding
               parameters.

Because they make different kinds of errors, voting all three together
reduces variance more than combining any two.

Architecture
------------
  Input       (batch, seq_len, pool_size) — multi-hot draw encodings
  → Transpose to (batch, pool_size, seq_len) for Conv1d
  → Conv1d(pool_size → channels, kernel=3, dilation=1, causal padding)
  → ReLU + residual
  → Conv1d(channels, kernel=3, dilation=2, causal padding) + ReLU + residual
  → Conv1d(channels, kernel=3, dilation=4, causal padding) + ReLU + residual
  → Conv1d(channels, kernel=3, dilation=8, causal padding) + ReLU + residual
  → Global average pool over time dimension → (batch, channels)
  → Linear(channels → pool_size) → sigmoid with temperature

Causal padding: pad left by (kernel-1)*dilation so that position t
sees only positions ≤ t (no future leakage).

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
# Model
# ---------------------------------------------------------------------------

if _TORCH:
    class _CausalConvBlock(nn.Module):
        """Single dilated causal conv layer with residual connection."""

        def __init__(self, channels: int, kernel: int, dilation: int) -> None:
            super().__init__()
            self.pad  = (kernel - 1) * dilation   # left-only causal padding
            self.conv = nn.Conv1d(
                channels, channels,
                kernel_size=kernel,
                dilation=dilation,
                padding=0,
            )
            self.norm = nn.BatchNorm1d(channels)
            self.act  = nn.ReLU()

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            # x: (batch, channels, seq)
            out = nn.functional.pad(x, (self.pad, 0))   # pad left
            out = self.conv(out)
            out = self.norm(out)
            return self.act(out + x)   # residual

    class _DilatedCNN(nn.Module):
        def __init__(
            self,
            pool_size: int,
            channels:  int = 64,
            kernel:    int = 3,
            n_layers:  int = 4,
            dropout:   float = 0.1,
        ) -> None:
            super().__init__()
            self.input_proj = nn.Conv1d(pool_size, channels, kernel_size=1)
            self.blocks = nn.ModuleList([
                _CausalConvBlock(channels, kernel, dilation=2 ** i)
                for i in range(n_layers)
            ])
            self.drop = nn.Dropout(dropout)
            self.head = nn.Linear(channels, pool_size)

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            # x: (batch, seq, pool_size) → (batch, pool_size, seq)
            out = x.transpose(1, 2)
            out = self.input_proj(out)
            for block in self.blocks:
                out = block(out)
            # Global average pool over time
            out = out.mean(dim=-1)   # (batch, channels)
            return self.head(self.drop(out))


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@register
class CNN1DStrategy(BaseStrategy):
    name        = "cnn_1d"
    description = "🔬 1D dilated CNN — local sequential pattern detection at multiple scales"
    tier        = "deep"
    requires_history = 100

    def __init__(
        self,
        seq_len:    int   = 32,
        channels:   int   = 64,
        n_layers:   int   = 4,
        epochs:     int   = 60,
        lr:         float = 1e-3,
        dropout:    float = 0.1,
        infer_temp: float = 1.0,
    ) -> None:
        self.seq_len    = seq_len
        self.channels   = channels
        self.n_layers   = n_layers
        self.epochs     = epochs
        self.lr         = lr
        self.dropout    = dropout
        self.infer_temp = infer_temp

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        if not _TORCH:
            raise ImportError("pip install 'lottery-engine[deep]'")

        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        idx  = {n: i for i, n in enumerate(all_numbers)}

        df = df.sort_values("draw_id").reset_index(drop=True)

        def encode(nums: list[int]) -> "torch.Tensor":
            v = torch.zeros(pool)
            for n in nums:
                if n in idx:
                    v[idx[n]] = 1.0
            return v

        sequences = [encode(row["numbers"]) for _, row in df.iterrows()]
        T = len(sequences)

        X_list, y_list = [], []
        for t in range(self.seq_len, T - 1):
            X_list.append(torch.stack(sequences[t - self.seq_len: t]))
            y_list.append(sequences[t + 1])

        if not X_list:
            return {n: 1.0 / pool for n in all_numbers}

        X = torch.stack(X_list)   # (N, seq_len, pool)
        y = torch.stack(y_list)   # (N, pool)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model  = _DilatedCNN(pool, self.channels, n_layers=self.n_layers, dropout=self.dropout).to(device)
        
        # --- Caching Logic ---
        import hashlib
        import hashlib
        from pathlib import Path
        slug = rules.name.replace(" ", "_").lower()
        last_draw_hash = hashlib.md5(pd.util.hash_pandas_object(df["draw_id"]).values).hexdigest()
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        params_str = f"{self.epochs}_{self.lr}_{self.seq_len}_{self.channels}_{self.n_layers}"
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
                loss = loss_fn(model(X), y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                
            torch.save(model.state_dict(), cache_path)

        model.eval()
        with torch.no_grad():
            last_seq    = torch.stack(sequences[-self.seq_len:]).unsqueeze(0).to(device)
            logits_out  = model(last_seq).squeeze(0)
            probs       = torch.sigmoid(logits_out / max(self.infer_temp, 1e-3)).cpu().numpy()

        return {n: float(probs[i]) for i, n in enumerate(all_numbers)}
