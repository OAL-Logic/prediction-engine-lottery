"""
Daily Command 📰
================
Comprehensive morning digest — chains all key diagnostics into a single
sequential report with a final action summary.

Pipeline (in order)
-------------------
  1. Regime check      lottery compare-draws  (JS divergence)
  2. Conditions scan   lottery scan           (6-layer GO/NO-GO)
  3. EV analysis       lottery risk           (Kelly / Expected Value)
  4. Consensus ticket  lottery forecast       (weighted ensemble)
  5. Oracle insight    lottery oracle         (persona narrative)
  6. Log snapshot      lottery log            (append to JSONL)
  7. Pruning advice    (AutoML)               (backtest & lift check)

Output
------
  One consolidated card per stage + final action summary panel.

Example
-------
  lottery daily br/lotofacil
  lottery daily br/lotofacil --persona mystic
  lottery daily br/lotofacil --export-md daily.md
  lottery daily br/lotofacil --quiet
"""

from __future__ import annotations

import json
from datetime import date as _date
from pathlib import Path
from typing import Annotated, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from engine.cli.utils import get_adapter, print_command_summary

console = Console()

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DEFAULT_LOG = _DATA_DIR / "draw_log.jsonl"


def daily(
    lottery: Annotated[str, typer.Argument(help="Lottery name [Required]")],
    strategy: Annotated[str, typer.Option("--strategy", "-s",
        help="Primary strategy for scan layers")] = "bayesian",
    persona: Annotated[str, typer.Option("--persona", "-p",
        help="Oracle persona: quant | mystic | degen")] = "quant",
    jackpot: Annotated[Optional[float], typer.Option("--jackpot", "-j",
        help="Current jackpot (for EV calculation)")] = None,
    export_md: Annotated[Optional[str], typer.Option("--export-md",
        help="Append daily digest to this .md file")] = None,
    quiet: Annotated[bool, typer.Option("--quiet/--no-quiet",
        help="Print only the final summary (no per-stage detail)")] = False,
    matrix: Annotated[bool, typer.Option("--matrix",
        help="Show exhaustive strategy matrix and risk ledger")] = False,
    narrative: Annotated[bool, typer.Option("--narrative",
        help="Synthesize a 'Daily Intelligence Narrative' (Synapse Architect persona)")] = False,
) -> None:
    """📰 Comprehensive morning digest — all diagnostics in one pass.

    Chains: regime check → 6-layer scan → EV analysis → consensus ticket
    → oracle insight → daily log snapshot → pruning audit.

    Example: lottery daily br/lotofacil
             lottery daily br/lotofacil --persona mystic --jackpot 50000000
             lottery daily br/lotofacil --matrix
    """

    if not quiet:
        print_command_summary("daily", lottery, strategy=strategy, persona=persona)

    with console.status(f"[bold green]Loading {lottery}…"):
        adapter = get_adapter(lottery)
        df = adapter.fetch()

    rules = adapter.rules
    today = _date.today()
    lo, hi = rules.number_range
    pool_size = hi - lo + 1

    if not quiet:
        console.print(Panel(
            f"[bold cyan]{rules.name}[/bold cyan]  "
            f"[dim]{today}  {len(df)} draws on record[/dim]",
            title="📰 Daily Digest",
        ))

    results: dict = {}

    # ── Stage 1: Regime check ─────────────────────────────────────────────────
    if not quiet:
        console.print()
        console.rule("[bold]Stage 1 — Regime[/bold]")

    from engine.cli.commands.scan import _regime_js
    js_val, regime_verdict = _regime_js(df, lo, pool_size, recent=50)

    results["regime"] = {"js": js_val, "verdict": regime_verdict}

    if not quiet:
        color = "green" if regime_verdict == "STABLE" else "yellow" if regime_verdict == "DRIFT" else "red"
        console.print(Panel(
            f"Jensen-Shannon divergence: [bold]{js_val:.5f}[/bold]\n"
            f"Verdict: [{color}]{regime_verdict}[/{color}]  "
            f"[dim](STABLE=consistent, DRIFT=mild shift, SHIFT=regime change)[/dim]",
            title="🔀 Regime Check",
            border_style=color,
        ))

    # ── Stage 2: Conditions scan ──────────────────────────────────────────────
    if not quiet:
        console.print()
        console.rule("[bold]Stage 2 — Conditions[/bold]")

    from engine.cli.commands.scan import (
        _rolling_stable_pct, _stress_delta, _solar_kp,
    )
    from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name
    from engine.modules import frequency

    scan_scores: dict[str, int] = {}
    scan_details: dict[str, str] = {}

    # L1 fairness
    try:
        f_res = frequency.analyze(df.tail(100), rules, top_n=1)
        p = f_res.chi2_p_value
        scan_scores["fairness"] = 2 if p > 0.5 else 1 if p >= 0.05 else 0
        scan_details["fairness"] = f"chi²p={p:.4f}"
    except Exception:
        scan_scores["fairness"] = 1
        scan_details["fairness"] = "n/a"
        p = None

    # L2 stability
    stab = _rolling_stable_pct(df, adapter, strategy, 50, n_windows=4)
    if stab is None:
        scan_scores["stability"] = 1; scan_details["stability"] = "n/a"
    elif stab >= 0.5:
        scan_scores["stability"] = 2; scan_details["stability"] = f"stable={stab:.0%}"
    elif stab >= 0.25:
        scan_scores["stability"] = 1; scan_details["stability"] = f"mixed={stab:.0%}"
    else:
        scan_scores["stability"] = 0; scan_details["stability"] = f"noisy={stab:.0%}"

    # L3 cluster (informational)
    scan_scores["cluster"] = 1; scan_details["cluster"] = "informational"

    # L4 esoteric
    moon_ratio_val = moon_phase_ratio(today)
    moon_name = phase_name(today)
    kp = _solar_kp()
    es = 2 if moon_name in ("New Moon", "Full Moon") else 1
    if kp is not None:
        es = max(0, es - 1) if kp >= 5 else min(2, es + 1) if kp < 3 else es
    scan_scores["esoteric"] = es
    scan_details["esoteric"] = f"{moon_name}  kp={kp or '?'}"

    # L5 discrimination
    delta = _stress_delta(df, adapter, strategy)
    if delta is None:
        scan_scores["discrimination"] = 1; scan_details["discrimination"] = "n/a"
    elif delta > 0.02:
        scan_scores["discrimination"] = 2; scan_details["discrimination"] = f"Δ={delta:+.4f}"
    elif delta < -0.005:
        scan_scores["discrimination"] = 0; scan_details["discrimination"] = f"Δ={delta:+.4f} (inverted)"
    else:
        scan_scores["discrimination"] = 1; scan_details["discrimination"] = f"Δ={delta:+.4f}"

    # L6 regime (reuse)
    scan_scores["regime"] = 2 if regime_verdict == "STABLE" else 1 if regime_verdict == "DRIFT" else 0
    scan_details["regime"] = f"JS={js_val:.5f} ({regime_verdict})"

    scan_total = sum(scan_scores.values())
    scan_max   = len(scan_scores) * 2
    scan_pct   = scan_total / scan_max
    if scan_pct >= 0.70:
        verdict = "GO"; v_color = "green"
    elif scan_pct >= 0.40:
        verdict = "CAUTION"; v_color = "yellow"
    else:
        verdict = "NO-GO"; v_color = "red"

    results["scan"] = {
        "verdict": verdict, "score": scan_total, "max": scan_max,
        "moon": moon_name, "kp": kp, "delta": delta, "stab": stab,
    }

    if not quiet:
        st = Table(box=None, padding=(0, 1), show_header=False)
        st.add_column("Layer", style="bold")
        st.add_column("Score", justify="center")
        st.add_column("Detail")
        for layer, score in scan_scores.items():
            bar = "●" * score + "○" * (2 - score)
            color = "green" if score == 2 else "yellow" if score == 1 else "red"
            st.add_row(layer.capitalize(), f"[{color}]{bar}[/{color}]", scan_details[layer])

        console.print(Panel(
            f"[bold {v_color}]{verdict}[/bold {v_color}]  ({scan_total}/{scan_max})\n",
            title="🔬 Conditions Scan",
            border_style=v_color,
        ))
        console.print(st)

    # ── Stage 3: EV / Risk ────────────────────────────────────────────────────
    if not quiet:
        console.print()
        console.rule("[bold]Stage 3 — EV Analysis[/bold]")

    price = rules.ticket_price
    odds  = rules.jackpot_odds
    prob  = 1.0 / odds
    assumed_jackpot = jackpot or (price * odds * 0.4)
    ev    = prob * assumed_jackpot - price
    ev_ratio = assumed_jackpot / (price * odds)
    results["risk"] = {"ev": ev, "ev_ratio": ev_ratio, "jackpot": assumed_jackpot}

    if not quiet:
        ev_color = "green" if ev_ratio > 1.0 else "red"
        console.print(Panel(
            f"Jackpot odds: 1 in {odds:,}\n"
            f"Assumed jackpot: [bold]{assumed_jackpot:,.0f} {rules.currency}[/bold]  "
            f"[dim](pass --jackpot to override)[/dim]\n"
            f"Expected value: [bold {ev_color}]{ev:+.4f} {rules.currency}[/bold {ev_color}]\n"
            f"EV ratio: [{ev_color}]{ev_ratio:.3f}[/{ev_color}]  "
            f"[dim](> 1.0 = positive expectation)[/dim]",
            title="⚖️ EV Analysis",
            border_style=ev_color,
        ))

    # ── Optional: Strategic Decision Matrix ───────────────────────────────────
    if matrix and not quiet:
        console.print()
        console.rule("[bold]Strategic Decision Matrix[/bold]")
        
        from engine.modules.decision_matrix import (
            get_full_strategy_matrix, get_risk_ledger, get_logic_assumptions
        )

        with console.status("[bold blue]Auditing all strategies…"):
            strat_matrix = get_full_strategy_matrix(adapter)
            risks = get_risk_ledger(df, rules, results)
            assumptions = get_logic_assumptions(df, rules)

        # 1. Strategy Sentiment Table
        mt = Table(title="Strategy Sentiment Matrix", box=None, padding=(0, 2))
        mt.add_column("Strategy", style="bold cyan")
        mt.add_column("Lift", justify="right")
        mt.add_column("Sentiment", justify="center")
        
        # Sort by lift
        sorted_strats = sorted(strat_matrix.items(), key=lambda x: x[1].lift, reverse=True)
        for name, data in sorted_strats:
            lift_color = "green" if data.lift > 0 else "red"
            mt.add_row(name, f"[{lift_color}]{data.lift:+.1%}[/]", data.sentiment)
        
        console.print(mt)
        
        # 2. Risk Ledger
        if risks:
            console.print("\n[bold red]Systemic Risk Ledger[/bold red]")
            rt = Table(box=None, padding=(0, 2))
            rt.add_column("Risk", style="bold red")
            rt.add_column("Impact", style="bold")
            rt.add_column("Description")
            for r in risks:
                rt.add_row(r["risk"], f"[bold]{r['impact']}[/]", r["description"])
            console.print(rt)
            
        # 3. Logic Assumptions
        console.print("\n[bold yellow]Model Assumptions[/bold yellow]")
        for a in assumptions:
            console.print(f"  • {a}")
        console.print()

    # ── Optional: Daily Intelligence Narrative ────────────────────────────────
    if narrative and not quiet:
        console.print()
        console.rule("[bold]Daily Intelligence Narrative[/bold]")
        
        from engine.modules.narrative import NarrativeGenerator
        gen = NarrativeGenerator(adapter, df, results)
        briefing = gen.generate_briefing_v10(persona="Synapse Architect")
        
        from rich.markdown import Markdown
        console.print(Markdown(briefing))
        console.print()

    # ── Stage 4: Consensus ticket ─────────────────────────────────────────────
    if not quiet:
        console.print()
        console.rule("[bold]Stage 4 — Consensus Ticket[/bold]")

    ticket: list[int] = []
    if verdict in ("GO", "CAUTION"):
        from engine.cli.commands.next_draw import _quick_forecast
        ticket = _quick_forecast(df, adapter, window=50)
        if ticket:
            from engine.cli.commands.forecast import _log_ticket
            _log_ticket(lottery, ticket, source="daily")

    results["ticket"] = ticket

    if not quiet:
        if ticket:
            ticket_str = "  ".join(str(n) for n in ticket)
            console.print(Panel(
                f"[bold yellow]{ticket_str}[/bold yellow]",
                title="🔮 Consensus Ticket",
                border_style="yellow",
            ))
        else:
            console.print("[dim]Ticket skipped — conditions NO-GO.[/dim]")

    # ── Stage 5: Oracle ───────────────────────────────────────────────────────
    if not quiet:
        console.print()
        console.rule("[bold]Stage 5 — Oracle[/bold]")

    try:
        from engine.modules import insights as insight_mod
        from engine.cli.commands.oracle import PERSONAS
        p_data = PERSONAS.get(persona, PERSONAS["quant"])
        insights = insight_mod.get_automated_insights(df, rules, limit=100)
        results["oracle"] = {"persona": persona, "insights": insights[:3]}

        if not quiet:
            lines = []
            for insight in insights[:4]:
                text = insight
                for tag in ["[red]●[/red]", "[green]●[/green]", "[yellow]●[/yellow]",
                            "[cyan]●[/cyan]", "[blue]●[/blue]", "[magenta]●[/magenta]"]:
                    text = text.replace(tag, "•")
                if persona == "mystic":
                    text = text.replace("distribution", "cosmic flow").replace("Statistical", "Vibrational")
                lines.append(f"  {text}")
            console.print(Panel(
                f"[italic]\"{p_data['intro']}\"[/italic]\n\n" + "\n".join(lines),
                title=f"{p_data['emoji']} {p_data['name']}",
                border_style=p_data["style"],
            ))
    except Exception:
        results["oracle"] = {"persona": persona, "insights": []}

    # ── Stage 6: Log snapshot ─────────────────────────────────────────────────
    _append_log(lottery, df, adapter, strategy, delta, stab, p if isinstance(p, float) else None,
                moon_name, moon_ratio_val, kp, js_val, ev, ticket)

    # ── Stage 7: Pruning Advice (AutoML) ──────────────────────────────────────
    pruning_results = []
    if not quiet:
        console.print()
        console.rule("[bold]Stage 7 — Pruning Advice[/bold]")

        try:
            from engine.modules.pruning import run_pruning_audit
            from engine.strategies import STRATEGY_PRESETS

            # Audit the 'default' set
            audit_set = STRATEGY_PRESETS.get("default", ["weighted", "markov", "bayesian"])

            with console.status("[bold blue]Auditing strategy performance (last 50 draws)…"):
                pruning_results = run_pruning_audit(adapter, audit_set, window=50)

            if pruning_results:
                pt = Table(box=None, padding=(0, 1))
                pt.add_column("Strategy", style="bold")
                pt.add_column("Lift vs Random", justify="right")
                pt.add_column("Status", justify="center")

                hibernated_count = 0
                for res in pruning_results:
                    lift_fmt = f"{res.lift_over_random:+.1%}"
                    color = "green" if res.lift_over_random > 0.05 else "yellow" if res.lift_over_random > 0 else "red"
                    status = "[red]⚠ SUGGEST HIBERNATE[/red]" if res.is_hibernated else "[green]ACTIVE[/green]"
                    if res.is_hibernated: hibernated_count += 1

                    pt.add_row(res.strategy_name, f"[{color}]{lift_fmt}[/{color}]", status)

                console.print(pt)

                if hibernated_count > 0:
                    console.print(f"\n[dim]💡 {hibernated_count} strategies are currently underperforming the random baseline.[/dim]")
                    console.print("[dim]   Consider using [bold]--strategy[/bold] to focus on those with positive lift.[/dim]")

        except Exception as exc:
            console.print(f"[dim]Pruning audit skipped: {exc}[/dim]")

    # ── Final Summary ─────────────────────────────────────────────────────────
    if not quiet:
        console.print()
        console.rule("[bold]ACTION SUMMARY[/bold]")

    ticket_str = "  ".join(str(n) for n in ticket) if ticket else "—"
    
    summary_lines = [
        f"  Regime     : [{'green' if regime_verdict == 'STABLE' else 'yellow' if regime_verdict == 'DRIFT' else 'red'}]{regime_verdict}[/]  JS={js_val:.5f}",
        f"  Conditions : [bold {'green' if verdict == 'GO' else 'yellow' if verdict == 'CAUTION' else 'red'}]{verdict}[/]  ({scan_total}/{scan_max})",
        f"  EV ratio   : [{('green' if ev_ratio > 1.0 else 'red')}]{ev_ratio:.3f}[/]  ({'+EV' if ev_ratio > 1.0 else '-EV'})",
        f"  Ticket     : [bold yellow]{ticket_str}[/bold yellow]",
        f"  Log        : [dim]✔ appended to {_DEFAULT_LOG.name}[/dim]",
    ]

    console.print(Panel(
        "\n".join(summary_lines),
        title=f"📰 {rules.name} — {today}",
        border_style=v_color,
    ))

    if quiet:
        # Quiet mode: just the verdict and ticket
        console.print(f"{verdict}  {ticket_str}")

    if export_md:
        _write_md(export_md, lottery, rules.name, today, results, scan_scores,
                  scan_details, verdict, scan_total, scan_max, persona)
        if not quiet:
            console.print(f"[green]✔ Daily digest appended to {export_md}[/green]")


