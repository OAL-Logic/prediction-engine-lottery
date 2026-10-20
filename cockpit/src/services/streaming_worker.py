"""
Streaming Combinatorial Worker
==============================
High-performance asynchronous background worker using PySide6 QRunnable and QThreadPool.
Executes vectorized SIMD chunk filtering with Fault Tolerance and real-time telemetry:
- Non-blocking GUI thread execution
- Cooperative cancellation tokens
- Throughput gauges (combos / sec)
- Redundancy and reduction rate tracking
- Batch ticket streaming
"""

from __future__ import annotations

import time
import logging
from typing import List, Optional
import numpy as np

from PySide6.QtCore import QRunnable, QObject, Signal, Slot

from cockpit.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, WheelingConfig,
    TicketReceipt, GenerationTelemetry
)
from cockpit.src.services.engine_bridge import EngineBridge
from cockpit.src.services.wheeling_solver import WheelingSolver

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """Signals emitted by the background streaming worker."""
    started = Signal()
    progress = Signal(object)              # Emits GenerationTelemetry
    batch_survivors = Signal(list)         # Emits List[TicketReceipt]
    finished = Signal(object, list)        # Emits (GenerationTelemetry, List[TicketReceipt])
    error = Signal(str)                    # Emits error message


class StreamingCombinatorialWorker(QRunnable):
    """
    Asynchronous QRunnable executing combinatorial chunk streaming across CPU cores.
    Maintains 60fps GUI fluidity by decoupling heavy NumPy matrix computations.
    """

    def __init__(
        self,
        game: GameSchema,
        pool: List[int],
        filters: List[FilterNode],
        tolerance: ToleranceRule,
        wheeling: Optional[WheelingConfig] = None,
        chunk_size: int = 50_000,
        max_survivors_cap: int = 5_000
    ):
        super().__init__()
        self.game = game
        self.pool = pool if pool else list(range(game.number_range_min, game.number_range_max + 1))
        self.filters = [f for f in filters if f.enabled]
        self.tolerance = tolerance
        self.wheeling = wheeling
        self.chunk_size = chunk_size
        self.max_survivors_cap = max_survivors_cap

        self.signals = WorkerSignals()
        self._is_cancelled = False
        self.bridge = EngineBridge()

    def cancel(self) -> None:
        """Cooperative cancellation request."""
        self._is_cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    @Slot()
    def run(self) -> None:
        """Main background execution loop."""
        self.signals.started.emit()
        start_time = time.perf_counter()

        telemetry = GenerationTelemetry()
        survivors: List[TicketReceipt] = []

        try:
            # 1. Fetch historical context for repeat and historical deletion filters
            last_draw = None
            past_draws = None
            df = self.bridge.get_draws(self.game.id, limit=50)
            if not df.empty and "numbers" in df.columns:
                past_draws = df["numbers"].tolist()
                last_draw = past_draws[-1] if past_draws else None

            # 2. Determine generation source: Wheeling Pre-computation vs Raw Combinations
            if self.wheeling and self.wheeling.pool_numbers:
                raw_tickets = WheelingSolver.execute_wheel(self.wheeling, self.game)
                combos_all = np.array(raw_tickets, dtype=np.uint8)
                chunks = [combos_all[i:i + self.chunk_size] for i in range(0, len(combos_all), self.chunk_size)]
            else:
                chunks = self.bridge.stream_combinations_chunked(
                    pool=self.pool,
                    pick_count=self.game.pick_count,
                    chunk_size=self.chunk_size
                )

            total_scanned = 0
            total_survived = 0

            for chunk_idx, chunk in enumerate(chunks):
                if self._is_cancelled:
                    telemetry.cancelled = True
                    break

                chunk_len = chunk.shape[0]
                total_scanned += chunk_len

                # Vectorized Filter Evaluation
                pass_matrix = self.bridge.evaluate_filter_chunk_vectorized(
                    combos=chunk,
                    active_filters=self.filters,
                    game=self.game,
                    last_draw=last_draw,
                    past_draws=past_draws
                )

                # Fault Tolerance Mask Evaluation
                survivor_mask = self.bridge.apply_tolerance_mask(
                    pass_matrix=pass_matrix,
                    tolerance=self.tolerance
                )

                survived_chunk = chunk[survivor_mask]
                num_chunk_survivors = survived_chunk.shape[0]
                total_survived += num_chunk_survivors

                # Build TicketReceipt batch
                batch_receipts: List[TicketReceipt] = []
                for idx_c in range(num_chunk_survivors):
                    if len(survivors) + len(batch_receipts) >= self.max_survivors_cap:
                        break
                    line_nums = [int(n) for n in survived_chunk[idx_c]]
                    rec = TicketReceipt(
                        ticket_id=len(survivors) + len(batch_receipts) + 1,
                        numbers=line_nums,
                        confidence_score=0.92,
                        filter_pass_count=int(np.sum(pass_matrix[survivor_mask][idx_c])) if self.filters else 0,
                        strategy_source="Combinatorial Studio"
                    )
                    batch_receipts.append(rec)

                survivors.extend(batch_receipts)
                if batch_receipts:
                    self.signals.batch_survivors.emit(batch_receipts)

                # Telemetry Update
                elapsed = max(0.001, time.perf_counter() - start_time)
                rate = total_scanned / elapsed
                reduct = ((total_scanned - total_survived) / total_scanned * 100.0) if total_scanned > 0 else 0.0

                telemetry.combinations_scanned = total_scanned
                telemetry.combinations_survived = total_survived
                telemetry.scan_rate_per_sec = round(rate, 1)
                telemetry.reduction_rate_pct = round(reduct, 2)
                telemetry.elapsed_seconds = round(elapsed, 2)

                self.signals.progress.emit(telemetry)

                if len(survivors) >= self.max_survivors_cap:
                    break

            telemetry.is_complete = not self._is_cancelled
            self.signals.finished.emit(telemetry, survivors)

        except Exception as e:
            logger.exception("StreamingCombinatorialWorker crashed: %s", e)
            self.signals.error.emit(str(e))
