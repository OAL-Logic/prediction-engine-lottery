from __future__ import annotations
import logging
import traceback
import numpy as np
import pandas as pd
import random
from typing import Any
from PySide6.QtCore import QThread, Signal, QObject

logger = logging.getLogger(__name__)

class JobSignals(QObject):
    """Signals for background analytical and optimization jobs."""
    progress = Signal(int, str)        # percentage (0-100), status message
    new_log = Signal(str, str)         # log message, severity level ('INFO', 'WARN', 'ERROR', 'RESONANCE')
    finished = Signal(dict)            # final analytical payload dictionary
    failed = Signal(str, str, str)     # error title, short message, traceback string

class ProphetJob(QThread):
    """
    Backward-compatible mock job for testing and general non-blocking tasks.
    Emits JobSignals matching the upgraded schema.
    """
    def __init__(self, task_name: str, params: dict | None = None, parent: QObject | None = None):
        super().__init__(parent)
        self.task_name = task_name
        self.params = params or {}
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Starting task: {self.task_name}...", "INFO")
        try:
            import time
            for i in range(10, 101, 10):
                if self.isInterruptionRequested():
                    self.signals.new_log.emit(f"Task {self.task_name} cancelled by user.", "WARN")
                    return
                time.sleep(0.1)
                self.signals.progress.emit(i, f"Processing node cluster {i//10}/10")
                self.signals.new_log.emit(f"Processing node cluster {i//10}/10...", "INFO")
            
            self.signals.new_log.emit(f"Task {self.task_name} completed successfully.", "SUCCESS")
            payload = {"status": "ok", "task": self.task_name}
            self.signals.finished.emit(payload)
        except Exception as e:
            tb_str = traceback.format_exc()
            err_msg = str(e) or type(e).__name__
            self.signals.new_log.emit(f"Task {self.task_name} failed: {err_msg}", "ERROR")
            self.signals.failed.emit(f"Task {self.task_name} Error", err_msg, tb_str)

class ForecastJob(QThread):
    """
    Runs core-engine forecasting calculations in a background thread.
    Builds a weighted consensus matrix from specified strategies and generates suggestions.
    """
    def __init__(
        self, 
        lottery_id: str, 
        strategies: list[str], 
        count: int = 1, 
        num_draws: int = 100, 
        pick_count: int | None = None, 
        parent: QObject | None = None
    ):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.strategies = strategies
        self.count = count
        self.num_draws = num_draws
        self.pick_count = pick_count
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Initializing forecast engine for game context: '{self.lottery_id}'...", "INFO")
        self.signals.progress.emit(5, "Loading draw database...")

        try:
            from engine.cli.utils import get_adapter
            from engine.strategies import get_strategy, _weighted_sample

            adapter = get_adapter(self.lottery_id)
            df = adapter.fetch()
            if df.empty:
                raise ValueError(f"No draw history found for lottery '{self.lottery_id}'.")

            df_slice = df.tail(self.num_draws)
            total_strategies = len(self.strategies)
            self.signals.new_log.emit(f"Loaded {len(df_slice)} draws. Running ensemble across {total_strategies} strategies...", "INFO")

            rules = adapter.rules
            lo, hi = rules.number_range
            pool_size = hi - lo + 1
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
                # Call suggest with count=1 just to generate a standard score mapping
                res = strat_obj.suggest(df_slice, rules, count=1, temperature=1.0)
                scores = res.scores
                
                score_arr = np.zeros(pool_size, dtype=float)
                for num, sc in scores.items():
                    if lo <= num <= hi:
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

            # Determine pick count (e.g. 6 for Mega-Sena, 15 for Lotofacil)
            pick = self.pick_count if self.pick_count is not None else rules.pick_count
            
            self.signals.progress.emit(90, "Generating consensus ticket suggestions...")
            tickets: list[list[int]] = []
            
            # 1. Deterministic Top-Pick Ticket (highest confidence)
            top_indices = np.argsort(consensus_matrix)[::-1][:pick]
            best_ticket = sorted([int(idx + lo) for idx in top_indices])
            tickets.append(best_ticket)
            
            # 2. Probability-Sampled Tickets (if count > 1)
            if self.count > 1:
                numbers_pool = list(range(lo, hi + 1))
                consensus_scores = {int(idx + lo): float(consensus_matrix[idx]) for idx in range(pool_size)}
                local_rng = random.Random()
                
                attempts = 0
                while len(tickets) < self.count and attempts < self.count * 15:
                    attempts += 1
                    sampled = _weighted_sample(numbers_pool, consensus_scores, pick, temperature=1.0, rng=local_rng)
                    ticket = sorted(sampled)
                    if ticket not in tickets:
                        tickets.append(ticket)

            # Package result
            confidence_scores = [float(consensus_matrix[num - lo]) for num in tickets[0]]
            result_payload = {
                "status": "success",
                "lottery_id": self.lottery_id,
                "tickets": tickets,
                "confidence_scores": confidence_scores,
                "strategy_weights": strategy_weights,
                "num_draws_analyzed": len(df_slice),
            }

            self.signals.progress.emit(100, "Forecast complete.")
            self.signals.new_log.emit(f"Generated {len(tickets)} ticket(s). First ticket: {tickets[0]} (Mean confidence: {np.mean(confidence_scores):.4f})", "RESONANCE")
            self.signals.finished.emit(result_payload)

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Forecast job error: {err_msg}", "ERROR")
            self.signals.failed.emit("Forecast Calculation Error", err_msg, tb_str)