def _append_log(lottery, df, adapter, strategy, delta, stab, chi2_p,
                moon_name, moon_ratio_val, kp, js_val, ev, ticket):
    """Silently append a log record to the default JSONL."""
    import json as _json
    from engine.strategies import get_strategy
    from engine.strategies.fun.moon_phase import moon_phase_ratio, phase_name

    record: dict = {
        "date":       _date.today().isoformat(),
        "draw_id":    int(df.iloc[-1]["draw_id"]) if not df.empty else -1,
        "game":       lottery,
        "strategy":   strategy,
        "confidence": None,
        "entropy":    None,
        "stable":     None,
        "chi2_p":     round(chi2_p, 6) if chi2_p is not None else None,
        "moon_phase": moon_name,
        "moon_ratio": round(moon_ratio_val, 4),
        "solar_kp":   kp,
        "js_val":     round(js_val, 6) if js_val is not None else None,
        "ev":         round(ev, 4) if ev is not None else None,
        "ticket":     ticket,
    }

    try:
        strat = get_strategy(strategy)
        res = strat.suggest(df.tail(50), adapter.rules, count=1, temperature=1.0)
        record["confidence"] = round(res.confidence, 6)
        vals = np.array(list(res.scores.values()), dtype=float)
        vals = vals / (vals.sum() or 1.0)
        vals = vals[vals > 0]
        record["entropy"] = round(float(-np.sum(vals * np.log(vals + 1e-12))), 6)
    except Exception:
        pass

    if stab is not None:
        record["stable"] = stab >= 0.5

    _DEFAULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(_DEFAULT_LOG, "a", encoding="utf-8") as f:
        f.write(_json.dumps(record) + "\n")


