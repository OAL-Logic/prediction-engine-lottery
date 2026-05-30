from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import pandas as pd
from datetime import date

from engine.api.models import (
    GameRulesSchema, GameSummary, AnalysisResultSchema,
    SuggestionRequest, SuggestionResponse, BacktestRequest, CheckRequest,
    OddsResponse, OddsTier, PruningResponse, PruningMetricsSchema,
    CalibrateRequest, TuneRequest,
    SacredManifoldRequest, SacredManifoldResponse, APIExpertSuggestRequest,
    SumDistributionResponse, GapAnalysisResponse,
    CompareResponse, CompareItem,
    WheelRequest, WheelResponse,
    TicketGradeRequest, HealthResponse
)
from engine.adapters.registry import registry as game_registry
from engine.cli.utils import get_adapter
from engine.modules.frequency import analyze as analyze_frequency
from engine.strategies import get_strategy, list_strategies
import engine.strategies.statistical # Trigger registration
import engine.strategies.fun         # Trigger registration

import time
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from starlette.responses import JSONResponse

app = FastAPI(
    title="Prediction Engine Sidecar",
    description="REST API for lottery analysis and ticket suggestion.",
    version="11.2.0"
)

_APP_START_TIME = time.time()

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    deadline_header = request.headers.get("X-Request-Deadline")
    if deadline_header:
        try:
            deadline = float(deadline_header)
            timeout = deadline - time.time()
            if timeout <= 0:
                return JSONResponse(status_code=408, content={"detail": "Request deadline already exceeded"})
            
            # Enforce timeout for the entire request
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            return JSONResponse(status_code=408, content={"detail": "Propagated request deadline exceeded"})
        except ValueError:
            pass # Ignore malformed headers
            
    return await call_next(request)

@app.get("/")
async def root():
    return {"message": "Prediction Engine Sidecar is active", "status": "online"}

@app.get("/games", response_model=List[GameSummary])
async def list_games():
    # In a real scenario, we'd list all registered adapters
    # For now, we'll hardcode the known ones or use the registry if it supports listing
    from engine.adapters.registry import ADAPTERS
    results = []
    for name, adapter_cls in ADAPTERS.items():
        adapter = adapter_cls()
        df = adapter.load_data()
        last_draw = df.iloc[-1] if not df.empty else None
        
        results.append(GameSummary(
            name=name,
            last_draw_id=int(last_draw["draw_id"]) if last_draw is not None else None,
            last_draw_date=last_draw["date"].date() if last_draw is not None else None,
            total_draws=len(df)
        ))
    return results



@app.post("/games/{name:path}/fetch")
async def fetch_game_data(name: str, background_tasks: BackgroundTasks):
    try:
        adapter = get_adapter(name)
        # Run fetch in background as it might be slow
        background_tasks.add_task(adapter.fetch_data)
        return {"message": f"Fetch started for {name}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/games/{name:path}/analysis", response_model=AnalysisResultSchema)