class TrainJob(QThread):
    """
    Runs the Swarm Intelligence Genetic Algorithm in the background to evolve the 'Alpha Ticket'.
    """
    def __init__(
        self,
        lottery_id: str,
        generations: int = 50,
        pop_size: int = 100,
        strategy: str = "weighted",
        parent: QObject | None = None
    ):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.generations = generations
        self.pop_size = pop_size
        self.strategy = strategy
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Initializing swarm evolution on '{self.lottery_id}'...", "INFO")
        self.signals.progress.emit(5, "Loading draw database...")

        try:
            from engine.cli.utils import get_adapter
            from engine.strategies import get_strategy
            from engine.cli.commands.swarm import TicketDNA

            adapter = get_adapter(self.lottery_id)
            df = adapter.fetch()
            if df.empty:
                raise ValueError(f"No draw history found for lottery '{self.lottery_id}'.")
                
            rules = adapter.rules
            lo, hi = rules.number_range
            pick = rules.pick_count
            
            self.signals.progress.emit(10, f"Evaluating base '{self.strategy}' scores...")
            strat = get_strategy(self.strategy)
            scores = strat.score(df.tail(100), rules)
            
            dna = TicketDNA(rules)
            
            self.signals.progress.emit(15, "Initializing bee population...")
            population = []
            pool = list(range(lo, hi + 1))
            for _ in range(self.pop_size):
                if self.isInterruptionRequested():
                    return
                population.append(random.sample(pool, pick))
                
            def fitness(ticket: list[int]) -> float:
                strat_score = np.mean([scores.get(n, 0.0) for n in ticket])
                dna_score = dna.get_fitness(ticket)
                return float(strat_score * dna_score)

            self.signals.new_log.emit(f"Swarm primed. Evolving {self.pop_size} bees over {self.generations} generations...", "INFO")

            for gen in range(self.generations):
                if self.isInterruptionRequested():
                    self.signals.new_log.emit("Swarm training cancelled by user.", "WARN")
                    return

                # Sort by fitness
                population.sort(key=lambda t: fitness(t), reverse=True)
                
                # Keep top 20%
                new_pop = population[:self.pop_size // 5]
                
                # Fill the rest with offspring
                while len(new_pop) < self.pop_size:
                    if self.isInterruptionRequested():
                        return
                    # Crossover
                    parent1, parent2 = random.sample(population[:self.pop_size // 2], 2)
                    # Uniform crossover
                    child = []
                    for i in range(pick):
                        gene = random.choice([parent1, parent2])[i]
                        if gene not in child:
                            child.append(gene)
                    
                    # Fill missing if duplicates occurred
                    while len(child) < pick:
                        r = random.choice(pool)
                        if r not in child:
                            child.append(r)
                    
                    # Mutation (10% chance)
                    if random.random() < 0.1:
                        idx = random.randint(0, pick - 1)
                        while True:
                            m = random.choice(pool)
                            if m not in child:
                                child[idx] = m
                                break
                                
                    new_pop.append(child)
                
                population = new_pop
                
                # Emit progress and periodic telemetry logs
                progress_pct = int(20 + (gen / self.generations) * 80)
                self.signals.progress.emit(progress_pct, f"Gen {gen+1}/{self.generations}")
                
                if (gen + 1) % 10 == 0 or gen == 0:
                    current_best = sorted(population[0])
                    current_fit = fitness(current_best)
                    self.signals.new_log.emit(f"Gen {gen+1:02d}: Best fitness = {current_fit:.4f} {current_best}", "INFO")

            # Finish
            population.sort(key=lambda t: fitness(t), reverse=True)
            best_ticket = sorted(population[0])
            best_fitness = fitness(best_ticket)
            
            result_payload = {
                "status": "success",
                "ticket": best_ticket,
                "fitness": best_fitness,
                "generations": self.generations,
                "pop_size": self.pop_size
            }
            
            self.signals.progress.emit(100, "Swarm evolution complete.")
            self.signals.new_log.emit(f"Swarm evolved Alpha Ticket: {best_ticket} (Fitness: {best_fitness:.4f})", "RESONANCE")
            self.signals.finished.emit(result_payload)

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Swarm evolution error: {err_msg}", "ERROR")
            self.signals.failed.emit("Swarm Evolution Error", err_msg, tb_str)

class ThreadManager:
    """Orchestrates background threads to prevent UI lockup and coordinate cleanup."""
    def __init__(self) -> None:
        self.active_jobs: dict[str, QThread] = {}

    def start_job(self, task_id: str, job_or_name: QThread | str, params: dict[str, Any] | None = None) -> QThread | None:
        if task_id in self.active_jobs:
            existing_job = self.active_jobs[task_id]
            if existing_job.isRunning():
                logger.warning(f"Task '{task_id}' is already running. Action ignored.")
                return None
            else:
                self._cleanup_job(task_id)

        if isinstance(job_or_name, str):
            # Backward-compatible mock job
            job = ProphetJob(job_or_name, params)
        else:
            job = job_or_name

        self.active_jobs[task_id] = job
        job.finished.connect(lambda: self._cleanup_job(task_id))
        job.start()
        return job

    def stop_job(self, task_id: str) -> bool:
        if task_id in self.active_jobs:
            job = self.active_jobs[task_id]
            if job.isRunning():
                job.requestInterruption()
                # Cooperative request sent
                return True
        return False

    def _cleanup_job(self, task_id: str) -> None:
        if task_id in self.active_jobs:
            job = self.active_jobs.pop(task_id)
            job.deleteLater()
            logger.info(f"Background thread for task '{task_id}' cleaned up.")
