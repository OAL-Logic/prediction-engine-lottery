"""
Pro Wizard Command 🧙‍♂️
=====================
Enhanced interactive wizard for expert-level session configuration.
Allows fine-tuning strategy parameters and multi-stage diagnostics.
"""

from __future__ import annotations

from typing import Annotated, Optional
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table

from engine.adapters.registry import registry
from engine.cli.utils import get_adapter

console = Console()

def wizard_pro() -> None:
    """🧙‍♂️ Expert Decision Support Wizard.

    Provides a structured, interactive path to configure a prediction session.
    Choose your analytical personality, fine-tune models, and validate 
    structural constraints in real-time.
    """
    console.rule("[bold yellow]🧙‍♂️ PREDICTION ENGINE — PRO WIZARD[/bold yellow]")
    
    # 1. Select Lottery
    games = [g.id for g in registry.list_games() if g.data_available]
    lottery = Prompt.ask("Select Lottery", choices=games, default="br/lotofacil")
    
    adapter = get_adapter(lottery)
    rules = adapter.rules
    
    console.print(f"\n[bold cyan]Target:[/] {rules.name} ({rules.pick_count}/{rules.pool_size})")
    
    # 2. Select Analysis Personality
    personalities = {
        "1": ("CONSERVATIVE", "Focuses on high-probability historical anchors and parity balance."),
        "2": ("BALANCED", "A blend of statistical inertia and moderate chaos signals."),
        "3": ("AGGRESSIVE", "Targets high-EV outliers and extreme value breakouts."),
        "4": ("EXPERIMENTAL", "Uses the latest 'Horizon' models (Quantum, TDA, Swarm).")
    }
    
    table = Table(box=None, header_style="bold magenta")
    table.add_column("Option")
    table.add_column("Personality")
    table.add_column("Description")
    for k, v in personalities.items():
        table.add_row(k, v[0], v[1])
    console.print(table)
    
    choice = Prompt.ask("Choose your Analysis Personality", choices=list(personalities.keys()), default="2")
    personality_name = personalities[choice][0]
    
    # 3. Fine-tune Parameters
    console.print(f"\n[bold yellow]--- Fine-tuning {personality_name} Parameters ---[/bold yellow]")
    
    temp = FloatPrompt.ask("Chaos Temperature (0.0=Static, 1.0=Standard, 2.0=Wild)", default=1.0)
    limit = IntPrompt.ask("Analysis Window (Number of historical draws)", default=100)
    count = IntPrompt.ask("Number of tickets to generate", default=3)
    
    # 4. Strategy Selection based on personality
    if choice == "1":
        strategies = "weighted,markov,positional"
    elif choice == "2":
        strategies = "bayesian,pattern,hurst_memory"
    elif choice == "3":
        strategies = "evt_extremes,game_theory,contagion"
    else:
        strategies = "zeno_quantum,tda_topology,ising_model"
        
    console.print(f"\n[bold green]Configuration Complete![/bold green]")
    config_summary = (
        f"Lottery: [cyan]{lottery}[/cyan]\n"
        f"Personality: [magenta]{personality_name}[/magenta]\n"
        f"Strategies: [white]{strategies}[/white]\n"
        f"Temp: {temp}  ·  Window: {limit}  ·  Count: {count}"
    )
    console.print(Panel(config_summary, title="Session Plan", border_style="green"))
    
    if Confirm.ask("Execute Session now?"):
        # We invoke the 'forecast' logic here
        # For simplicity in this iteration, we'll just print the command to run
        cmd = f"./lottery forecast {lottery} --strategies {strategies} --temp {temp} --limit {limit}"
        console.print(f"\n[bold yellow]Executing:[/] [dim]{cmd}[/dim]\n")
        
        from engine.cli.commands.forecast import forecast as impl
        impl(lottery, strategies=strategies, temperature=temp, window=limit)
        
    console.print("\n[dim]Wizard finished. The probability field has been collapsed.[/dim]")

if __name__ == "__main__":
    wizard_pro()
