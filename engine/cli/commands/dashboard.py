"""
Dashboard Command 📈
===================
High-fidelity Terminal Dashboard with real-time multi-panel analysis.
Supports composable views, cycle intelligence, and flexible layouts.
"""

from __future__ import annotations

from typing import Annotated, Optional, Dict, Any, List, Callable
from collections import Counter
import typer
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.columns import Columns
from rich.text import Text

from engine.cli.utils import get_adapter, bar_chart
from engine.modules import frequency, deviation, sum_range, insights as insight_mod
from engine.modules.patterns import (
    analyze_cycle, analyze_voids, get_pattern_string,
    get_primes_in_set, get_fibonacci_in_set, get_magic_in_set, 
    get_multiples_3_in_set, get_repeated_count, get_frame_center_logic
)
from engine.modules.tendency import analyze_pattern_tendency, TendencyResult, PatternQtyStats
from engine.modules import filters as f_mod

console = Console()

# --- Pattern Definitions ---

def get_segment_count(nums: List[int], start: int, end: int) -> int:
    return len([n for n in nums if start <= n <= end])

PATTERN_CONFIG: Dict[str, Dict[str, Any]] = {
    "primes": {"name": "Primes", "func": lambda nums, prev: len(get_primes_in_set(nums))},
    "fibonacci": {"name": "Fibonacci", "func": lambda nums, prev: len(get_fibonacci_in_set(nums))},
    "magic": {"name": "Magic Numbers", "func": lambda nums, prev: len(get_magic_in_set(nums))},
    "multiples_3": {"name": "Multiples of 3", "func": lambda nums, prev: len(get_multiples_3_in_set(nums))},
    "repeated": {"name": "Repeated Numbers", "func": lambda nums, prev: get_repeated_count(nums, prev) if prev is not None else 0},
    "odd": {"name": "Odd Numbers", "func": lambda nums, prev: len([n for n in nums if n % 2 != 0])},
    "even": {"name": "Even Numbers", "func": lambda nums, prev: len([n for n in nums if n % 2 == 0])},
    "frame": {"name": "Frame (Perimeter)", "func": lambda nums, prev: len(get_frame_center_logic(nums)["frame"])},
    "center": {"name": "Center", "func": lambda nums, prev: len(get_frame_center_logic(nums)["center"])},
    "c1": {"name": "Segment C1 (1-5)", "func": lambda nums, prev: get_segment_count(nums, 1, 5)},
    "c2": {"name": "Segment C2 (6-10)", "func": lambda nums, prev: get_segment_count(nums, 6, 10)},
    "c3": {"name": "Segment C3 (11-15)", "func": lambda nums, prev: get_segment_count(nums, 11, 15)},
    "c4": {"name": "Segment C4 (16-20)", "func": lambda nums, prev: get_segment_count(nums, 16, 20)},
    "c5": {"name": "Segment C5 (21-25)", "func": lambda nums, prev: get_segment_count(nums, 21, 25)},
}

def dashboard(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    limit:   Annotated[int, typer.Option("--limit", "-L", help="Analysis window (last N draws)")] = 100,
    view:    Annotated[Optional[str], typer.Option("--view", "-V", help="View: alerts | odd_even | primes | fibonacci | frame | multiples_3 | magic | repeated | complete")] = "alerts",
) -> None:
    """🖥️ High-fidelity Terminal Dashboard with real-time multi-panel analysis."""
    adapter = get_adapter(lottery)
    df_full = adapter.fetch()
    render_dashboard(df_full, adapter.rules, limit=limit, view=view)

def render_dashboard(df_full, rules, limit=100, view="alerts"):
    """Entry point for rendering the dashboard with view support."""
    df = df_full.tail(limit)
    
    if view == "alerts" or view is None:
        render_alerts_view(df_full, rules, limit)
    elif view == "complete" or view == "all":
        render_complete_view(df_full, rules, limit)
    elif view in PATTERN_CONFIG:
        render_single_pattern_view(df_full, rules, limit, view)
    elif view == "odd_even":
        # Special case for combined odd/even view
        render_combined_view(df_full, rules, limit, ["odd", "even"], "Odd & Even Analysis")
    elif view == "legacy" or view == "overview":
        render_legacy_dashboard(df_full, rules, limit)
    else:
        console.print(f"[bold red]Unknown view '{view}'.[/bold red] Showing alerts instead.")
        render_alerts_view(df_full, rules, limit)

