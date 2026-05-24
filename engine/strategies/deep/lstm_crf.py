"""
LSTM-CRF Sequence Logic Brain 🧠
================================
Ported from LottoProphet. Uses a Bi-LSTM paired with a Conditional Random Field (CRF)
to model inter-number dependencies and enforce global structural validity.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torchcrf import CRF

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

logger = logging.getLogger(__name__)

class LstmCRFModel(nn.Module):
    """
    Core sequence labeling architecture.
    Models the joint probability of the entire ticket sequence.
    """
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, output_seq_length: int):
        super(LstmCRFModel, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=2, batch_first=True, bidirectional=True)
        # Bidirectional doubles the hidden dim
        self.fc = nn.Linear(hidden_dim * 2, output_dim * output_seq_length)
        self.crf = CRF(output_dim, batch_first=True)
        self.output_seq_length = output_seq_length
        self.output_dim = output_dim

    def forward(self, x: torch.Tensor, labels: torch.Tensor = None, mask: torch.Tensor = None) -> Any:
        lstm_out, _ = self.lstm(x)
        # Use only the last hidden state for prediction
        final_hidden = lstm_out[:, -1, :]
        logits = self.fc(final_hidden)
        logits = logits.view(-1, self.output_seq_length, self.output_dim)

        if labels is not None:
            if mask is not None:
                mask = mask.bool()
            # Returns negative log likelihood
            loss = -self.crf(logits, labels, mask=mask)
            return loss
        else:
            # Returns best path sequence
            predictions = self.crf.decode(logits, mask=mask)
            return predictions

@register
class LSTMCRFStrategy(BaseStrategy):
    name = "lstm_crf"
    description = "🧠 Sequence Logic Brain (LSTM-CRF) — models inter-number dependencies"
    tier = "deep"
    requires_history = 60 # Window of 10 * 6 samples

    def __init__(self, hidden_dim: int = 64, window_size: int = 10):
        self.hidden_dim = hidden_dim
        self.window_size = window_size
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _prepare_data(self, df: pd.DataFrame, rules: DrawRules) -> Tuple[torch.Tensor, torch.Tensor]:
        """Converts draw history into sliding window sequences."""
        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        
        # Flatten numbers to indices
        history = []
        for nums in df["numbers"]:
            history.append([n - lo for n in sorted(nums)])
            
        X, y = [], []
        for i in range(len(history) - self.window_size):
            X.append(history[i:i + self.window_size])
            y.append(history[i + self.window_size])
            
        return torch.tensor(X, dtype=torch.float32).to(self.device), \
               torch.tensor(y, dtype=torch.long).to(self.device)

    def train(self, df: pd.DataFrame, rules: DrawRules, epochs: int = 20):
        """Trains or retrains the LSTM-CRF model and serializes it."""
        lo, hi = rules.number_range
        output_dim = hi - lo + 1
        seq_length = rules.pick_count
        
        X, y = self._prepare_data(df, rules)
        input_dim = X.shape[-1]
        
        self.model = LstmCRFModel(input_dim, self.hidden_dim, output_dim, seq_length).to(self.device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        
        self.model.train()
        from engine.modules.telemetry import pulse
        for epoch in range(epochs):
            optimizer.zero_grad()
            loss = self.model(X, y)
            loss.backward()
            optimizer.step()
            if epoch % 5 == 0:
                pulse(f"LSTM-CRF Training: Epoch {epoch}/{epochs}, Loss: {loss.item():.4f}", "INFO")
            
        # Model caching (Story 5.2.1/5.2.4)
        os.makedirs("data/model_cache", exist_ok=True)
        game_slug = rules.name.lower().replace(" ", "_")
        cache_path = f"data/model_cache/lstm_crf_{game_slug}.pt"
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'hidden_dim': self.hidden_dim,
            'window_size': self.window_size
        }, cache_path)
        logger.info(f"LSTM-CRF model saved to {cache_path}")

    def load(self, rules: DrawRules) -> bool:
        """Loads a cached model if it exists."""
        game_slug = rules.name.lower().replace(" ", "_")
        cache_path = f"data/model_cache/lstm_crf_{game_slug}.pt"
        
        if not os.path.exists(cache_path):
            return False
            
        lo, hi = rules.number_range
        output_dim = hi - lo + 1
        seq_length = rules.pick_count
        
        checkpoint = torch.load(cache_path, map_location=self.device)
        self.hidden_dim = checkpoint['hidden_dim']
        self.window_size = checkpoint['window_size']
        
        # We need input_dim to init model, usually pick_count if we use indices
        input_dim = seq_length
        self.model = LstmCRFModel(input_dim, self.hidden_dim, output_dim, seq_length).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        return True

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        """
        Uses the CRF transition matrix to score likely numbers in the sequence.
        """
        if self.model is None:
            if not self.load(rules):
                self.train(df, rules)
            
        self.model.eval()
        X, _ = self._prepare_data(df.tail(self.window_size + 1), rules)
        
        with torch.no_grad():
            best_path = self.model(X[-1:]) # Predict for the latest sequence
            
        # Convert best path into frequency-style scores [0, 1]
        lo, hi = rules.number_range
        scores = {n: 0.1 for n in range(lo, hi + 1)}
        
        # Boost numbers in the predicted path
        for idx in best_path[0]:
            num = idx + lo
            if num in scores:
                scores[num] = 1.0
                
        return scores
