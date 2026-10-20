"""
Vectorized Combinatorial Streaming Worker
=========================================
Executes large-scale combinatorial generation and filtering in background
threads using PySide6 QRunnable and QThreadPool.
Ensures zero UI thread blocking while computing high-throughput analytics:
- Combinations/second scan rate
- Surviving tickets count & reduction efficiency %
- Cooperative cancellation tokens
"""

from __future__ import annotations

import time
import itertools
import logging
from typing import List, Dict, Optional, Any
import numpy as np

from PySide6.QtCore import QRunnable, QObject, Signal, Slot

from desktop.src.core.models import (
    FilterNode, ToleranceRule, ToleranceMode, TicketReceipt, GenerationTelemetry
)
from desktop.src.services.engine_bridge import EngineBridge

logger = logging.getLogger(__name__)


class StreamingWorkerSignals(QObject):
    """Signals emitted by the StreamingCombinatorialWorker."""
    started = Signal()
    progress = Signal(object)      # Emits GenerationTelemetry
    chunk_ready = Signal(list)     # Emits List[TicketReceipt]
    finished = Signal(list, dict)  # Emits (List[TicketReceipt], summary_dict)
    cancelled = Signal()
    error = Signal(str)


class StreamingCombinatorialWorker(QRunnable):
    """
    QRunnable worker executing chunked combination generation, vectorized filter
    evaluation, and fault tolerance pruning in the Qt global thread pool.
    """

    def __init__(
        self,
        pool: List[int],
        pick_count: int,
        active_filters: List[FilterNode],
        tolerance: ToleranceRule,
        chunk_size: int = 100_000,
        max_survivors_cap: int = 10_000,
        last_draw: Optional[List[int]] = None
    ):
        super().__init__()
        self.pool = sorted(pool)
        self.pick_count = pick_count
        self.active_filters = active_filters
        self.tolerance = tolerance
        self.chunk_size = chunk_size
        self.max_survivors_cap = max_survivors_cap
        self.last_draw = last_draw
        
        self.signals = StreamingWorkerSignals()
        self._is_cancelled = False
        self.bridge = EngineBridge()

    def cancel(self) -> None:
        """Cooperative cancellation flag."""
        self._is_cancelled = True

    @Slot()
    def run(self) -> None:
        try:
            self.signals.started.emit()
            start_time = time.perf_counter()

            total_combinations = None
            try:
                import math
                total_combinations = math.comb(len(self.pool), self.pick_count)
            except Exception:
                total_combinations = 1_000_000

            total_scanned = 0
            total_survived = 0
            all_survivors: List[TicketReceipt] = []
            ticket_counter = 1

            comb_iter = itertools.combinations(self.pool, self.pick_count)

            while not self._is_cancelled:
                # 1. Pull next chunk
                chunk_tuples = list(itertools.islice(comb_iter, self.chunk_size))
                if not chunk_tuples:
                    break

                chunk_np = np.array(chunk_tuples, dtype=np.uint8)
                chunk_len = len(chunk_np)
                total_scanned += chunk_len

                # 2. Vectorized Filter Evaluation
                pass_matrix = self.bridge.evaluate_filter_chunk_vectorized(
                    chunk_np, self.active_filters, last_draw=self.last_draw
                )

                # 3. Fault Tolerance (Error Allowance) Mask
                survivor_mask = self.bridge.apply_tolerance_mask(pass_matrix, self.tolerance)
                surviving_combos = chunk_np[survivor_mask]
                num_survivors = len(surviving_combos)
                total_survived += num_survivors

                # Convert survivors to domain TicketReceipt objects
                chunk_receipts: List[TicketReceipt] = []
                for row in surviving_combos:
                    chunk_receipts.append(TicketReceipt(
                        ticket_id=ticket_counter,
                        numbers=row.tolist(),
                        confidence_score=0.95,
                        filter_pass_count=len(self.active_filters),
                        strategy_source="Vectorized Harmony Gate"
                    ))
                    ticket_counter += 1
                    if len(all_survivors) + len(chunk_receipts) >= self.max_survivors_cap:
                        break

                all_survivors.extend(chunk_receipts)
                if chunk_receipts:
                    self.signals.chunk_ready.emit(chunk_receipts)

                # 4. Telemetry Update
                elapsed = max(0.001, time.perf_counter() - start_time)
                rate = total_scanned / elapsed
                reduction_pct = 100.0 * (1.0 - (total_survived / total_scanned)) if total_scanned > 0 else 0.0

                telemetry = GenerationTelemetry(
                    combinations_scanned=total_scanned,
                    combinations_survived=total_survived,
                    reduction_rate_pct=round(reduction_pct, 2),
                    scan_rate_per_sec=round(rate, 1),
                    elapsed_seconds=round(elapsed, 2),
                    is_complete=False,
                    cancelled=False
                )
                self.signals.progress.emit(telemetry)

                if len(all_survivors) >= self.max_survivors_cap:
                    logger.info("Maximum survivor cap (%d) reached.", self.max_survivors_cap)
                    break

            if self._is_cancelled:
                self.signals.cancelled.emit()
                return

            total_elapsed = max(0.001, time.perf_counter() - start_time)
            summary = {
                "total_scanned": total_scanned,
                "total_survived": total_survived,
                "reduction_rate_pct": round(100.0 * (1.0 - (total_survived / max(1, total_scanned))), 2),
                "elapsed_seconds": round(total_elapsed, 2),
                "throughput_combos_sec": round(total_scanned / total_elapsed, 1),
            }

            self.signals.finished.emit(all_survivors, summary)

        except Exception as e:
            logger.exception("Error during combinatorial streaming: %s", e)
            self.signals.error.emit(str(e))
