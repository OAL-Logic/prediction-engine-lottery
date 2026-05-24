from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import pandas as pd
from datetime import date

from engine.api.models import (
    GameRulesSchema, GameSummary, AnalysisResultSchema,
    SuggestionRequest, SuggestionResponse, BacktestRequest, CheckRequest,
    OddsResponse, OddsTier, PruningResponse, PruningMetricsSchema,
    CalibrateRequest, TuneRequest
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
    version="0.1.0"
)

# STORY 3.1: Middleware to enforce propagated deadlines
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

@app.get("/games/{name}", response_model=GameRulesSchema)
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

@app.post("/games/{name}/fetch")
async def fetch_game_data(name: str, background_tasks: BackgroundTasks):
    try:
        adapter = get_adapter(name)
        # Run fetch in background as it might be slow
        background_tasks.add_task(adapter.fetch_data)
        return {"message": f"Fetch started for {name}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/games/{name}/analysis", response_model=AnalysisResultSchema)
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

@app.post("/games/{name}/suggest", response_model=SuggestionResponse)
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

@app.post("/games/{name}/backtest")
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

@app.post("/games/{name}/check")
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

@app.get("/games/{name}/odds", response_model=OddsResponse)
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

@app.post("/games/{name}/prune", response_model=PruningResponse)
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

@app.post("/games/{name}/calibrate")
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

@app.post("/games/{name}/tune")
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