def _write_md(path, lottery, game_name, today, results, scan_scores,
              scan_details, verdict, score, max_score, persona):
    rows = "".join(
        f"| {k.capitalize()} | {scan_details[k]} | {'●' * scan_scores[k]}{'○' * (2 - scan_scores[k])} |\n"
        for k in scan_scores
    )
    ticket = results.get("ticket", [])
    ticket_str = ", ".join(str(n) for n in ticket) if ticket else "none"
    risk = results.get("risk", {})
    regime = results.get("regime", {})

    content = f"""---
type: pattern-log
subtype: daily
game: "{game_name}"
lottery: "{lottery}"
date: {today}
verdict: {verdict}
score: {score}/{max_score}
regime: {regime.get('verdict', '?')}
js_divergence: {regime.get('js', 0):.5f}
ev_ratio: {risk.get('ev_ratio', 0):.3f}
ticket: [{ticket_str}]
source-strategy: "synapse"
confidence-rating: {results.get('scan', {}).get('score', 0) / results.get('scan', {}).get('max', 1):.2f}
tags: [prediction-engine, daily, digest, #lottery/analysis]
data-payload: {json.dumps(results)}
---

# Daily Digest: {game_name} — {today}

**Verdict:** {verdict} ({score}/{max_score}) | **Regime:** {regime.get('verdict','?')} | **EV ratio:** {risk.get('ev_ratio', 0):.3f}

## Scan Layers

| Layer | Detail | Signal |
|-------|--------|--------|
{rows}
## Consensus Ticket

**`{ticket_str}`**

---
"""
    p = Path(path)
    # STORY 3.2: Create new file (or overwrite), don't append
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

    # STORY 3.2: Update central index (docs/analysis-index.md)
    index_path = p.parent.parent / "docs" / "analysis-index.md"
    # Ensure index exists
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# Lottery Analysis Index\n\n| Date | Game | Analysis File |\n| :--- | :--- | :--- |\n")
    
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(f"| {today} | {game_name} | [[{p.name}]] |\n")
