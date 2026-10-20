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
        offset: int = 0,
        parent: QObject | None = None
    ):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.strategies = strategies
        self.count = count
        self.num_draws = num_draws
        self.pick_count = pick_count
        self.offset = max(0, offset)  # draws to hold back from the end (predict as of `offset` draws ago)
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

            df_held_back = df.iloc[: len(df) - self.offset] if self.offset > 0 else df
            if df_held_back.empty:
                raise ValueError(f"Offset {self.offset} exceeds available history ({len(df)} draws).")
            df_slice = df_held_back.tail(self.num_draws)
            total_strategies = len(self.strategies)
            offset_note = f" (as of {self.offset} draws ago)" if self.offset > 0 else ""
            self.signals.new_log.emit(f"Loaded {len(df_slice)} draws{offset_note}. Running ensemble across {total_strategies} strategies...", "INFO")

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

class SkipsJob(QThread):
    """
    Computes skip metrics (Actual Skips, Average Skip, Now Skip) for a specific number in the background.
    """
    def __init__(
        self,
        lottery_id: str,
        number: int,
        num_draws: int = 200,
        parent: QObject | None = None
    ):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.number = number
        self.num_draws = num_draws
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Initializing skips calculations for Ball {self.number:02d} on '{self.lottery_id}'...", "INFO")
        self.signals.progress.emit(10, "Loading draw database...")

        try:
            from engine.modules.storage import storage
            from engine.modules.skips import compute_skip_profile

            # Load draws (newest to oldest or vice versa; load_draws sorts draw_id ascending internally)
            df = storage.load_draws(self.lottery_id, limit=self.num_draws)
            if df.empty:
                raise ValueError(f"No draw history found for lottery '{self.lottery_id}'.")

            self.signals.progress.emit(50, "Computing skips sequence...")
            
            # Compute skips profile
            result_payload = compute_skip_profile(df, self.number)
            result_payload["status"] = "success"
            result_payload["lottery_id"] = self.lottery_id
            result_payload["num_draws_analyzed"] = len(df)

            self.signals.progress.emit(100, "Skips calculation complete.")
            self.signals.new_log.emit(
                f"Computed skips for Ball {self.number:02d}. Avg Skip: {result_payload['average_skip']:.2f}, Now Skip: {result_payload['now_skip']}",
                "RESONANCE"
            )
            self.signals.finished.emit(result_payload)

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Skips calculation error: {err_msg}", "ERROR")
            self.signals.failed.emit("Skips Calculation Error", err_msg, tb_str)


class FormulaVerificationJob(QThread):
    """
    Verification Desk 'Formula Leaderboard': walk-forward backtests each
    candidate strategy ('formula', in Lottery Studio's terms) over the last
    `depth` historical draws and ranks them by win rate / capture rate.

    Thin QThread wrapper around engine.services.backtest.run_backtest() —
    that function already implements "blind" walk-forward evaluation (each
    draw is scored using only draws strictly before it) and per-strategy
    summary stats; this job adds no verification logic of its own, only
    progress/signal plumbing via the existing `on_draw` callback hook.
    """
    def __init__(self, lottery_id: str, strategy_names: list[str], depth: int = 20, parent: QObject | None = None):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.strategy_names = strategy_names
        self.depth = max(1, depth)
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(
            f"Starting formula verification on '{self.lottery_id}' — "
            f"{len(self.strategy_names)} formula(s) x last {self.depth} draws...",
            "INFO",
        )
        self.signals.progress.emit(5, "Loading draw database...")

        try:
            from engine.services.backtest import run_backtest

            tested = {"n": 0}

            def _on_draw(draw_result):
                tested["n"] += 1
                pct = 10 + int(min(1.0, tested["n"] / self.depth) * 80)
                self.signals.progress.emit(pct, f"Backtested draw #{draw_result.draw_id} ({tested['n']}/{self.depth})")

            result = run_backtest(
                self.lottery_id,
                prev=f"1-{self.depth}",
                strategy_names=self.strategy_names,
                on_draw=_on_draw,
            )

            self.signals.progress.emit(92, "Ranking formulas...")

            leaderboard = []
            for name in result.strategy_names:
                summary = result.summary.get(name)
                if summary is None:
                    continue
                leaderboard.append({
                    "formula": name,
                    "draws_tested": len(result.draws),
                    "avg_rank": summary.avg_rank,
                    "capture_pct": summary.capture_pct,
                    "best_hit": summary.best_hit,
                    "win_rate_pct": summary.win_rate_pct,
                })
            leaderboard.sort(key=lambda r: (r["win_rate_pct"], r["capture_pct"]), reverse=True)

            self.signals.progress.emit(100, "Verification complete.")
            self.signals.new_log.emit(
                f"Formula verification complete. {len(leaderboard)} formula(s) ranked over {len(result.draws)} draws.",
                "RESONANCE",
            )
            self.signals.finished.emit({
                "status": "success",
                "lottery_id": self.lottery_id,
                "game_name": result.game_name,
                "leaderboard": leaderboard,
            })

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Formula verification error: {err_msg}", "ERROR")
            self.signals.failed.emit("Formula Verification Error", err_msg, tb_str)