async def analyze_game(name: str):
    try:
        adapter = get_adapter(name)
        df = adapter.load_data()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available for analysis. Run fetch first.")
        
        freq = analyze_frequency(df, adapter.rules)
        return AnalysisResultSchema(
            game=name,
            draw_count=len(df),
            hot_numbers=freq["hot_numbers"],
            cold_numbers=freq["cold_numbers"],
            expected_frequency=freq["expected_frequency"],
            chi_squared_p_value=freq["chi_squared_p_value"],
            is_predictive=freq["is_predictive"],
            summary=f"Analysis based on {len(df)} draws."
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/games/{name:path}/suggest", response_model=SuggestionResponse)
async def suggest_tickets(name: str, request: SuggestionRequest):
    try:
        adapter = get_adapter(name)
        df = adapter.load_data()
        
        # Build strategy kwargs from request
        kwargs = {}
        if request.full_name: kwargs["full_name"] = request.full_name
        if request.birth_date: kwargs["birth_date"] = request.birth_date
        if request.topic: kwargs["topic"] = request.topic
        if request.adaptive_window: kwargs["adaptive_window"] = True
        
        # Handle comma-separated strategies (Ensemble)
        strat_names = [s.strip() for s in request.strategy.split(",")]
        
        # ── (v10.0) High-Fidelity Ensemble Support ───────────────────────────
        if len(strat_names) > 1:
            from engine.strategies.ml.ensemble import VotingEnsemble
            strat = VotingEnsemble(members=strat_names)
        else:
            strat = get_strategy(strat_names[0], **kwargs)
        
        result = strat.suggest(
            df, 
            adapter.rules,
            count=request.count,
            temperature=request.temperature,
            history_limit=request.history_limit,
            seed=request.seed,
            pick=request.pick,
            pool=request.pool,
            key=request.key,
            filters=request.filters
        )
        
        return SuggestionResponse(
            tickets=result.tickets,
            confidence=result.confidence,
            metadata=result.metadata,
            strategy_used=request.strategy
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/games/{name:path}/backtest")
async def backtest_strategy(name: str, request: BacktestRequest):
    try:
        from engine.cli.commands.backtest import backtest as backtest_impl
        # For API, we'll capture output or return a structured summary
        # Note: calling CLI impl directly might print to stdout. 
        # In a real API we'd refactor the core logic out.
        backtest_impl(
            lottery=name,
            draw_id=request.draw_ids,
            prev=request.prev,
            strategy=request.strategy,
            numbers=None,
            count=request.count,
            temperature=request.temperature,
            limit=request.limit,
            summary=request.summary,
            show_map=request.show_map,
            config=None,
            export_md=None
        )
        return {"message": "Backtest completed", "game": name, "strategy": request.strategy}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/games/{name:path}/check")
async def check_ticket(name: str, request: CheckRequest):
    try:
        from engine.modules.filters import get_root_sum, get_odd_count, get_decade_metrics
        adapter = get_adapter(name)
        
        # Basic check logic
        res = {
            "numbers": request.numbers,
            "sum": sum(request.numbers),
            "odd_count": get_odd_count(request.numbers),
            "even_count": len(request.numbers) - get_odd_count(request.numbers),
            "root_sum": get_root_sum(request.numbers),
            "decades": get_decade_metrics(request.numbers)
        }
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/games/{name:path}/odds", response_model=OddsResponse)
async def get_odds(name: str):
    try:
        from math import comb
        adapter = get_adapter(name)
        rules = adapter.rules
        
        def _hyp_prob(pool, pick, match):
            denom = comb(pool, pick)
            if denom == 0: return 0.0
            return (comb(pick, match) * comb(pool - pick, pick - match)) / denom

        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        tiers = []
        
        for t in sorted(rules.prize_tiers, reverse=True):
            p = _hyp_prob(pool_size, rules.pick_count, t)
            tiers.append(OddsTier(
                tier=t,
                probability=p,
                odds_1_in_x=1.0/p if p > 0 else 0
            ))
            
        return OddsResponse(
            game=name,
            tiers=tiers,
            ticket_price=rules.ticket_price,
            currency=rules.currency
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/games/{name:path}/prune", response_model=PruningResponse)
async def prune_strategies(name: str, window: int = 30, threshold: float = 0.02):
    try:
        from engine.modules.pruning import run_pruning_audit
        adapter = get_adapter(name)
        
        # Use default strategies for API pruning
        from engine.strategies import CURATED_PRESETS
        s_list = CURATED_PRESETS.get("default", ["weighted", "markov", "bayesian"])
        
        metrics = run_pruning_audit(adapter, s_list, window=window, threshold=threshold)
        
        schema_metrics = [
            PruningMetricsSchema(
                strategy_name=m.strategy_name,
                lift_over_random=m.lift_over_random,
                avg_rank=m.avg_rank,
                best_hit=m.best_hit,
                is_hibernated=m.is_hibernated
            ) for m in metrics
        ]
        
        return PruningResponse(
            game=name,
            window=window,
            threshold=threshold,
            metrics=schema_metrics
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/games/{name:path}/calibrate")
async def calibrate_game(name: str, request: CalibrateRequest, background_tasks: BackgroundTasks):
    try:
        from engine.cli.commands.calibrate import calibrate as calibrate_impl
        # Run calibrate in background as it is slow
        background_tasks.add_task(
            calibrate_impl, 
            name, 
            request.draws, 
            request.strategies, 
            request.limit, 
            None, # export_md
            request.min_training
        )
        return {"message": f"Calibration started for {name}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/games/{name:path}/tune")
async def tune_game(name: str, request: TuneRequest, background_tasks: BackgroundTasks):
    try:
        from engine.cli.commands.tune import tune as tune_impl
        # Run tune in background as it is extremely slow
        background_tasks.add_task(
            tune_impl,
            name,
            request.draws,
            request.limit,
            request.strategies,
            False, # no_grid
            request.metric,
            request.top,
            "flat", # fmt
            None, # output
            None, # export_md
            30 # min_training
        )
        return {"message": f"Optimization (tuning) started for {name}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/strategies")
async def get_strategies():
    return list_strategies()

@app.post("/games/{name:path}/sacred-manifold", response_model=SacredManifoldResponse)
async def get_sacred_manifold(name: str, request: SacredManifoldRequest):
    try:
        from engine.modules.geometry import get_manifold_coords, calculate_symmetry_metrics
        adapter = get_adapter(name)
        rules = adapter.rules
        
        coords = {}
        for num in request.numbers:
            x, y, z = get_manifold_coords(num, rules, request.manifold)
            coords[num] = [x, y, z]
            
        metrics = calculate_symmetry_metrics(request.numbers, rules, request.manifold)
        
        return SacredManifoldResponse(
            game=name,
            numbers=request.numbers,
            manifold=request.manifold,
            coordinates=coords,
            center_of_mass=list(metrics["center_of_mass"]),
            resonance=metrics["resonance"],
            reflection_h=metrics["reflection_h"],
            reflection_v=metrics["reflection_v"],
            symmetry_grade=metrics["symmetry_grade"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/games/{name:path}/sacred-manifold/transits")
async def get_sacred_manifold_transits(name: str):
    try:
        from engine.modules.environment import EnvironmentalService
        env = EnvironmentalService()
        jitter = env.get_jitter()
        
        import time
        t = time.time()
        celestial_angle = (int(t) % 360)
        
        return {
            "game": name,
            "celestial_angle": celestial_angle,
            "solar_kp": jitter.get("kp", 3.0),
            "seismic_mag": jitter.get("seismic_mag", 0.0),
            "total_boost": jitter.get("total_boost", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/games/{name:path}/expert-suggest")
async def api_expert_suggest(name: str, request: APIExpertSuggestRequest, background_tasks: BackgroundTasks):
    try:
        from engine.cli.commands.expert_suggest import expert_suggest as expert_suggest_impl
        background_tasks.add_task(
            expert_suggest_impl,
            name,
            request.budget,
            request.draws,
            request.start_bankroll,
            None,
            None
        )
        return {"message": f"Expert Suggestion & Portfolio Simulation started for {name}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Sprint 2 Gap Closure Endpoints ───────────────────────────────────────────


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check with uptime, version, and resource counts."""
    from engine.adapters.registry import registry as reg
    strategy_count = len(STRATEGY_REGISTRY) if 'STRATEGY_REGISTRY' in dir() else 0
    try:
        from engine.strategies import STRATEGY_REGISTRY
        strategy_count = len(STRATEGY_REGISTRY)
    except Exception:
        pass

    return HealthResponse(
        status="healthy",
        version="11.2.0",
        uptime_seconds=round(time.time() - _APP_START_TIME, 2),
        registered_games=len(reg.list_games()),
        registered_strategies=strategy_count
    )


@app.get("/games/{name:path}/sum-distribution", response_model=SumDistributionResponse)
async def get_sum_distribution(name: str, coverage: float = 0.70):
    """Sum probability distribution (PMF) with 70% most-probable range."""
    try:
        from engine.modules.sum_range import most_probable_range, pmf, moments
        adapter = get_adapter(name)
        rules = adapter.rules

        lo_sum, hi_sum, midpoint, sigma = most_probable_range(rules, coverage=coverage)

        # Compute PMF (can be expensive for large pools — limit to manageable sizes)
        lo, hi = rules.number_range
        pool_size = hi - lo + 1
        sum_pmf = {}
        if pool_size <= 70:  # Only compute exact PMF for reasonable pool sizes
            sum_pmf = pmf(rules)
            # Convert numpy keys to int for JSON serialisation
            sum_pmf = {int(k): round(float(v), 8) for k, v in sum_pmf.items()}

        return SumDistributionResponse(
            game=name,
            midpoint=round(midpoint, 2),
            sigma=round(sigma, 2),
            range_lo=lo_sum,
            range_hi=hi_sum,
            coverage=coverage,
            pmf=sum_pmf
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/games/{name:path}/gap/{number}", response_model=GapAnalysisResponse)
async def get_gap_analysis(name: str, number: int):
    """Per-number gap (recency / overdue) analysis."""
    try:
        from engine.modules.deviation import analyze as analyze_deviation
        adapter = get_adapter(name)
        df = adapter.load_data()
        if df.empty:
            raise HTTPException(status_code=400, detail="No data available. Run fetch first.")

        rules = adapter.rules
        lo, hi = rules.number_range
        if not (lo <= number <= hi):
            raise HTTPException(status_code=400, detail=f"Number {number} out of range [{lo}, {hi}]")

        result = analyze_deviation(df, rules)

        # Find the row for this specific number
        row = result.table[result.table["number"] == number]
        if row.empty:
            raise HTTPException(status_code=404, detail=f"Number {number} not found in analysis")

        row = row.iloc[0]
        gap_info = result.gap_stats.get(number, {})

        return GapAnalysisResponse(
            game=name,
            number=number,
            last_seen_draw=int(row["last_seen_draw"]),
            draws_since_last=int(row["draws_since_last"]),
            expected_interval=float(row["expected_interval"]),
            deviation_ratio=float(row["deviation_ratio"]),
            gap_mean=gap_info.get("mean"),
            gap_std=gap_info.get("std"),
            gap_max=gap_info.get("max"),
            gap_min=gap_info.get("min"),
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/games/compare", response_model=CompareResponse)
async def compare_games():
    """Cross-game odds comparison ranked by jackpot odds."""
    try:
        from engine.adapters.registry import ADAPTERS
        from engine.odds.comparator import compare_lotteries

        rules_list = []
        for adapter_name, adapter_cls in ADAPTERS.items():
            try:
                adapter = adapter_cls()
                rules_list.append(adapter.rules)
            except Exception:
                continue

        results = compare_lotteries(rules_list)
        items = [
            CompareItem(
                name=r.name,
                jackpot_odds=r.jackpot_odds,
                ticket_price=r.ticket_price,
                currency=r.currency,
                efficiency_score=round(r.efficiency_score, 4)
            ) for r in results
        ]
        return CompareResponse(games=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/games/{name:path}/wheel", response_model=WheelResponse)
async def generate_wheel(name: str, request: WheelRequest):
    """Generate a covering-design wheel for the given pool of numbers."""
    try:
        from engine.wheels import generate_full_wheel, generate_key_wheel, generate_abbreviated_wheel
        adapter = get_adapter(name)
        rules = adapter.rules

        pool = sorted(request.pool)

        if request.wheel_type == "full":
            tickets = generate_full_wheel(pool, rules.pick_count)
        elif request.wheel_type == "key":
            key = request.key_number or pool[0]
            tickets = generate_key_wheel(pool, rules.pick_count, [key])
        elif request.wheel_type == "abbreviated":
            guarantee = request.guarantee or (rules.pick_count - 1)
            tickets = generate_abbreviated_wheel(pool, rules.pick_count, guarantee)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown wheel type: {request.wheel_type}")

        return WheelResponse(
            game=name,
            wheel_type=request.wheel_type,
            ticket_count=len(tickets),
            tickets=[sorted(t) for t in tickets]
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/games/{name:path}/ticket-grade")
async def grade_ticket(name: str, request: TicketGradeRequest):
    """Grade a user-submitted ticket across multiple quality dimensions."""
    try:
        from engine.modules.filters import get_root_sum, get_odd_count, get_decade_metrics
        from engine.modules.sum_range import most_probable_range, classify

        adapter = get_adapter(name)
        rules = adapter.rules
        numbers = sorted(request.numbers)

        # Validate
        if not rules.validate(numbers):
            raise HTTPException(status_code=400, detail="Invalid ticket for this game")

        # Structural metrics
        odd_count = get_odd_count(numbers)
        even_count = len(numbers) - odd_count
        total_sum = sum(numbers)
        root_sum = get_root_sum(numbers)
        decades = get_decade_metrics(numbers)

        # Sum range analysis
        lo_sum, hi_sum, midpoint, sigma = most_probable_range(rules)
        sum_class, z_score = classify(numbers, rules)

        # Parity balance (ideal: close to 50/50)
        parity_ratio = min(odd_count, even_count) / max(odd_count, even_count) if max(odd_count, even_count) > 0 else 0

        # Decade spread
        decade_set = set(n // 10 for n in numbers)
        decade_spread = len(decade_set)

        # Consecutive check
        sorted_nums = sorted(numbers)
        consecutive_pairs = sum(1 for i in range(len(sorted_nums) - 1) if sorted_nums[i + 1] - sorted_nums[i] == 1)

        # Grade logic
        grade_points = 0
        max_points = 5
        notes = []

        if sum_class == "in":
            grade_points += 1
            notes.append("✅ Sum within 70% probable range")
        else:
            notes.append(f"⚠️ Sum {sum_class} 70% range (z={z_score:.2f})")

        if 0.4 <= parity_ratio <= 1.0:
            grade_points += 1
            notes.append("✅ Good parity balance")
        else:
            notes.append("⚠️ Extreme odd/even imbalance")

        if decade_spread >= 3:
            grade_points += 1
            notes.append(f"✅ Spans {decade_spread} decades")
        else:
            notes.append(f"⚠️ Only {decade_spread} decade(s)")

        if consecutive_pairs <= 2:
            grade_points += 1
            notes.append("✅ Few consecutive numbers")
        else:
            notes.append(f"⚠️ {consecutive_pairs} consecutive pairs")

        # Spread check
        spread = sorted_nums[-1] - sorted_nums[0]
        lo, hi = rules.number_range
        pool_range = hi - lo
        if spread >= pool_range * 0.5:
            grade_points += 1
            notes.append("✅ Good number spread")
        else:
            notes.append("⚠️ Numbers clustered too tightly")

        # Letter grade
        grade_map = {5: "A+", 4: "A", 3: "B", 2: "C", 1: "D", 0: "F"}
        letter_grade = grade_map.get(grade_points, "F")

        return {
            "game": name,
            "numbers": numbers,
            "grade": letter_grade,
            "score": grade_points,
            "max_score": max_points,
            "metrics": {
                "sum": total_sum,
                "sum_classification": sum_class,
                "z_score": round(z_score, 3),
                "sum_range": [lo_sum, hi_sum],
                "odd_count": odd_count,
                "even_count": even_count,
                "parity_ratio": round(parity_ratio, 3),
                "root_sum": root_sum,
                "decades": decades,
                "decade_spread": decade_spread,
                "consecutive_pairs": consecutive_pairs,
                "spread": spread,
            },
            "notes": notes
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/games/{name:path}", response_model=GameRulesSchema)
async def get_game_rules(name: str):
    try:
        adapter = get_adapter(name)
        rules = adapter.rules
        return GameRulesSchema(
            name=rules.name,
            pick_count=rules.pick_count,
            number_range=[rules.number_range[0], rules.number_range[1]],
            bonus_count=rules.bonus_count,
            bonus_range=[rules.bonus_range[0], rules.bonus_range[1]] if rules.bonus_range else None,
            prize_tiers=rules.prize_tiers,
            ticket_price=rules.ticket_price,
            currency=rules.currency
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