# --- Renderers ---

def create_tendency_table(res: TendencyResult) -> Table:
    """Create a rich Table for a TendencyResult."""
    table = Table(title=f"{res.pattern_name} Tendency", box=None, header_style="bold cyan")
    table.add_column("QTY", justify="center")
    table.add_column("OCCURRENCE", justify="right")
    table.add_column("AVERAGE (%)", justify="right")
    table.add_column("AVG FREQ", justify="right")
    table.add_column("DELAY", justify="right")
    table.add_column("TREND (Last 20)", justify="center")

    for s in res.stats:
        # High delay alert (Atraso >= 1.5 * Average Frequency)
        is_alert = s.delay >= (s.avg_frequency * 1.5) and s.avg_frequency > 0
        row_style = "bold red" if is_alert else ""
        
        # Sparkline-like trend
        trend_str = "".join(["[green]█[/]" if v else "[dim].[/]" for v in s.trend])
        
        table.add_row(
            str(s.qty),
            str(s.occurrence),
            f"{s.average_pct:.1f}%",
            f"1 in {s.avg_frequency:.1f}",
            str(s.delay),
            trend_str,
            style=row_style
        )
    return table

def render_single_pattern_view(df_full, rules, limit, pattern_key):
    config = PATTERN_CONFIG[pattern_key]
    res = analyze_pattern_tendency(df_full, config["func"], config["name"])
    table = create_tendency_table(res)
    console.print(Panel(table, border_style="green", expand=False))

def render_combined_view(df_full, rules, limit, pattern_keys, title):
    tables = []
    for pk in pattern_keys:
        config = PATTERN_CONFIG[pk]
        res = analyze_pattern_tendency(df_full, config["func"], config["name"])
        tables.append(create_tendency_table(res))
    
    console.print(Panel(Columns(tables, equal=True), title=title, border_style="magenta"))

def render_alerts_view(df_full, rules, limit):
    insights = insight_mod.get_automated_insights(df_full, rules, limit=limit)
    if insights:
        console.print(Panel("\n".join(insights), title="Automated Insight Ribbon", border_style="cyan"))
        console.print()

    console.print(Rule("[bold red]Statistical Anomalies & Alerts[/bold red]"))
    all_alerts = []
    for pk, config in PATTERN_CONFIG.items():
        res = analyze_pattern_tendency(df_full, config["func"], config["name"])
        for s in res.stats:
            if s.delay >= (s.avg_frequency * 1.5) and s.avg_frequency > 0 and s.average_pct > 5:
                all_alerts.append({
                    "pattern": res.pattern_name,
                    "qty": s.qty,
                    "delay": s.delay,
                    "avg": s.avg_frequency,
                    "pct": s.average_pct
                })
    
    if not all_alerts:
        console.print("[green]No major statistical anomalies detected in current draw cycle.[/green]")
        return

    table = Table(box=None, header_style="bold yellow")
    table.add_column("Pattern")
    table.add_column("QTY", justify="center")
    table.add_column("Delay", justify="right")
    table.add_column("Avg Freq", justify="right")
    table.add_column("Probability", justify="right")
    
    for a in sorted(all_alerts, key=lambda x: x["delay"]/x["avg"], reverse=True):
        prob = min(99, int((a["delay"] / a["avg"]) * 50)) # Simplistic probability score
        table.add_row(
            a["pattern"],
            str(a["qty"]),
            f"[bold red]{a['delay']}[/]",
            f"1 in {a['avg']:.1f}",
            f"{prob}%"
        )
    
    console.print(table)
    console.print("\n[dim]Action: lottery suggest --filter-anomalies[/dim]")

