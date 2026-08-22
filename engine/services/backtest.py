"""
Backtest Service 🔬
===================
Evaluates one or more strategies against one or more historical draws.

Framework-agnostic: no Rich, no FastAPI/Pydantic. The CLI renders this to
the terminal (engine/cli/commands/backtest.py); the API serializes it to
JSON (engine/api/main.py). Both call `run_backtest()` and get the same
`BacktestResult` back.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import pandas as pd

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy, list_strategies


class UnknownStrategyError(ValueError):
    """Raised when a requested strategy name isn't registered."""


@dataclass
class StrategyDrawResult:
    hits: list[int]
    avg_rank: float
    top_n: int


@dataclass
class DrawResult:
    draw_id: int
    date: str | None
    winning_numbers: list[int]
    strategies: dict[str, StrategyDrawResult] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    attempted_strategies: list[str] = field(default_factory=list)


@dataclass
class StrategySummary:
    avg_rank: float
    top_n_capture: int
    capture_pct: float
    best_hit: int
    win_rate_pct: float


@dataclass
class BacktestResult:
    lottery: str
    game_name: str
    strategy_names: list[str]
    draws: list[DrawResult] = field(default_factory=list)
    summary: dict[str, StrategySummary] = field(default_factory=dict)


def _resolve_strategy_names(strategy_names: list[str] | None) -> list[str]:
    if not strategy_names:
        return ["weighted"]
    if len(strategy_names) == 1 and strategy_names[0].lower() == "all":
        return [s["name"] for s in list_strategies()]
    return strategy_names


def _resolve_target_rows(df: pd.DataFrame, draw_id: str | None, prev: str | None) -> list[pd.Series]:
    target_rows: list[pd.Series] = []

    if prev is not None:
        indices: list[int] = []
        for part in prev.split(","):
            if ".." in part:
                start, end = part.split("..")
                indices.extend(range(int(start), int(end) + 1))
            elif "-" in part:
                start, end = part.split("-")
                indices.extend(range(int(start), int(end) + 1))
            else:
                indices.append(int(part))
        for idx in indices:
            try:
                target_rows.append(df.iloc[-idx])
            except IndexError:
                continue

    elif draw_id is not None:
        ids_to_fetch: list[Any] = []
        for part in draw_id.split(","):
            if ".." in part:
                start, end = part.split("..")
                ids_to_fetch.extend(range(int(start), int(end) + 1))
            elif "-" in part and not part.startswith("-"):
                start, end = part.split("-")
                ids_to_fetch.extend(range(int(start), int(end) + 1))
            else:
                ids_to_fetch.append(part)
        for val in ids_to_fetch:
            try:
                tid = int(val)
                matches = df[df["draw_id"] == tid]
                if not matches.empty:
                    target_rows.append(matches.iloc[0])
            except ValueError:
                matches = df[df["date"].astype(str).str.contains(str(val))]
                if not matches.empty:
                    target_rows.append(matches.iloc[0])
    else:
        raise ValueError("Provide either draw_id or prev.")

    target_rows.sort(key=lambda r: int(r["draw_id"]))
    return target_rows


def _strategy_kwargs_for(name: str, base: dict[str, Any] | None, draw_date: Any) -> dict[str, Any]:
    kwargs = dict(base or {})
    if name in ("weather", "moon_phase"):
        kwargs["upcoming_draw_date"] = draw_date
    elif name == "numerology":
        kwargs["target_date"] = draw_date
    elif name in ("biorhythm", "zodiac"):
        kwargs["draw_date"] = draw_date
    return kwargs


