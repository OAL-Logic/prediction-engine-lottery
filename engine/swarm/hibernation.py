"""
Automated agent hibernation (Story 3.4).

Keeps a rolling window of per-agent "Lift over Random" (0.0 = random baseline,
positive = better, as in ``RewardSignal``) and hibernates an agent whose
full-window mean lift falls below a threshold. Each event is appended, with its
rationale, to an append-only JSONL ledger sink.
"""

from __future__ import annotations

import json
import math
import threading
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Set

from engine._paths import PROJECT_ROOT

WINDOW = 50
DEFAULT_THRESHOLD = 0.0
DEFAULT_LEDGER_PATH = PROJECT_ROOT / "data" / "forensic_ledger.jsonl"


def _valid_lift(lift: Any) -> Optional[float]:
    if isinstance(lift, bool):
        return None
    try:
        f = float(lift)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _pulse(message: str, level: str = "INFO") -> None:
    try:
        from engine.modules.telemetry import pulse

        pulse(message, level)
    except Exception:
        pass


class JsonlLedger:
    """Append-only sink: one JSON event per line. The file is created lazily."""

    def __init__(self, path: Optional[Any] = None):
        self.path = Path(path) if path is not None else DEFAULT_LEDGER_PATH
        self._lock = threading.Lock()

    def append(self, event: Dict[str, Any]) -> None:
        line = json.dumps(event, separators=(",", ":"), sort_keys=False) + "\n"
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(line)


class HibernationMonitor:
    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        window: int = WINDOW,
        ledger: Optional[Any] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        t = _valid_lift(threshold)
        if t is None:
            raise ValueError(f"threshold must be a finite number, got {threshold!r}")
        if isinstance(window, bool) or not isinstance(window, int) or window < 1:
            raise ValueError(f"window must be a positive int, got {window!r}")
        self.threshold = t
        self.window = window
        self._ledger = ledger if ledger is not None else JsonlLedger()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._windows: Dict[Any, Deque[float]] = {}
        self._hibernated: Set[Any] = set()

    def is_hibernated(self, agent_id: Any) -> bool:
        return agent_id in self._hibernated

    def hibernated_ids(self) -> List[Any]:
        return sorted(self._hibernated, key=lambda x: (str(type(x)), x))

    def record(self, agent_id: Any, lift: Any) -> bool:
        """Record one lift observation. Returns True if this call hibernated the agent."""
        value = _valid_lift(lift)
        if value is None or agent_id is None or agent_id in self._hibernated:
            return False
        win = self._windows.setdefault(agent_id, deque(maxlen=self.window))
        win.append(value)
        if len(win) < self.window:
            return False
        mean = sum(win) / len(win)
        if not mean < self.threshold:
            return False
        self._hibernated.add(agent_id)
        self._windows.pop(agent_id, None)
        self._log(agent_id, mean)
        return True

    def record_signals(self, signals: Iterable[Any]) -> List[Any]:
        """Record lifts from RewardSignal-like objects; return newly hibernated ids."""
        newly: List[Any] = []
        for sig in signals:
            try:
                agent_id = getattr(sig, "agent_id", None)
                lift = getattr(sig, "lift", None)
                if self.record(agent_id, lift):
                    newly.append(agent_id)
            except Exception:
                continue
        return newly

    def _log(self, agent_id: Any, mean: float) -> None:
        event = {
            "event": "agent_hibernated",
            "agent_id": agent_id,
            "window": self.window,
            "observations": self.window,
            "mean_lift": mean,
            "threshold": self.threshold,
            "timestamp": self._clock().isoformat(),
            "rationale": (
                f"mean lift over last {self.window} draws {mean:.4f} "
                f"< threshold {self.threshold:.4f}"
            ),
        }
        try:
            self._ledger.append(event)
        except Exception as exc:
            _pulse(
                f"Hibernation ledger write failed for agent {agent_id}: {exc}",
                "WARN",
            )