def render_complete_view(df_full, rules, limit):
    """The 'Everything Everywhere' view with intelligent layout."""
    console.print(Rule(f"[bold gold1]Complete Pattern Intelligence — {rules.name}[/bold gold1]"))
    
    # 1. Summary Ribbon
    last_draw = df_full.iloc[-1]
    last_nums = last_draw["numbers"]
    
    summary_table = Table(box=None, padding=(0, 2))
    summary_table.add_column("Draw", style="bold yellow")
    summary_table.add_column("Numbers", style="green")
    summary_table.add_column("Sum", justify="right")
    summary_table.add_column("Cycle Progress", justify="right")
    summary_table.add_column("Missing", justify="left")
    
    lo_r, hi_r = rules.number_range
    cycle_data = analyze_cycle(df_full["numbers"].tolist(), list(range(lo_r, hi_r + 1)))
    prog = cycle_data['current_cycle_progress']
    missing = cycle_data['missing_in_current']
    missing_str = " ".join(f"{n:02d}" for n in missing) if missing else "CYCLE COMPLETE"
    
    summary_table.add_row(
        str(last_draw["draw_id"]),
        " ".join(f"{n:02d}" for n in sorted(last_nums)),
        str(sum(last_nums)),
        f"{prog*100:.1f}%",
        f"[bold red]{missing_str}[/bold red]"
    )
    console.print(Panel(summary_table, border_style="dim"))

    # 2. Pattern Grid (2 columns or wrapping)
    all_tables = []
    for pk in ["primes", "fibonacci", "magic", "multiples_3", "repeated", "frame", "odd", "even"]:
        config = PATTERN_CONFIG[pk]
        res = analyze_pattern_tendency(df_full, config["func"], config["name"])
        all_tables.append(Panel(create_tendency_table(res), border_style="blue", padding=(0,1)))
    
    console.print(Columns(all_tables))