def compute_metric_values(uid: str, combinations: np.ndarray, mid_point: int) -> np.ndarray:
    import numpy as np
    from engine.modules.filters import PRIMES, count_bits_64
    n_rows, k = combinations.shape
    
    # Sorting combinations is useful for positional/distance calculations
    sorted_combs = np.sort(combinations, axis=1)

    if uid == "structural_odd_count":
        return np.sum(combinations % 2 != 0, axis=1)
    elif uid == "structural_even_count":
        return np.sum(combinations % 2 == 0, axis=1)
    elif uid == "structural_prime_count":
        return np.sum(np.isin(combinations, PRIMES), axis=1)
    elif uid == "structural_ac_value":
        if k < 2: return np.zeros(n_rows, dtype=np.int32)
        bitmasks = np.zeros(n_rows, dtype=np.uint64)
        for i in range(k):
            for j in range(i + 1, k):
                diff = sorted_combs[:, j] - sorted_combs[:, i]
                bitmasks |= (np.uint64(1) << (diff.astype(np.uint64) - 1))
        unique_counts = count_bits_64(bitmasks)
        return unique_counts - (k - 1)
    elif uid == "structural_digit_sum":
        return np.sum((combinations // 10) + (combinations % 10), axis=1)
    elif uid == "structural_unit_sum":
        return np.sum(combinations % 10, axis=1)
    elif uid == "structural_high_count":
        return np.sum(combinations > mid_point, axis=1)
    elif uid == "structural_low_count":
        return np.sum(combinations <= mid_point, axis=1)
    elif uid.startswith("positional_ball_") and uid.endswith("_range"):
        try:
            ball_idx = int(uid.split("_")[2]) - 1
            if 0 <= ball_idx < k:
                return sorted_combs[:, ball_idx]
        except Exception:
            pass
    elif uid == "positional_first_last_distance":
        return sorted_combs[:, -1] - sorted_combs[:, 0]
    elif uid.startswith("positional_gap_"):
        try:
            parts = uid.split("_")
            idx1 = int(parts[2]) - 1
            idx2 = int(parts[3]) - 1
            if 0 <= idx1 < k and 0 <= idx2 < k:
                return np.abs(sorted_combs[:, idx2] - sorted_combs[:, idx1])
        except Exception:
            pass
    elif uid.startswith("algebraic_div_by_"):
        try:
            n = int(uid.split("_")[-1])
            return np.sum(combinations % n == 0, axis=1)
        except Exception:
            pass
            
    # Fallback to sum of combinations
    return np.sum(combinations, axis=1)


class LimitsCalculationJob(QThread):
    def __init__(self, lottery_id: str, active_filter_ids: list[str], limit: int = 50, parent: QObject | None = None):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.active_filter_ids = active_filter_ids
        self.limit = limit
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Starting auto calculate limits for '{self.lottery_id}' (lookback {self.limit} draws)...", "INFO")
        self.signals.progress.emit(10, "Fetching historical draws...")
        
        try:
            from engine.modules.storage import storage
            from engine.cli.utils import get_adapter
            
            df = storage.load_draws(self.lottery_id, limit=self.limit)
            if df.empty:
                raise ValueError("No draw history found.")
                
            combinations = np.array(df["numbers"].tolist())
            adapter = get_adapter(self.lottery_id)
            rules = adapter.rules
            number_range = rules.number_range
            mid_point = (number_range[0] + number_range[1]) // 2
            
            self.signals.progress.emit(40, "Calculating filter limits...")
            
            results = {}
            for idx, fid in enumerate(self.active_filter_ids):
                vals = compute_metric_values(fid, combinations, mid_point)
                min_v = int(np.min(vals))
                max_v = int(np.max(vals))
                results[fid] = (min_v, max_v)
                
                # Report progress
                pct = 40 + int((idx + 1) / len(self.active_filter_ids) * 50)
                self.signals.progress.emit(pct, f"Calculated bounds for {fid}...")
                
            self.signals.progress.emit(100, "Limits calculation complete.")
            self.signals.new_log.emit(f"Successfully auto-calculated limits for {len(results)} filters.", "RESONANCE")
            self.signals.finished.emit({"status": "success", "limits": results})
            
        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Auto limits calculation error: {err_msg}", "ERROR")
            self.signals.failed.emit("Auto Limits Error", err_msg, tb_str)


class PruningJob(QThread):
    def __init__(self, lottery_id: str, tickets: list[list[int]], active_filters: list[dict], logical_condition: dict, parent: QObject | None = None):
        super().__init__(parent)
        self.lottery_id = lottery_id
        self.tickets = tickets
        self.active_filters = active_filters
        self.logical_condition = logical_condition
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(f"Starting pruning on {len(self.tickets)} tickets in background thread...", "INFO")
        self.signals.progress.emit(10, "Initializing filter engine...")
        
        try:
            from engine.cli.utils import get_adapter
            from engine.modules.filters import registry
            
            if not self.tickets:
                self.signals.progress.emit(100, "No tickets to filter.")
                self.signals.finished.emit({"status": "success", "passed_indices": [], "elimination_counts": {}})
                return
                
            combinations = np.array(self.tickets)
            n_tickets = combinations.shape[0]
            adapter = get_adapter(self.lottery_id)
            rules = adapter.rules
            number_range = rules.number_range
            mid_point = (number_range[0] + number_range[1]) // 2
            
            # Store pass/fail matrix: shape (n_tickets, n_active_filters)
            n_filters = len(self.active_filters)
            if n_filters == 0:
                self.signals.progress.emit(100, "No active filters.")
                self.signals.finished.emit({
                    "status": "success",
                    "passed_indices": list(range(n_tickets)),
                    "elimination_counts": {}
                })
                return
                
            filter_results = np.zeros((n_tickets, n_filters), dtype=bool)
            elimination_counts = {}
            
            for i, item in enumerate(self.active_filters):
                fid = item["id"]
                ftype = item["type"]
                
                if ftype == "base":
                    lo, hi = item["lo"], item["hi"]
                    vals = compute_metric_values(fid, combinations, mid_point)
                    passed = (vals >= lo) & (vals <= hi)
                else: # advanced
                    f = registry.get(fid)
                    if not f:
                        passed = np.ones(n_tickets, dtype=bool)
                    else:
                        val = item.get("val", "")
                        passed = f.apply(combinations, rules)
                        if val and "-" in val:
                            try:
                                lo, hi = map(int, val.split("-"))
                                vals = compute_metric_values(fid, combinations, mid_point)
                                passed = (vals >= lo) & (vals <= hi)
                            except Exception:
                                pass
                                
                filter_results[:, i] = passed
                eliminated_count = int(np.sum(~passed))
                elimination_counts[fid] = eliminated_count
                
                pct = 10 + int((i + 1) / n_filters * 70)
                self.signals.progress.emit(pct, f"Evaluated filter {fid}...")
                
            # Combine results based on logical condition
            mode = self.logical_condition.get("mode", "AND")
            if mode == "AND":
                passed_mask = np.all(filter_results, axis=1)
            elif mode == "OR":
                passed_mask = np.any(filter_results, axis=1)
            else: # N-of-M
                n_min = self.logical_condition.get("n_min", 1)
                n_max = self.logical_condition.get("n_max", n_filters)
                match_counts = np.sum(filter_results, axis=1)
                passed_mask = (match_counts >= n_min) & (match_counts <= n_max)
                
            passed_indices = np.where(passed_mask)[0].tolist()
            
            self.signals.progress.emit(100, "Pruning complete.")
            self.signals.new_log.emit(
                f"Pruning finished. {len(passed_indices)} / {n_tickets} tickets passed, {n_tickets - len(passed_indices)} eliminated.",
                "RESONANCE"
            )
            self.signals.finished.emit({
                "status": "success",
                "passed_indices": passed_indices,
                "elimination_counts": elimination_counts
            })
            
        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Pruning error: {err_msg}", "ERROR")
            self.signals.failed.emit("Pruning Error", err_msg, tb_str)


class TicketStoreReductionJob(QThread):
    """
    Ticket Store 'Reduce (WRG Guarantee)': applies engine.modules.wheels_wrg
    .WheelingEngine's greedy set-cover reduction to an already-generated batch
    of tickets (the main window's Ticket Store), dropping tickets whose
    t-if-m coverage is already subsumed by others already kept. Thin QThread
    wrapper — WheelingEngine.reduce_tickets() does all the actual set-cover
    work; this job only remaps ticket numbers to the dense 1..N range that
    engine expects (same convention WheelingTab's WheelingWorker uses for
    get_gap_matrix()) and guards against a combinatorial explosion in the
    coverage universe C(pool_size, m), which is a plain Python loop with no
    interruption support.
    """
    SAFE_UNIVERSE_LIMIT = 50_000

    def __init__(self, tickets: list[list[int]], t: int, m: int, target_coverage: float = 1.0, parent: QObject | None = None):
        super().__init__(parent)
        self.tickets = tickets
        self.t = t
        self.m = m
        self.target_coverage = target_coverage
        self.signals = JobSignals()

    def run(self) -> None:
        self.signals.new_log.emit(
            f"Starting ticket store reduction on {len(self.tickets)} tickets (guarantee {self.t}-if-{self.m})...",
            "INFO",
        )
        self.signals.progress.emit(5, "Building coverage pool...")

        try:
            from math import comb
            from engine.modules.wheels_wrg import WheelingEngine

            if not self.tickets:
                self.signals.finished.emit({"status": "success", "kept_tickets": [], "original_count": 0, "reduced_count": 0})
                return

            pool = sorted({n for ticket in self.tickets for n in ticket})
            if self.m > len(pool):
                raise ValueError(f"'If drawn' (m={self.m}) exceeds the ticket store's pool size ({len(pool)} distinct numbers).")
            if self.t > self.m:
                raise ValueError(f"Guarantee (t={self.t}) cannot exceed m={self.m}.")
            if len(pool) > 64:
                raise ValueError(f"WheelingEngine supports pools up to 64 numbers (bit-packed limit); this store spans {len(pool)}.")

            universe = comb(len(pool), self.m)
            if universe > self.SAFE_UNIVERSE_LIMIT:
                raise ValueError(
                    f"Coverage universe C({len(pool)}, {self.m}) = {universe:,} target subsets is too large to "
                    f"reduce in the UI (limit {self.SAFE_UNIVERSE_LIMIT:,}). Narrow the ticket store's pool or "
                    f"raise 'm' first."
                )

            self.signals.progress.emit(15, f"Pool: {len(pool)} numbers, {universe:,} target subsets to cover...")
            pool_map = {n: i + 1 for i, n in enumerate(pool)}
            reverse_map = {i + 1: n for i, n in enumerate(pool)}
            shifted = np.array([[pool_map[n] for n in ticket] for ticket in self.tickets])

            wrg = WheelingEngine(len(pool), self.m)
            self.signals.progress.emit(30, "Running greedy WRG set-cover reduction...")
            kept_shifted = wrg.reduce_tickets(shifted, self.t, self.m, self.target_coverage)
            kept = [sorted(reverse_map[i] for i in ticket) for ticket in kept_shifted.tolist()]

            reduction_pct = (1.0 - (len(kept) / len(self.tickets))) * 100 if self.tickets else 0.0
            self.signals.progress.emit(100, "Reduction complete.")
            self.signals.new_log.emit(
                f"Ticket store reduced from {len(self.tickets)} to {len(kept)} tickets "
                f"({reduction_pct:.1f}% smaller) while preserving {self.t}-if-{self.m} coverage.",
                "RESONANCE",
            )
            self.signals.finished.emit({
                "status": "success",
                "kept_tickets": kept,
                "original_count": len(self.tickets),
                "reduced_count": len(kept),
                "pool_size": len(pool),
            })

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc) or type(exc).__name__
            self.signals.new_log.emit(f"Ticket store reduction error: {err_msg}", "ERROR")
            self.signals.failed.emit("Ticket Store Reduction Error", err_msg, tb_str)


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
