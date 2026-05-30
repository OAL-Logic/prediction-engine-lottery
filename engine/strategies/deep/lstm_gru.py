"""
LSTM/GRU Strategies  🤖
=======================
Uses recurrent neural networks to capture temporal dependencies in 
lottery draw history.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import hashlib
from pathlib import Path
from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

def _get_model_classes():
    """Deferred loading of torch-dependent classes."""
    import torch
    import torch.nn as nn

    class _RecurrentModel(nn.Module):
        def __init__(
            self,
            pool_size: int,
            d_model:   int = 128,
            n_layers:  int = 2,
            dropout:   float = 0.1,
            cell_type: str = "lstm"
        ) -> None:
            super().__init__()
            self.proj = nn.Linear(pool_size, d_model)
            
            if cell_type.lower() == "gru":
                self.rnn = nn.GRU(d_model, d_model, n_layers, batch_first=True, dropout=dropout)
            else:
                self.rnn = nn.LSTM(d_model, d_model, n_layers, batch_first=True, dropout=dropout)
                
            self.head = nn.Linear(d_model, pool_size)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # x: (batch, seq_len, pool_size)
            x = torch.relu(self.proj(x))
            out, _ = self.rnn(x)
            # Use last hidden state
            logits = self.head(out[:, -1, :])
            return logits
            
    return _RecurrentModel

class _BaseRecurrentStrategy(BaseStrategy):
    requires_history = 200
    cell_type = "lstm"
    tier = "deep"

    def __init__(
        self,
        seq_len:    int   = 50,
        d_model:    int   = 128,
        n_layers:   int   = 2,
        epochs:     int   = 50,
        lr:         float = 5e-4,
        dropout:    float = 0.1,
        infer_temp: float = 1.0,
    ) -> None:
        self.seq_len    = seq_len
        self.d_model    = d_model
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

        _RecurrentModel = _get_model_classes()

        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        idx  = {n: i for i, n in enumerate(all_numbers)}

        df = df.sort_values("draw_id").reset_index(drop=True)

        def encode(nums: list[int]) -> torch.Tensor:
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

        X = torch.stack(X_list)
        y = torch.stack(y_list)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model  = _RecurrentModel(pool, self.d_model, self.n_layers, self.dropout, self.cell_type).to(device)
        
        # Caching
        slug = rules.name.replace(" ", "_").lower()
        last_draw_hash = hashlib.md5(pd.util.hash_pandas_object(df["draw_id"]).values).hexdigest()
        cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "model_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        params_str = f"{self.epochs}_{self.lr}_{self.seq_len}_{self.d_model}_{self.n_layers}"
        cache_key = f"{self.cell_type}_{slug}_{last_draw_hash}_{params_str}.pt"
        cache_path = cache_dir / cache_key

        if cache_path.exists():
            model.load_state_dict(torch.load(cache_path, map_location=device))
        else:
            opt = torch.optim.AdamW(model.parameters(), lr=self.lr)
            loss_fn = nn.BCEWithLogitsLoss()
            X, y = X.to(device), y.to(device)
            model.train()
            for _ in range(self.epochs):
                opt.zero_grad()
                logits = model(X)
                loss = loss_fn(logits, y)
                loss.backward()
                opt.step()
            torch.save(model.state_dict(), cache_path)

        model.eval()
        with torch.no_grad():
            last_seq = torch.stack(sequences[-self.seq_len:]).unsqueeze(0).to(device)
            logits_out = model(last_seq).squeeze(0)
            probs = torch.sigmoid(logits_out / max(self.infer_temp, 1e-3)).cpu().numpy()

        return {n: float(probs[i]) for i, n in enumerate(all_numbers)}

@register
class LSTMStrategy(_BaseRecurrentStrategy):
    name = "lstm"
    description = "🧠 LSTM (Long Short-Term Memory) — captures long-range temporal dependencies"
    cell_type = "lstm"

@register
class GRUStrategy(_BaseRecurrentStrategy):
    name = "gru"
    description = "🧠 GRU (Gated Recurrent Unit) — efficient temporal sequence modeling"
    cell_type = "gru"
