"""
Algorithm distillation pipeline (Story 3.5).

Transfers a quantum teacher (``distill_entropy`` interface) into a small
pure-numpy LSTM policy, verifies signal fidelity (Bhattacharyya, >= 0.90) and
inference latency (P99 < 500ms), and caches the policy to ``data/model_cache/``
only if it passes.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from engine._paths import PROJECT_ROOT

DEFAULT_CACHE_DIR = PROJECT_ROOT / "data" / "model_cache"
FIDELITY_THRESHOLD = 0.90
LATENCY_P99_LIMIT_MS = 500.0
SUM_TOLERANCE = 1e-2


class DistillationError(Exception):
    """Teacher failure, invalid distribution, or unreadable policy file."""


def _pulse(message: str, level: str = "INFO") -> None:
    try:
        from engine.modules.telemetry import pulse

        pulse(message, level)
    except Exception:
        pass


def signal_fidelity(p: Any, q: Any) -> float:
    """Classical (Bhattacharyya) fidelity F = (sum sqrt(p*q))**2, in [0, 1]."""
    a = np.asarray(p, dtype=np.float64)
    b = np.asarray(q, dtype=np.float64)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("distributions must be 1-D and of equal length")
    a = np.clip(a, 0.0, None)
    b = np.clip(b, 0.0, None)
    f = float(np.sum(np.sqrt(a * b))) ** 2
    return min(1.0, max(0.0, f))


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


_PARAMS = ("Wx", "Wh", "b", "Wy", "by")


class NumpyLSTMPolicy:
    """LSTM mapping a window of past outcomes to probabilities over ``n_outcomes``."""

    def __init__(self, n_outcomes: int, hidden: int = 32, window: int = 4, seed: int = 0):
        if n_outcomes < 2 or hidden < 1 or window < 1:
            raise ValueError("n_outcomes >= 2, hidden >= 1, window >= 1 required")
        self.n_outcomes = int(n_outcomes)
        self.hidden = int(hidden)
        self.window = int(window)
        rng = np.random.default_rng(seed)
        K, H = self.n_outcomes, self.hidden
        s = 0.1
        self.params: Dict[str, np.ndarray] = {
            "Wx": rng.normal(0, s, (K, 4 * H)),
            "Wh": rng.normal(0, s, (H, 4 * H)),
            "b": np.zeros(4 * H),
            "Wy": rng.normal(0, s, (H, K)),
            "by": np.zeros(K),
        }
        self.params["b"][H : 2 * H] = 1.0  # forget-gate bias
        self._m = {k: np.zeros_like(v) for k, v in self.params.items()}
        self._v = {k: np.zeros_like(v) for k, v in self.params.items()}
        self._t = 0

    # -- forward / inference -------------------------------------------------
    def _forward(self, X: np.ndarray):
        """X: (B, T) int outcomes. Returns probs (B, K) and cache."""
        P = self.params
        B, T = X.shape
        H = self.hidden
        h = np.zeros((B, H))
        c = np.zeros((B, H))
        cache = []
        for t in range(T):
            x = np.zeros((B, self.n_outcomes))
            x[np.arange(B), X[:, t]] = 1.0
            z = x @ P["Wx"] + h @ P["Wh"] + P["b"]
            i = _sigmoid(z[:, :H])
            f = _sigmoid(z[:, H : 2 * H])
            g = np.tanh(z[:, 2 * H : 3 * H])
            o = _sigmoid(z[:, 3 * H :])
            c_new = f * c + i * g
            tc = np.tanh(c_new)
            h_new = o * tc
            cache.append((x, h, c, i, f, g, o, c_new, tc))
            h, c = h_new, c_new
        probs = _softmax(h @ P["Wy"] + P["by"])
        return probs, (cache, h)

    def _coerce(self, context: Any) -> np.ndarray:
        arr = np.asarray(context, dtype=np.int64)
        if arr.ndim == 1:
            arr = arr[None, :]
        if arr.ndim != 2 or arr.shape[1] < 1:
            raise ValueError("context must be a 1-D or 2-D array of outcomes")
        if arr.min() < 0 or arr.max() >= self.n_outcomes:
            raise ValueError("context outcome out of range")
        return arr

    def predict_probs(self, context: Any) -> np.ndarray:
        """Probabilities for the next outcome. 1-D context -> (K,), 2-D -> (B, K)."""
        single = np.asarray(context).ndim == 1
        probs, _ = self._forward(self._coerce(context))
        return probs[0] if single else probs

    # -- training --------------------------------------------------------------
    def _grads(self, X: np.ndarray, target: np.ndarray):
        """Cross-entropy loss vs soft ``target`` and its analytic BPTT gradients."""
        P = self.params
        B, T = X.shape
        H = self.hidden
        tgt = np.broadcast_to(np.asarray(target, dtype=np.float64), (B, self.n_outcomes))
        probs, (cache, h_last) = self._forward(X)
        loss = float(-np.mean(np.sum(tgt * np.log(probs + 1e-12), axis=1)))

        grads = {k: np.zeros_like(v) for k, v in P.items()}
        dlogits = (probs - tgt) / B
        grads["Wy"] = h_last.T @ dlogits
        grads["by"] = dlogits.sum(axis=0)
        dh = dlogits @ P["Wy"].T
        dc = np.zeros((B, H))
        for t in reversed(range(T)):
            x, h_prev, c_prev, i, f, g, o, c_new, tc = cache[t]
            do = dh * tc
            dc_t = dc + dh * o * (1 - tc**2)
            di = dc_t * g
            dg = dc_t * i
            df = dc_t * c_prev
            dz = np.concatenate(
                [di * i * (1 - i), df * f * (1 - f), dg * (1 - g**2), do * o * (1 - o)],
                axis=1,
            )
            grads["Wx"] += x.T @ dz
            grads["Wh"] += h_prev.T @ dz
            grads["b"] += dz.sum(axis=0)
            dh = dz @ P["Wh"].T
            dc = dc_t * f
        return loss, grads

    def train_step(self, X: np.ndarray, target: np.ndarray, lr: float = 0.05) -> float:
        """One BPTT + Adam step minimising cross-entropy vs soft ``target`` (K,) or (B, K)."""
        P = self.params
        loss, grads = self._grads(X, target)
        self._t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for k in _PARAMS:
            gk = np.clip(grads[k], -5.0, 5.0)
            self._m[k] = b1 * self._m[k] + (1 - b1) * gk
            self._v[k] = b2 * self._v[k] + (1 - b2) * gk * gk
            mh = self._m[k] / (1 - b1**self._t)
            vh = self._v[k] / (1 - b2**self._t)
            P[k] -= lr * mh / (np.sqrt(vh) + eps)
        return loss

    # -- persistence -----------------------------------------------------------
    def save(self, path: Any) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # np.savez appends ".npz" to str paths lacking it; write via file handle.
        with open(p, "wb") as fh:
            np.savez(
                fh,
                n_outcomes=self.n_outcomes,
                hidden=self.hidden,
                window=self.window,
                **self.params,
            )
        return p

    @classmethod
    def load(cls, path: Any) -> "NumpyLSTMPolicy":
        try:
            with np.load(Path(path), allow_pickle=False) as d:
                pol = cls(int(d["n_outcomes"]), int(d["hidden"]), int(d["window"]))
                for k in _PARAMS:
                    arr = np.array(d[k], dtype=np.float64)
                    if arr.shape != pol.params[k].shape:
                        raise ValueError(f"bad shape for {k}")
                    pol.params[k] = arr
        except Exception as exc:
            raise DistillationError(f"cannot load policy from {path}: {exc}") from exc
        return pol


@dataclass
class DistillationResult:
    policy: NumpyLSTMPolicy
    fidelity: float
    passed: bool
    latency_p99_ms: float
    epochs: int
    teacher_source: str
    cache_path: Optional[str]
    threshold: float = FIDELITY_THRESHOLD


class DistillationPipeline:
    def __init__(
        self,
        teacher: Optional[Any] = None,
        qubits: int = 4,
        epochs: int = 60,
        steps_per_epoch: int = 4,
        batch_size: int = 64,
        hidden: int = 32,
        window: int = 4,
        lr: float = 0.05,
        seed: int = 0,
        threshold: float = FIDELITY_THRESHOLD,
        probes: int = 64,
        latency_limit_ms: float = LATENCY_P99_LIMIT_MS,
        report_interval: int = 10,
        cache_dir: Optional[Any] = None,
        cache_name: str = "distilled_lstm.npz",
    ):
        if isinstance(qubits, bool) or not isinstance(qubits, int) or qubits < 1:
            raise ValueError(f"qubits must be a positive int, got {qubits!r}")
        if isinstance(epochs, bool) or not isinstance(epochs, int) or epochs < 0:
            raise ValueError(f"epochs must be a non-negative int, got {epochs!r}")
        if not (isinstance(threshold, (int, float)) and 0.0 <= threshold <= 1.0):
            raise ValueError(f"threshold must be in [0, 1], got {threshold!r}")
        for name, v in (("steps_per_epoch", steps_per_epoch), ("batch_size", batch_size),
                        ("probes", probes), ("report_interval", report_interval)):
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise ValueError(f"{name} must be a positive int, got {v!r}")
        self._teacher = teacher
        self.qubits = qubits
        self.epochs = epochs
        self.steps_per_epoch = steps_per_epoch
        self.batch_size = batch_size
        self.hidden = hidden
        self.window = window
        self.lr = lr
        self.seed = seed
        self.threshold = float(threshold)
        self.probes = probes
        self.latency_limit_ms = latency_limit_ms
        self.report_interval = report_interval
        self.cache_dir = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
        self.cache_name = cache_name

    def _get_teacher(self) -> Any:
        if self._teacher is None:
            from engine.modules.cosmic import QuantumSidecar

            self._teacher = QuantumSidecar()
        return self._teacher

    async def _fetch_teacher(self):
        n = 2**self.qubits
        try:
            result = await self._get_teacher().distill_entropy(self.qubits)
            raw = result["entropy"]
            source = str(result.get("source", "unknown"))
        except Exception as exc:
            raise DistillationError(f"teacher failed: {exc}") from exc
        try:
            dist = np.asarray(raw, dtype=np.float64)
        except Exception as exc:
            raise DistillationError(f"invalid teacher distribution: {exc}") from exc
        if dist.shape != (n,):
            raise DistillationError(
                f"invalid teacher distribution: expected length {n}, got shape {dist.shape}"
            )
        if not np.all(np.isfinite(dist)) or np.any(dist < 0):
            raise DistillationError("invalid teacher distribution: NaN/inf or negative entries")
        total = float(dist.sum())
        if abs(total - 1.0) > SUM_TOLERANCE:
            raise DistillationError(f"invalid teacher distribution: sums to {total}")
        return dist / total, source

    async def run(self) -> DistillationResult:
        dist, source = await self._fetch_teacher()
        n = dist.size
        rng = np.random.default_rng(self.seed)
        policy = NumpyLSTMPolicy(n, self.hidden, self.window, seed=self.seed)
        _pulse(f"Distillation started: {n} outcomes, {self.epochs} epochs, teacher={source}")

        loss = float("nan")
        for epoch in range(1, self.epochs + 1):
            for _ in range(self.steps_per_epoch):
                # Context windows are i.i.d. teacher shots.
                X = rng.choice(n, size=(self.batch_size, self.window), p=dist)
                loss = policy.train_step(X, dist, self.lr)
            if epoch % self.report_interval == 0 and epoch != self.epochs:
                _pulse(f"Distillation epoch {epoch}/{self.epochs} loss={loss:.5f}")

        probes = rng.integers(0, n, size=(self.probes, self.window))
        student = policy.predict_probs(probes)
        fidelity = float(np.mean([signal_fidelity(dist, row) for row in student]))

        times = []
        for ctx in probes:
            t0 = time.perf_counter()
            policy.predict_probs(ctx)
            times.append((time.perf_counter() - t0) * 1000.0)
        p99 = float(np.percentile(times, 99))

        passed = bool(fidelity >= self.threshold and p99 < self.latency_limit_ms)
        cache_path: Optional[str] = None
        if passed:
            cache_path = str(policy.save(self.cache_dir / self.cache_name))
        _pulse(
            f"Distillation complete: fidelity={fidelity:.4f} p99={p99:.2f}ms "
            f"passed={passed}",
            "INFO" if passed else "WARN",
        )
        return DistillationResult(
            policy=policy,
            fidelity=fidelity,
            passed=passed,
            latency_p99_ms=p99,
            epochs=self.epochs,
            teacher_source=source,
            cache_path=cache_path,
            threshold=self.threshold,
        )
