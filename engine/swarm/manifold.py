"""
Riemannian state-vector shared by the swarm (Story 3.2).

The state is a unit vector on the positive orthant of S^3: the sqrt-embedded
4-simplex (Fisher-Rao geometry). Weights are the squared components and always
sum to 1. Updates move along geodesics using the sphere exp/log maps.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

KEYS: Tuple[str, ...] = ("frequency", "deviation", "cosmic", "ml")
DIM = len(KEYS)
_EPS = 1e-12


@dataclass(frozen=True)
class RewardSignal:
    """Out-of-sample reward from one agent: lift plus a preferred simplex point."""

    lift: float
    preference: Sequence[float]
    agent_id: Optional[int] = None


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(a: Sequence[float]) -> float:
    return math.sqrt(_dot(a, a))


def log_map(x: Sequence[float], p: Sequence[float]) -> List[float]:
    """Tangent vector at x pointing to p, length equal to geodesic distance."""
    c = max(-1.0, min(1.0, _dot(x, p)))
    theta = math.acos(c)
    if theta < _EPS or math.sin(theta) < _EPS:
        return [0.0] * len(x)
    k = theta / math.sin(theta)
    return [k * (pi - c * xi) for xi, pi in zip(x, p)]


def exp_map(x: Sequence[float], v: Sequence[float]) -> List[float]:
    n = _norm(v)
    if n < _EPS:
        return list(x)
    s = math.sin(n) / n
    return [math.cos(n) * xi + s * vi for xi, vi in zip(x, v)]


def geodesic_distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.acos(max(-1.0, min(1.0, _dot(a, b))))


def _embed(preference: Sequence[float]) -> Optional[List[float]]:
    """Simplex point -> unit vector on the positive orthant, or None if invalid."""
    try:
        vals = [float(v) for v in preference]
    except (TypeError, ValueError):
        return None
    if len(vals) != DIM or any(not math.isfinite(v) or v < 0 for v in vals):
        return None
    total = sum(vals)
    if total <= 0 or not math.isfinite(total):
        return None
    roots = [math.sqrt(v / total) for v in vals]
    n = _norm(roots)
    return [r / n for r in roots]


def _valid_lift(lift: Any) -> Optional[float]:
    if isinstance(lift, bool):
        return None
    try:
        f = float(lift)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


class RiemannianState:
    def __init__(self, lr: float = 0.5, initial: Optional[Sequence[float]] = None):
        self._check_lr(lr)
        self.lr = float(lr)
        vec = _embed(initial) if initial is not None else [1.0 / math.sqrt(DIM)] * DIM
        if vec is None:
            raise ValueError("initial must be a valid 4-component simplex point")
        self._x: List[float] = vec
        self.epoch = 0
        self.rejected = 0
        self.last_distance_to_consensus = 0.0

    @staticmethod
    def _check_lr(lr: float) -> None:
        if isinstance(lr, bool) or not isinstance(lr, (int, float)) or not (0 < lr <= 1):
            raise ValueError(f"lr must be in (0, 1], got {lr!r}")

    # ---- views -----------------------------------------------------
    @property
    def vector(self) -> List[float]:
        return list(self._x)

    def weights(self) -> Dict[str, float]:
        sq = [c * c for c in self._x]
        total = sum(sq)
        return {k: s / total for k, s in zip(KEYS, sq)}

    def distance_to(self, preference: Sequence[float]) -> float:
        p = _embed(preference)
        if p is None:
            raise ValueError("invalid simplex point")
        return geodesic_distance(self._x, p)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "weights": self.weights(),
            "distance_to_consensus": self.last_distance_to_consensus,
        }

    # ---- evolution -------------------------------------------------
    def evolve(self, signals: Iterable[Any], lr: Optional[float] = None) -> Dict[str, Any]:
        """Apply one geodesic step. Returns a snapshot plus ``applied``/``rejected``."""
        step_lr = self.lr if lr is None else lr
        self._check_lr(step_lr)
        acc = [0.0] * DIM
        total = 0.0
        applied = 0
        rejected = 0
        for sig in signals:
            try:
                lift = _valid_lift(getattr(sig, "lift", None))
                p = _embed(getattr(sig, "preference", None))
            except Exception:
                lift, p = None, None
            if lift is None or p is None:
                rejected += 1
                continue
            applied += 1
            total += abs(lift)
            if lift == 0.0:
                continue
            t = log_map(self._x, p)
            for i in range(DIM):
                acc[i] += lift * t[i]
        self.rejected += rejected

        moved = False
        if total > 0:
            full = [a / total for a in acc]  # unscaled tangent -> consensus target
            if _norm(full) > _EPS:
                consensus = exp_map(self._x, full)
                v = [step_lr * c for c in full]
                new = [max(0.0, c) for c in exp_map(self._x, v)]
                n = _norm(new)
                if n > _EPS:
                    self._x = [c / n for c in new]
                    cn = [max(0.0, c) for c in consensus]
                    cnn = _norm(cn) or 1.0
                    self.last_distance_to_consensus = geodesic_distance(
                        self._x, [c / cnn for c in cn]
                    )
                    moved = True
        if moved:
            self.epoch += 1
        out = self.snapshot()
        out["applied"] = applied if moved else 0
        out["rejected"] = rejected
        return out
