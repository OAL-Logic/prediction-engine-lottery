"""
Personal Commands 🧘
====================
Kabbalistic and numerological personal utilities.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from engine.strategies.fun.kabbalistic import KabbalisticStrategy

console = Console()

def calendar(
    full_name: Annotated[str, typer.Option("--full-name", help="Full birth name for Kabbalistic numerology")] = "GEMINI ENGINE",
    birth_date: Annotated[str, typer.Option("--birth-date", help="Birthday (YYYY-MM-DD)")] = "1990-01-01",
    month: Annotated[Optional[int], typer.Option("--month", "-m", help="Month (1-12) to generate calendar for")] = None,
    year: Annotated[Optional[int], typer.Option("--year", "-y", help="Year (e.g. 2026)")] = None,
) -> None:
    """📅 Generate a personal Kabbalistic calendar of Favorable Days."""
    import calendar as py_calendar
    
    today = date.today()
    c_month = month or today.month
    c_year = year or today.year

    strat = KabbalisticStrategy(full_name=full_name, birth_date=birth_date)
    destiny = strat.destiny

    cal = py_calendar.monthcalendar(c_year, c_month)
    month_name = py_calendar.month_name[c_month]

    console.print(f"\n  [bold cyan]Personal Kabbalistic Calendar: {month_name} {c_year}[/bold cyan]")
    console.print(f"  [dim]Name: {full_name} | Birthday: {birth_date}[/dim]\n")

    header = " Mo Tu We Th Fr Sa Su"
    console.print(f"  [bold]{header}[/bold]")

    for week in cal:
        row_str = " "
        for day in week:
            if day == 0:
                row_str += "   "
            else:
                d_obj = date(c_year, c_month, day)
                vib = strat._get_vibrations(d_obj)
                pd = vib["day"]
                color = "white"
                if d_obj.day == strat.birth_date.day: color = "bold gold1"
                elif pd in (1, 8): color = "bold yellow"
                elif pd == destiny: color = "bold green"
                elif pd in (7, 9): color = "dim"
                row_str += f"[{color}]{day:2}[/{color}] "
        console.print(row_str)

    current_vib = strat._get_vibrations(date(c_year, c_month, 1))
    py = current_vib["year"]
    console.print(f"\n  [bold cyan]Current Personal Year:[/bold cyan] [bold yellow]{py}[/bold yellow]")


def signature(
    name: Annotated[str, typer.Argument(help="Full birth name to analyze")],
) -> None:
    """✍️ Analyze Name for Negative Sequences (for entertainment)."""
    strat = KabbalisticStrategy(full_name=name)
    neg = strat.negative_sequences
    
    console.print(f"\n  [bold cyan]Kabbalistic Signature Analysis[/bold cyan]")
    console.print(f"  [dim]Original Name: {name}[/dim]\n")
    
    if not neg:
        console.print(f"  [green]✓ Clean Signature:[/green] No negative sequences detected.")
    else:
        # Kabbalistic meanings for repeated digit sequences
        MEANINGS = {
            1: "Mental Fatigue / Limitations",
            2: "Indecision / Emotional Flux",
            3: "Communication Blockage",
            4: "Hard Work / Low Return",
            5: "Instability / Chaos",
            6: "Material Attachment",
            7: "Overthinking / Isolation",
            8: "Financial Pressure",
            9: "Unfinished Business"
        }
        console.print(f"  [red]⚠ Sequence Alerts:[/red] {len(neg)} blockages found.")
        for val in sorted(list(neg)):
            meaning = MEANINGS.get(val, "Energy Blockage")
            console.print(f"    - [yellow]{val}{val}{val}[/yellow]: {meaning}")

    core = strat.core
    console.print(f"\n  Core Vibrations:")
    console.print(f"  Motivation: {core['motivation']} | Impression: {core['impression']} | Expression: {core['expression']}")
