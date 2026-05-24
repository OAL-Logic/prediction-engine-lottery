"""
Wizard Command 🧙
=================
Interactive wizard to guide you through lottery analysis and prediction.
"""

from __future__ import annotations

import inspect
from datetime import date, timedelta
from typing import Annotated, Optional, Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt

from engine.cli.utils import select_lottery_ui, get_adapter, print_command_summary, geocode
from engine.adapters.registry import registry

console = Console()

def wizard() -> None:
    """🧙 Interactive wizard to guide you through lottery analysis and prediction."""
    rprint(Panel.fit(
        "[bold cyan]Lottery Engine Wizard[/bold cyan]\n"
        "Follow the steps to guide your next move.",
        border_style="cyan"
    ))

    # 0. Select Mode
    mode = Prompt.ask(
        "[bold]0. What do you want to do?[/bold]",
        choices=["suggest", "wheel", "backtest"],
        default="suggest"
    )

    if mode == "wheel":
        # --- Wheeling Flow ---
        from engine.cli.commands.management import wheel
        lottery = select_lottery_ui(console, "Select a lottery for wheeling")
        adapter = get_adapter(lottery)
        pick_count = adapter.rules.pick_count

        pool_str = Prompt.ask(
            "[bold]2. Number Pool[/bold]\n"
            f"   [dim](Select {pick_count}-20 numbers you want to cover, space-separated)[/dim]",
            default=" ".join(str(n) for n in range(1, pick_count * 3))
        )
        
        guarantee = IntPrompt.ask(
            "[bold]3. Prize Guarantee[/bold]\n"
            f"   [dim](e.g. {pick_count-1} for 'Hit {pick_count-1} if all winning numbers are in your pool')[/dim]",
            default=pick_count-1
        )
        
        print_command_summary("wheel", lottery, pool=pool_str, guarantee=guarantee)
        
        wheel(
            lottery=lottery,
            pool=pool_str,
            mode="abbreviated",
            guarantee=guarantee
        )
        return

    if mode == "backtest":
        # --- Backtest Flow ---
        from engine.cli.commands.backtest import backtest
        rprint("\n[bold cyan]🔬 Historical Backtest Mode[/bold cyan]")
        rprint("   This mode evaluates strategies against past winning numbers.")
        rprint("   It performs 'blind' testing: strategies only see draws that")
        rprint("   happened BEFORE the target draw, simulating a real-world bet.\n")
        
        lottery = select_lottery_ui(console, "Select a lottery for backtesting")
        
        draw_input = Prompt.ask(
            "[bold]2. Target Draws[/bold]\n"
            "   [dim](e.g. '2990', '2990-2999', or use '@1' for latest, '@1-5' for last 5)[/dim]",
            default="@1-3"
        )
        
        prev_val = None
        draw_id_val = None
        if draw_input.startswith("@"):
            prev_val = draw_input[1:]
        else:
            draw_id_val = draw_input

        strategy = Prompt.ask(
            "[bold]3. Select strategies[/bold]\n"
            "   [dim](e.g. 'weighted', 'markov,bayesian', or 'all')[/dim]",
            default="weighted"
        )
        
        limit = IntPrompt.ask("[bold]4. History Limit[/bold] (Recency bias: draws to look at)", default=100)
        temp = FloatPrompt.ask("[bold]5. Sampling temperature[/bold] (0=top picks, 1=balanced)", default=0.0)

        print_command_summary("backtest", lottery, strategy=strategy, temp=temp, limit=limit)
        
        backtest(
            lottery=lottery,
            draw_id=draw_id_val,
            prev=prev_val,
            strategy=strategy,
            temperature=temp,
            limit=limit,
            summary=True
        )
        return

    # --- Suggest Flow ---
    from engine.cli.commands.suggest import _run_comparison
    from engine.strategies import STRATEGY_PRESETS
    lottery = select_lottery_ui(console, "Select a lottery for suggestions")

    adapter = get_adapter(lottery)
    rules = adapter.rules
    pick = rules.pick_count
    
    # 1.5 Global Settings (Hoist)
    global_draw_date = None
    draw_date_str = Prompt.ask(
        "[bold]1.5 Global Draw Date[/bold]\n"
        "    [dim](Affects date-dependent strategies like Moon Phase, Zodiac. YYYY-MM-DD or 'none')[/dim]", 
        default="none"
    )
    if draw_date_str.lower() != "none":
        try:
            global_draw_date = date.fromisoformat(draw_date_str[:10])
        except ValueError:
            rprint("[yellow]⚠ Invalid date format. Using 'none'.[/yellow]")

    if len(rules.allowed_picks) > 1:
        use_multiple = Prompt.ask(
            f"[bold]1.6 Do you want to play a Multiple Bet?[/bold]\n"
            f"   [dim](e.g. play more than {rules.pick_count} numbers in one ticket)[/dim]",
            choices=["yes", "no"],
            default="no"
        )
        if use_multiple == "yes":
            choices = [str(p) for p in rules.allowed_picks]
            pick_str = Prompt.ask(
                f"    How many balls to pick?",
                choices=choices,
                default=str(rules.pick_count + 1)
            )
            pick = int(pick_str)
            cost = rules.calculate_bet_cost(pick)
            rprint(f"    [yellow]Note: Playing {pick} numbers costs {cost:.2f} {rules.currency} per ticket.[/yellow]")

    group_input = Prompt.ask(
        "[bold]2. Select strategy group or enter comma-separated strategies[/bold]\n"
        "   [dim](Groups: statistical, chaos, fun, ml, deep, all, custom)[/dim]",
        default="statistical"
    )

    strategy_names = []
    # Smart detection: if input contains commas or is not a known preset, assume custom
    if "," in group_input or group_input not in ["statistical", "chaos", "fun", "ml", "deep", "all", "custom"]:
        strategy_names = [s.strip() for s in group_input.split(",") if s.strip()]
    elif group_input == "custom":
        from engine.strategies import list_strategies
        available = sorted([s["name"] for s in list_strategies()])
        rprint(f"  [dim]Available: {', '.join(available)}[/dim]")
        strategy_input = Prompt.ask("   Enter strategy name(s) (comma-separated)", default="weighted")
        strategy_names = [s.strip() for s in strategy_input.split(",") if s.strip()]
    elif group_input in STRATEGY_PRESETS:
        strategy_names = STRATEGY_PRESETS[group_input]

    # --- Strategy Customization ---
    from engine.strategies import get_strategy, STRATEGY_REGISTRY

    strat_objects = []
    strat_configs = []

    for name in strategy_names:
        try:
            if name not in STRATEGY_REGISTRY:
                rprint(f"  [red]⚠ Strategy '{name}' not found — skipping.[/red]")
                continue
                
            # Trigger lazy load to get the class
            strat_obj_template = get_strategy(name)
            strat_cls = strat_obj_template.__class__

            # Reflect on __init__
            sig = inspect.signature(strat_cls.__init__)
            # EXCLUDE *args and **kwargs from prompts (Task 2.2)
            params = [
                p for p in sig.parameters.values() 
                if p.name != "self" and p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            ]

            if not params:
                strat_objects.append(get_strategy(name))
                strat_configs.append({})
                continue

            rprint(f"\n[cyan]Settings for [bold]{name}[/bold]:[/cyan]")

            # Extract docstrings for help hints
            doc = strat_cls.__init__.__doc__ or ""
            param_docs = {}
            if doc:
                import re
                matches = re.findall(r"^ +(\w+)\s*\n\s+([^\n]+(?:(?!\n\s*\w+\s*\n)\n\s+[^\n]+)*)", doc, re.MULTILINE)
                for p_name, p_desc in matches:
                    param_docs[p_name] = " ".join(p_desc.split())

            customize = Prompt.ask(f"   Customize parameters for {name}?", choices=["yes", "no"], default="no")

            if customize == "no":
                strat_objects.append(get_strategy(name))
                strat_configs.append({})
            else:
                kwargs = {}
                # (Task 2.4) Smart Geolocation Defaults
                if name in ("weather", "ley_lines", "seismic", "refraction"):
                    default_loc = "Sao Paulo, Brazil" if "br/" in lottery else "New York, USA" if "us/" in lottery else "London, UK"
                    location = Prompt.ask(f"     [dim]Location search for {name}[/dim]", default=default_loc)
                    coords = geocode(location)
                    if coords:
                        kwargs["latitude"], kwargs["longitude"] = coords
                
                for p in params:
                    if p.name in kwargs: continue
                    
                    # (Task 2.1) Hoist Global Variables: skip prompting for dates if globally set
                    if "date" in p.name.lower() and global_draw_date is not None:
                        kwargs[p.name] = global_draw_date
                        continue
                        
                    default_val = p.default if p.default is not inspect.Parameter.empty else None
                    
                    label = p.name
                    hint = " [dim](YYYY-MM-DD)[/dim]" if "date" in p.name.lower() else ""
                    if p.name in param_docs:
                        console.print(f"     [italic dim]{param_docs[p.name]}[/italic dim]")

                    val = Prompt.ask(f"     {label}{hint}", default=str(default_val) if default_val is not None else None)
                    if val is None or val == "None" or (isinstance(val, str) and val.strip() == ""):
                        kwargs[p.name] = default_val
                        continue

                    # Handle Date conversion
                    if "date" in p.name.lower():
                        try:
                            from datetime import datetime
                            kwargs[p.name] = datetime.strptime(val, "%Y-%m-%d").date()
                            continue
                        except Exception:
                            kwargs[p.name] = default_val
                            continue

                    # Basic type conversion
                    target_type = p.annotation
                    if target_type is inspect.Parameter.empty and default_val is not None:
                        target_type = type(default_val)

                    try:
                        if target_type in [float, Optional[float]]: kwargs[p.name] = float(val)
                        elif target_type in [int, Optional[int]]: kwargs[p.name] = int(val)
                        elif target_type in [bool, Optional[bool]]: kwargs[p.name] = val.lower() in ["true", "yes", "1", "y", "t"]
                        else: kwargs[p.name] = val
                    except Exception:
                        kwargs[p.name] = val

                strat_objects.append(get_strategy(name, **kwargs))
                strat_configs.append({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in kwargs.items()})
                
        except Exception as exc:
            # (Task 1.1) Fixed Exception Loop
            rprint(f"  [red]⚠ Initialization failed for '{name}': {exc} — skipping.[/red]")
            continue

    # 3. Settings
    count = IntPrompt.ask("[bold]3. Number of tickets per strategy[/bold]", default=1)
    temp = FloatPrompt.ask("[bold]4. Sampling temperature[/bold] (0=top picks, 1=balanced)", default=1.0)
    limit_str = Prompt.ask("[bold]5. History Limit[/bold] (Recency bias: draws to look at, or 'none')", default="100")

    final_limit = int(limit_str) if limit_str.lower() != "none" else None
    
    # Ensure global date is passed to all strategies even if not customized
    if global_draw_date:
        for strat in strat_objects:
            if hasattr(strat, "upcoming_draw_date"): strat.upcoming_draw_date = global_draw_date
            if hasattr(strat, "target_date"): strat.target_date = global_draw_date
            if hasattr(strat, "draw_date"): strat.draw_date = global_draw_date

    rprint(f"\n[bold green]🚀 Launching customized analysis for {lottery}...[/bold green]\n")

    _run_comparison(
        lottery=lottery,
        strategies=",".join([s.name for s in strat_objects]),
        count=count,
        temperature=temp,
        limit=final_limit,
        learn=True,
        strategy_objects=strat_objects,
        strategy_configs=strat_configs,
        pick=pick
    )
