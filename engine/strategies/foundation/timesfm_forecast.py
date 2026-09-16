"""
TimesFM Foundation Model Strategy 🔭
=====================================
Zero-shot time-series forecasting via Google Research's TimesFM 2.5, applied
to each number's binary hit-indicator series — the same per-number encoding
`lstm`/`gru` already use — instead of a model trained from scratch per game.

Optional dependency: `pip install 'lottery-engine[foundation]'` (installs
`timesfm`, which pulls in `torch`). Model weights (~800MB) download once from
Hugging Face Hub on first use and are cached by the `timesfm` package itself
under `~/.cache/huggingface/`; this module keeps no separate weight cache,
only a process-local singleton for the loaded/compiled model object so a
single CLI invocation that scores multiple times doesn't reload it.

Origin: proposed in this project's TODO.md after a session exploring
TimesFM/TabFM for cycle analysis — see that file's "Integration Plan for
Google Research Foundation Models" for the original write-up this
implements the TimesFM half of. TabFM (tabular, in-context classification
over engineered features) is a natural follow-on in the same tier, not
implemented here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.adapters import DrawRules
from engine.strategies import BaseStrategy, register

_MODEL_CACHE = None  # process-local singleton; avoids recompiling per call


def _load_model():
    """Deferred: only imports/downloads/compiles timesfm when this strategy
    actually runs, never at module import time."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    import timesfm

    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
    model.compile(timesfm.ForecastConfig(
        max_context=1024,
        max_horizon=1,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        fix_quantile_crossing=True,
    ))
    _MODEL_CACHE = model
    return model


@register
class TimesFMStrategy(BaseStrategy):
    name = "timesfm"
    description = "🔭 TimesFM — zero-shot foundation-model forecast per number's hit series"
    tier = "foundation"
    requires_history = 60  # zero-shot (no training), but still needs real context to be meaningful

    def score(self, df: pd.DataFrame, rules: DrawRules) -> dict[int, float]:
        try:
            import timesfm  # noqa: F401 — presence check; _load_model() does the real work
        except ImportError:
            raise ImportError("pip install 'lottery-engine[foundation]'")

        lo, hi = rules.number_range
        all_numbers = list(range(lo, hi + 1))
        pool = len(all_numbers)
        idx = {n: i for i, n in enumerate(all_numbers)}

        df = df.sort_values("draw_id").reset_index(drop=True)

        # One binary hit-indicator series per number: x_t(n) = 1 if n was
        # drawn at t, else 0. TimesFM forecasts each series independently
        # (zero-shot, no cross-number structure) — the same simplification
        # the lstm/gru strategies' encoding makes, just without training.
        series = np.zeros((pool, len(df)), dtype=np.float32)
        for t, nums in enumerate(df["numbers"]):
            for n in nums:
                if n in idx:
                    series[idx[n], t] = 1.0

        if series.shape[1] == 0:
            return {n: 1.0 / pool for n in all_numbers}

        model = _load_model()
        point_forecast, _ = model.forecast(horizon=1, inputs=[series[i] for i in range(pool)])
        # point_forecast: (pool, 1) — the model's point estimate that each
        # number hits next draw. Clip negatives (the model isn't constrained
        # to [0, 1] for a 0/1 input series) and normalize into a score dict.
        raw = np.clip(np.asarray(point_forecast)[:, 0], 0.0, None)
        total = float(raw.sum())
        if total <= 0:
            return {n: 1.0 / pool for n in all_numbers}
        return {n: float(raw[i] / total) for i, n in enumerate(all_numbers)}