def _summarize(
    strategy_names: list[str],
    draws: list[DrawResult],
    pick_count: int,
    odds: dict,
) -> dict[str, StrategySummary]:
    min_win = min(odds.keys()) if odds else pick_count - 1
    summary: dict[str, StrategySummary] = {}

    for name in strategy_names:
        all_ranks: list[float] = []
        total_top_n = 0
        best_hit = 0
        wins = 0
        total_tickets = 0

        for draw in draws:
            data = draw.strategies.get(name)
            if data is None:
                continue
            all_ranks.append(data.avg_rank)
            total_top_n += data.top_n
            best_hit = max(best_hit, max(data.hits) if data.hits else 0)
            wins += sum(1 for h in data.hits if h >= min_win)
            total_tickets += len(data.hits)

        if not all_ranks:
            continue

        summary[name] = StrategySummary(
            avg_rank=sum(all_ranks) / len(all_ranks),
            top_n_capture=total_top_n,
            capture_pct=(total_top_n / (len(all_ranks) * pick_count)) * 100,
            best_hit=best_hit,
            win_rate_pct=(wins / total_tickets * 100) if total_tickets > 0 else 0.0,
        )

    return summary


def run_backtest(
    lottery: str,
    draw_id: str | None = None,
    prev: str | None = None,
    strategy_names: list[str] | None = None,
    strategy_kwargs: dict[str, dict[str, Any]] | None = None,
    count: int = 1,
    temperature: float = 0.0,
    limit: int | None = None,
    on_draw: Callable[[DrawResult], None] | None = None,
) -> BacktestResult:
    """
    Evaluate `strategy_names` against the historical draw(s) selected by
    `draw_id` and/or `prev` (same string formats as the CLI/API accept:
    single id, comma list, or `start-end`/`start..end` range).

    "Blind" testing: each strategy only sees draws before the one being
    tested. `on_draw` fires once per evaluated draw, in draw_id order, so a
    caller can render progress without waiting for the full result.
    """
    if draw_id is None and prev is None:
        raise ValueError("Provide either draw_id or prev.")

    names = _resolve_strategy_names(strategy_names)
    for name in names:
        try:
            get_strategy(name)
        except KeyError as exc:
            raise UnknownStrategyError(f"Unknown strategy '{name}'.") from exc

    adapter = get_adapter(lottery)
    df = adapter.fetch()

    target_rows = _resolve_target_rows(df, draw_id, prev)
    if not target_rows:
        raise ValueError("No draws found to test.")

    draws: list[DrawResult] = []

    for target_row in target_rows:
        t_id = int(target_row["draw_id"])
        t_date = target_row["date"]
        if pd.isna(t_date):
            t_date = None
        elif hasattr(t_date, "date"):
            t_date = t_date.date()

        train_df = df[df["draw_id"] < t_id].copy()
        if train_df.empty:
            continue

        winning_numbers = sorted(int(n) for n in target_row["numbers"])
        draw_result = DrawResult(
            draw_id=t_id,
            date=str(t_date) if t_date is not None else None,
            winning_numbers=winning_numbers,
        )

        for name in names:
            draw_result.attempted_strategies.append(name)
            kwargs = _strategy_kwargs_for(name, (strategy_kwargs or {}).get(name), t_date)
            try:
                strat_obj = get_strategy(name, **kwargs)
                result = strat_obj.suggest(
                    train_df,
                    adapter.rules,
                    count=count,
                    temperature=temperature,
                    history_limit=limit,
                )
            except Exception as exc:
                draw_result.errors[name] = str(exc)
                continue

            hits = [len(set(ticket) & set(winning_numbers)) for ticket in result.tickets]
            sorted_scores = sorted(result.scores.items(), key=lambda x: x[1], reverse=True)
            ranks = {num: rank + 1 for rank, (num, _score) in enumerate(sorted_scores)}
            top_n = sum(1 for n in winning_numbers if ranks.get(n, 999) <= adapter.rules.pick_count)
            avg_rank = sum(ranks.get(n, 0) for n in winning_numbers) / len(winning_numbers)

            draw_result.strategies[name] = StrategyDrawResult(hits=hits, avg_rank=avg_rank, top_n=top_n)

        draws.append(draw_result)
        if on_draw is not None:
            on_draw(draw_result)

    summary = _summarize(names, draws, adapter.rules.pick_count, adapter.rules.odds)

    return BacktestResult(
        lottery=lottery,
        game_name=adapter.rules.name,
        strategy_names=names,
        draws=draws,
        summary=summary,
    )
