# MDR-101: Qt App Bootstrap and Threading Design

* **Status**: Accepted (Research Complete)
* **Date**: 2026-08-11
* **Author**: Antigravity (AI Assistant)
* **Decides**: Concurrency architecture, custom signal schema, worker templates, and thread-safe error handling for PySide6 integration with the backend engine.

---

## 1. Concurrency Architecture

To prevent the GUI from freezing during heavy engine computations (e.g. forecasts, simulations, calibrations, and grid-searches), all calculations will run asynchronously in background thread pools using PySide6's native `QThread` and cooperative interruption checks.

We evaluated two main concurrency models:
1. **`QThread` Worker Subclassing**: Native signal-slot support, fine-grained control, straightforward cooperative interruption. **Selected for stateful, long-running processes (forecasts, calibrations).**
2. **`QRunnable` + `QThreadPool`**: Reuses thread pools, lower memory overhead. Suitable for lightweight, quick operations.

### Custom Signal Schema (`JobSignals`)
Background threads will communicate with the Main GUI thread using a dedicated thread-safe signal object:

```python
from PySide6.QtCore import QObject, Signal

class JobSignals(QObject):
    progress = Signal(int, str)        # percentage (0-100), status message
    new_log = Signal(str, str)         # log message, severity level ('INFO', 'WARN', 'ERROR', 'RESONANCE')
    finished = Signal(dict)            # final analytical payload dictionary
    failed = Signal(str, str, str)     # error title, short message, traceback string
```

---

## 2. Forecast Worker Template

The following class subclasses `QThread` and wraps the core engine's forecasting calls, running them safely off the GUI thread:

```python
from __future__ import annotations
import traceback
import numpy as np
import pandas as pd
from typing import Any
from PySide6.QtCore import QThread
from PySide6.QtCore import QObject, Signal

class JobSignals(QObject):
    progress = Signal(int, str)
    new_log = Signal(str, str)
    finished = Signal(dict)
    failed = Signal(str, str, str)

class ForecastJob(QThread):
    def __init__(self, lottery_id: str, strategies: list[str], num_draws: int = 100, pick_count: int = 15, parent: QThread | None = None):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.strategies = strategies
        self.num_draws = num_draws
        self.pick_count = pick_count
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Initializing forecast engine for game context: '{self.lottery_id}'...", "INFO")
        self.signals.progress.emit(5, "Loading draw database...")

        try:
            from engine.cli.utils import get_adapter
            from engine.strategies import get_strategy

            adapter = get_adapter(self.lottery_id)
            df = adapter.fetch()
            if df.empty:
                raise ValueError(f"No draw history found for lottery '{self.lottery_id}'.")

            df_slice = df.tail(self.num_draws)
            total_strategies = len(self.strategies)
            self.signals.new_log.emit(f"Loaded {len(df_slice)} draws. Running ensemble across {total_strategies} strategies...", "INFO")

            rules = adapter.rules
            pool_size = rules.number_range[1] - rules.number_range[0] + 1
            strategy_scores: dict[str, np.ndarray] = {}
            strategy_weights: dict[str, float] = {}

            for idx, strat_name in enumerate(self.strategies, start=1):
                if self.isInterruptionRequested():
                    self.signals.new_log.emit("Forecast job cancelled by user.", "WARN")
                    return

                pct = int(10 + (idx / total_strategies) * 70)
                self.signals.progress.emit(pct, f"Evaluating strategy: {strat_name}")
                self.signals.new_log.emit(f"Executing strategy node: '{strat_name}'...", "INFO")

                strat_obj = get_strategy(strat_name)
                res = strat_obj.suggest(df_slice, rules, count=1, temperature=1.0)
                scores = res.scores
                
                score_arr = np.zeros(pool_size, dtype=float)
                lo = rules.number_range[0]
                for num, sc in scores.items():
                    if rules.number_range[0] <= num <= rules.number_range[1]:
                        score_arr[num - lo] = max(0.0, sc)

                std_dev = float(np.std(score_arr))
                weight = 1.0 / (1.0 + std_dev)

                strategy_scores[strat_name] = score_arr
                strategy_weights[strat_name] = weight

            self.signals.progress.emit(85, "Aggregating weighted consensus matrix...")
            consensus_matrix = np.zeros(pool_size, dtype=float)
            total_weight = sum(strategy_weights.values()) or 1.0

            for strat_name, score_arr in strategy_scores.items():
                w = strategy_weights[strat_name] / total_weight
                consensus_matrix += score_arr * w

            top_indices = np.argsort(consensus_matrix)[::-1][:rules.pick_count]
            selected_numbers = sorted([int(idx + lo) for idx in top_indices])
            confidence_scores = [float(consensus_matrix[idx]) for idx in top_indices]

            result_payload = {
                "status": "success",
                "lottery_id": self.lottery_id,
                "ticket": selected_numbers,
                "confidence_scores": confidence_scores,
                "strategy_weights": strategy_weights,
                "num_draws_analyzed": len(df_slice),
            }

            self.signals.progress.emit(100, "Forecast complete.")
            self.signals.new_log.emit(f"Generated ticket: {selected_numbers} (Mean confidence: {np.mean(confidence_scores):.4f})", "RESONANCE")
            self.signals.finished.emit(result_payload)

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Forecast job error: {err_msg}", "ERROR")
            self.signals.failed.emit("Forecast Calculation Error", err_msg, tb_str)
```