def render_legacy_dashboard(df_full, rules, limit):
    """The original dashboard layout."""
    df = df_full.tail(limit)
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="insights", size=5),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="middle", ratio=1),
        Layout(name="right", ratio=2)
    )
    layout["left"].split_column(
        Layout(name="stats"),
        Layout(name="anomalies")
    )
    layout["middle"].split_column(
        Layout(name="voids", ratio=1),
        Layout(name="structural", ratio=1),
        Layout(name="clusters", ratio=1)
    )
    
    f_res = frequency.analyze(df, rules, top_n=5)
    d_res = deviation.analyze(df_full, rules, top_n=5)
    insights = insight_mod.get_automated_insights(df_full, rules, limit=limit)
    
    p_val = f_res.chi2_p_value
    p_style = "green" if p_val >= 0.05 else "red"
    p_badge = f"[{p_style}]P-Value: {p_val:.4f}[/{p_style}]"
    
    layout["insights"].update(Panel("\n".join(insights) + f"\n\n  {p_badge}", title="Automated Insight Ribbon", border_style="cyan"))
    layout["header"].update(Panel(f"[bold gold1]LottoLogic Terminal Dashboard: {rules.name}[/bold gold1] [dim](Window: last {limit})[/dim]", border_style="gold1"))
    layout["footer"].update(Panel("[dim]Press Ctrl+C to exit. View: Legacy Overview.[/dim]", border_style="dim"))
    
    # Tables for Stats, Anomalies, Voids, etc. (same as original code)
    # ... (skipping repetition for brevity in this tool call, but I will include it in the real file)
    # Actually, I must include EVERYTHING to ensure no regressions.
    
    # Stats
    s_table = Table(box=None)
    s_table.add_column("Rank", style="dim")
    s_table.add_column("Num", style="bold yellow")
    s_table.add_column("Z-Score", justify="right")
    for i, n in enumerate(f_res.hot):
        row = f_res.table[f_res.table["number"] == n].iloc[0]
        s_table.add_row(str(i+1), str(n), f"{row['z_score']:+.2f}")
    layout["stats"].update(Panel(s_table, title="Top Performers (Z-Score)"))
    
    # Anomalies
    a_table = Table(box=None)
    a_table.add_column("Num", style="bold red")
    a_table.add_column("Delay", justify="right")
    a_table.add_column("Max", justify="right", style="dim")
    for n in d_res.streak_free:
        row = d_res.table[d_res.table["number"] == n].iloc[0]
        max_d = d_res.gap_stats.get(n, {}).get("max", "-")
        a_table.add_row(str(n), f"{int(row['draws_since_last'])}d", str(max_d))
    layout["anomalies"].update(Panel(a_table, title="Overdue vs Max Delay"))

    # Voids
    draws_list = df_full["numbers"].tolist()
    lo_r, hi_r = rules.number_range
    v_data = analyze_voids(draws_list, cols=rules.board_cols, max_n=hi_r)
    v_table = Table(box=None)
    v_table.add_column("Sector", style="dim")
    v_table.add_column("Delay", justify="right")
    for r in sorted(v_data["row_delays"].keys()):
        delay = v_data["row_delays"][r]
        if delay >= 3: v_table.add_row(f"Row {r}", f"[bold red]{delay}d[/bold red]")
    layout["voids"].update(Panel(v_table, title="Spatial Voids (Cold Rows)"))

    # Structural
    last_nums = draws_list[-1]
    st_table = Table(box=None, show_header=False)
    st_table.add_row("AC Value", f"[bold cyan]{f_mod.get_ac_value(last_nums)}[/bold cyan]")
    st_table.add_row("Root Sum", f"[bold yellow]{f_mod.get_root_sum(last_nums)}[/bold yellow]")
    st_table.add_row("Unit Sum", f"[bold magenta]{f_mod.get_unit_metrics(last_nums)['sum']}[/bold magenta]")
    layout["structural"].update(Panel(st_table, title="Structural Harmony"))

    # Clusters
    c_table = Table(box=None, show_header=False)
    succ = f_mod.get_successive_metrics(last_nums)
    dist = f_mod.get_distance_metrics(last_nums)
    c_table.add_row("Max Gap", f"[bold yellow]{dist['max']}[/bold yellow]")
    c_table.add_row("Succ. Groups", f"[bold cyan]{succ['groups']}[/bold cyan]")
    c_table.add_row("Spread", f"[bold green]{dist['spread']}[/bold green]")
    
    # (v10.0) 30-day Gap History Sparkline
    from engine.cli.utils import sparkline
    gap_history = []
    for d in draws_list[-30:]:
        gap_history.append(float(f_mod.get_distance_metrics(d)["max"]))
    c_table.add_row("Gap History", sparkline(gap_history, width=15))
    
    layout["clusters"].update(Panel(c_table, title="Clusters & Gaps"))

    # Right panel
    lo_s, hi_s, _, _ = sum_range.most_probable_range(rules)
    s_val = sum(last_nums)
    last_p = get_pattern_string(last_nums, cols=rules.board_cols, max_n=hi_r)
    
    # (v10.0) Row Pattern Rarity
    all_patterns = [get_pattern_string(d, cols=rules.board_cols, max_n=hi_r) for d in draws_list]
    p_counts = Counter(all_patterns)
    p_occ = p_counts[last_p]
    p_rarity = (p_occ / len(draws_list)) * 100
    rarity_str = f"{p_rarity:.1f}%" if p_rarity > 1 else f"[bold red]{p_rarity:.2f}%[/bold red]"
    
    cycle_data = analyze_cycle(draws_list, list(range(lo_r, hi_r + 1)))
    prog = cycle_data['current_cycle_progress']
    missing = cycle_data['missing_in_current']
    missing_str = " ".join(f"{n:02d}" for n in missing) if missing else "COMPLETE"
    
    main_content = (
        f"\n[bold]Latest Draw:[/bold] {sorted(last_nums)}\n"
        f"[bold]Latest Sum:[/bold]  {s_val} ({'IN' if lo_s<=s_val<=hi_s else '[red]OUT[/red]'} band)\n\n"
        f"[bold]Row Pattern:[/bold] {last_p} (Rarity: {rarity_str})\n\n"
        f"[bold]Cycle Progress:[/bold]\n{bar_chart(prog, width=25)} {prog*100:.1f}%\n"
        f"[bold]Missing:[/bold] [bold red]{missing_str}[/bold red]\n"
    )
    layout["right"].update(Panel(main_content, title="Market Overview"))
    
    console.print(layout)
