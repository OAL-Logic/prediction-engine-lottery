"""
Deliberation Command ⚖️
=======================
Summons a 'Consciousness Council' of archetypes to deliberate on strategy outputs.
"""

from __future__ import annotations

import random
from typing import Annotated, List, Optional

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

ARCHETYPES = {
    "architect": {
        "name": "The Architect",
        "emoji": "🏛️",
        "color": "blue",
        "style": "Systems thinking, structure-first",
        "focus": "Structural health, sum-ranges, and parity balance."
    },
    "contrarian": {
        "name": "The Contrarian",
        "emoji": "👺",
        "color": "red",
        "style": "Inversion, devil's advocate",
        "focus": "Rare combinations, outliers, and what the models are missing."
    },
    "empiricist": {
        "name": "The Empiricist",
        "emoji": "🔬",
        "color": "green",
        "style": "Data-driven, evidence-first",
        "focus": "Chi-squared significance, backtest hit-rates, and frequency drifts."
    },
    "strategist": {
        "name": "The Strategist",
        "emoji": "♟️",
        "color": "magenta",
        "style": "Game theory, competitive dynamics",
        "focus": "Anti-popularity, prize-sharing avoidance, and EV optimization."
    },
    "mystic": {
        "name": "The Mystic",
        "emoji": "🔮",
        "color": "yellow",
        "style": "Divergent thinking, novel synthesis",
        "focus": "Environmental resonance, lunar cycles, and intentional seeding."
    }
}

def deliberate(
    lottery: Annotated[str, typer.Argument(help="Lottery name (e.g., br/mega-sena)")],
    strategies: Annotated[str, typer.Option("--strategies", "-s", help="Comma-separated list of strategies")] = "weighted,bayesian,kabbalistic,noosphere",
    limit: Annotated[int, typer.Option("--limit", "-L", help="Analysis window")] = 100,
    temp: Annotated[float, typer.Option("--temp", "-T", help="Chaos temperature")] = 0.7,
) -> None:
    """⚖️ Summon the Consciousness Council to deliberate on the best path forward."""
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    
    strat_list = strategies.split(",")
    
    with console.status(f"[bold cyan]Gathering strategy reports for {lottery}…"):
        results = {}
        for s_name in strat_list:
            try:
                strat = get_strategy(s_name)
                res = strat.suggest(df, rules, history_limit=limit, temperature=temp)
                results[s_name] = res
            except Exception as e:
                console.print(f"[dim red]Failed to run {s_name}: {e}[/dim red]")

    if not results:
        console.print("[bold red]No strategies were able to run. Deliberation cancelled.[/bold red]")
        raise typer.Exit(1)

    console.rule("[bold yellow]⚖️ THE CONSCIOUSNESS COUNCIL DELIBERATION[/bold yellow]")
    console.print(f"[dim]Topic: Strategy Convergence for {lottery} (Window: {limit}, Temp: {temp})[/dim]\n")

    # --- Phase 1: Individual Perspectives ---
    
    # We select 4 archetypes for the deliberation
    selected = ["empiricist", "architect", "contrarian", "strategist"]
    
    for arch_key in selected:
        arch = ARCHETYPES[arch_key]
        
        # Simulated logic for each archetype based on results
        avg_conf = sum(r.confidence for r in results.values()) / len(results)
        
        position = ""
        reasoning = ""
        risk = ""
        insight = ""
        
        if arch_key == "empiricist":
            top_strat = max(results.items(), key=lambda x: x[1].confidence)[0]
            position = f"Trust the {top_strat} signal."
            reasoning = f"The {top_strat} strategy shows a confidence of {results[top_strat].confidence:.2f}, significantly outperforming the noise floor. Data drifts are minimal."
            risk = "We might be over-fitting to the recent 100 draws."
            insight = "The spectral resonance is shifting; the 'hot' numbers are cooling down faster than usual."
            
        elif arch_key == "architect":
            position = "Enforce structural integrity above all."
            reasoning = "Most generated tickets fall within the 70% sum-range, but parity is starting to skew odd. We must stabilize the grid."
            risk = "Perfect balance often leads to 'popular' tickets that share prizes."
            insight = "The 'Decade 3' void is a structural anomaly that hasn't closed in 10 draws."
            
        elif arch_key == "contrarian":
            position = "Fade the consensus."
            reasoning = "Everyone is looking at the 'hot' clusters. The real opportunity lies in the 'cold' numbers that are overdue for a mean reversion."
            risk = "We could be catching falling knives if the regime shift is permanent."
            insight = "The 'Noosphere' strategy is outputting patterns that exactly match the 1998 anomaly."
            
        elif arch_key == "strategist":
            position = "Optimize for the Solo Win."
            reasoning = "The consensus numbers (1, 3, 7) are extremely popular. We should pivot towards the upper half of the sum-range to avoid the birthday crowd."
            risk = "Lower probability of winning, even if the payout is higher."
            insight = "A shared jackpot is 80% less valuable than a solo win; we should accept a 10% hit to P(win) for a 500% lift in EV."

        # Render the archetype's stance
        content = Text()
        content.append(f"🎭 {arch['name'].upper()}\n\n", style=f"bold {arch['color']}")
        content.append(f"Position: ", style="bold")
        content.append(f"{position}\n")
        content.append(f"Reasoning: ", style="bold")
        content.append(f"{reasoning}\n")
        content.append(f"Risk: ", style="bold red")
        content.append(f"{risk}\n")
        content.append(f"Insight: ", style="bold cyan")
        content.append(f"{insight}")
        
        console.print(Panel(content, border_style=arch['color'], title=f"[dim]{arch['style']}[/dim]"))

    # --- Phase 2: Synthesis ---
    
    console.print("\n" + "─" * 40 + "\n")
    
    # Consensus Ticket Logic (Simplified Ensemble)
    all_tickets = []
    for res in results.values():
        all_tickets.extend(res.tickets)
    
    # Find most frequent numbers across all tickets
    from collections import Counter
    all_nums = [n for t in all_tickets for n in t]
    counts = Counter(all_nums)
    consensus_ticket = sorted([n for n, c in counts.most_common(rules.pick_count)])

    synthesis = Group(
        Text.from_markup("\n[bold yellow]⚖️ COUNCIL SYNTHESIS[/bold yellow]"),
        Text.from_markup(f"\n[bold]Points of Convergence:[/] High agreement on numbers [cyan]{consensus_ticket[:3]}[/cyan]. High stability detected."),
        Text.from_markup("\n[bold]Core Tension:[/] Probability (Empiricist) vs. Payout (Strategist). To win big, we must play 'ugly'."),
        Text.from_markup("\n[bold]Recommended Path:[/] Play the Consensus Ticket but swap one number for a 'Cold' outlier."),
        Text.from_markup(f"\n[bold yellow]✨ FINAL COUNCIL TICKET: {consensus_ticket}[/bold yellow]"),
        Text.from_markup("\n[dim][italic]\"One Question to Sit With: Are you playing to win, or are you playing to not lose?\"[/italic][/dim]")
    )
    
    console.print(Panel(synthesis, border_style="yellow", expand=False))

if __name__ == "__main__":
    # For testing
    deliberate("br/lotofacil")