---

## 3. Thread Manager Design

The `ThreadManager` class will coordinate launching background tasks, preventing duplicate job triggers, clean garbage collection, and cancellation support.

```python
import logging
from PySide6.QtCore import QThread

logger = logging.getLogger(__name__)

class ThreadManager:
    def __init__(self):
        self.active_jobs: dict[str, QThread] = {}

    def start_job(self, task_id: str, job: QThread) -> QThread | None:
        if task_id in self.active_jobs:
            existing_job = self.active_jobs[task_id]
            if existing_job.isRunning():
                logger.warning(f"Task '{task_id}' is already running. Action ignored.")
                return None
            else:
                self._cleanup_job(task_id)

        self.active_jobs[task_id] = job
        job.finished.connect(lambda: self._cleanup_job(task_id))
        job.start()
        return job

    def stop_job(self, task_id: str) -> bool:
        if task_id in self.active_jobs:
            job = self.active_jobs[task_id]
            if job.isRunning():
                job.requestInterruption()
                return True
        return False

    def _cleanup_job(self, task_id: str) -> None:
        if task_id in self.active_jobs:
            job = self.active_jobs.pop(task_id)
            job.deleteLater()
            logger.info(f"Background thread for task '{task_id}' cleaned up.")
```

---

## 4. GUI Thread-Safety & `QMessageBox` Integration

To satisfy Qt's **strict GUI thread affinity rule**, background worker threads are forbidden from instantiating dialog boxes. Instead, when an exception occurs inside a worker thread, it must:
1. Catch the exception and convert the traceback to a string.
2. Emit the `failed` signal with the traceback and error messages.
3. The slot on the Main GUI thread receives the signal, logs the error, and pops up a `QMessageBox` showing the details.

### Main Window Handler
```python
def handle_job_failure(self, title: str, message: str, traceback_str: str):
    self.predict_tab.progress_bar.setValue(0)
    self.predict_tab.predict_button.setEnabled(True)
    self.predict_tab.status_label.setText("Engine State: ERROR")
    self.telemetry_tab.append_log(f"CRITICAL: {title} - {message}", "ERROR")

    msg_box = QMessageBox(self)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText("An error occurred while executing the backend engine task.")
    msg_box.setInformativeText(message)
    msg_box.setDetailedText(traceback_str)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    msg_box.exec()
```
