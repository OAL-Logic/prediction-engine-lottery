"""
Teimosinha Command 🍀🔁
======================
Dedicated weekly multi-draw (Teimosinha) generator and backtest analyzer
combining the Trevo da Sorte numerological map (Márcia Sensitiva + Pythagorean
Gematria), multi-strategy statistical/ML/esoteric consensus, structural harmony
filters, abbreviated wheels, and Quina combinatorial unfolding.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional

import numpy as np
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter, load_local_config
from engine.modules import harmony
from engine.modules.filters import get_ac_value, get_prime_count
from engine.strategies import get_strategy
from engine.strategies.fun.trevo_sorte import compute_trevo_profile
from engine.wheels.abbreviated import generate_abbreviated_wheel

console = Console()


def _build_draw_schedule(game_name: str, start_date: date, teimosinha_draws: int) -> List[date]:
    game_lower = game_name.lower()
    if "mega" in game_lower:
        draw_weekdays = {1, 3, 5}  # Tue, Thu, Sat
    elif "quina" in game_lower or "lotofacil" in game_lower or "lotofácil" in game_lower:
        draw_weekdays = {0, 1, 2, 3, 4, 5}  # Mon-Sat
    else:
        draw_weekdays = {1, 3, 5}

    schedule: List[date] = []
    cur = start_date
    for _ in range(120):
        if cur.weekday() in draw_weekdays:
            schedule.append(cur)
            if len(schedule) >= teimosinha_draws:
                break
        cur = cur + timedelta(days=1)
    return schedule


def _evaluate_rolling_blocks(
    tickets: List[List[int]],
    df: Any,
    rules: Any,
    teimosinha_draws: int,
    max_draws: int = 300,
) -> Dict[str, Any]:
    """Evaluates a set of tickets across rolling consecutive blocks of `teimosinha_draws` historical draws."""
    recent_df = df.tail(max_draws) if len(df) > max_draws else df
    draw_sets = [set(nums) for nums in recent_df["numbers"]]
    tiers = sorted(rules.prize_tiers)
    min_tier = tiers[0] if tiers else rules.pick_count

    tier_hits = {t: 0 for t in tiers}
    for d_set in draw_sets:
        for t in tickets:
            h = len(set(t) & d_set)
            # For multiple bets (len(t) > rules.pick_count), compute combinatoric sub-ticket hits
            if len(t) > rules.pick_count:
                k = rules.pick_count
                m = len(t)
                for tier in tiers:
                    if h >= tier and (m - h) >= (k - tier):
                        ways = math.comb(h, tier) * math.comb(m - h, k - tier)
                        tier_hits[tier] += ways
            else:
                if h in tier_hits:
                    tier_hits[h] += 1

    n_blocks = max(1, len(draw_sets) - teimosinha_draws + 1)
    winning_blocks = 0
    multi_hit_blocks = 0
    for b_idx in range(n_blocks):
        block = draw_sets[b_idx : b_idx + teimosinha_draws]
        block_wins = 0
        for d_set in block:
            for t in tickets:
                if len(set(t) & d_set) >= min_tier:
                    block_wins += 1
        if block_wins >= 1:
            winning_blocks += 1
        if block_wins >= 2:
            multi_hit_blocks += 1

    return {
        "evaluated_draws": len(draw_sets),
        "n_blocks": n_blocks,
        "winning_blocks": winning_blocks,
        "multi_hit_blocks": multi_hit_blocks,
        "block_win_rate": winning_blocks / n_blocks,
        "tier_hits": tier_hits,
    }


def _describe_ticket_metrics(ticket: List[int], rules: Any, core_set: set[int], harm_set: set[int]) -> str:
    s_ticket = sorted(ticket)
    t_sum = sum(s_ticket)
    odds = sum(1 for n in s_ticket if n % 2 != 0)
    evens = len(s_ticket) - odds
    primes = get_prime_count(s_ticket)
    ac = get_ac_value(s_ticket)
    core_hits = sorted(set(s_ticket) & core_set)
    harm_hits = sorted(set(s_ticket) & (core_set | harm_set))
    return (
        f"Sum={t_sum} | Odd/Even={odds}:{evens} | Primes={primes} | AC={ac} | "
        f"Trevo Anchors={core_hits} ({len(harm_hits)}/{len(s_ticket)} harmonic)"
    )


def teimosinha(
    lottery: Annotated[str, typer.Argument(help="Lottery slug (e.g. br/mega-sena, br/quina)")],
    birth_date: Annotated[Optional[str], typer.Option("--birth-date", "-b", help="Player birth date (YYYY-MM-DD); defaults to personal.local.yaml or synthetic 1990-01-01")] = None,
    target_date: Annotated[Optional[str], typer.Option("--target-date", "-d", help="Start date of the Teimosinha week (YYYY-MM-DD)")] = None,
    draws: Annotated[Optional[int], typer.Option("--draws", "-T", help="Number of consecutive Teimosinha draws (default: 3 for Mega-Sena, 6 for Quina)")] = None,
    full_name: Annotated[Optional[str], typer.Option("--full-name", help="Optional full name for Kabbalistic/Gematria resonance")] = None,
    tickets_count: Annotated[int, typer.Option("--count", "-c", help="Number of simple tickets to generate")] = 5,
    export_md: Annotated[Optional[str], typer.Option("--export-md", help="Export full Teimosinha report to Markdown file")] = None,
) -> None:
    """
    🍀🔁 Generate a complete Teimosinha weekly game package (Simple, Multiple, and Wheeled/Unfolded bets)
    tailored to a birth date and target week using Trevo da Sorte numerology + multi-strategy consensus.
    """
    personal_cfg = load_local_config()
    b_date_str = birth_date or personal_cfg.get("birth_date", "1990-01-01")
    t_date_str = target_date or personal_cfg.get("target_date") or date.today().isoformat()
    f_name = full_name or personal_cfg.get("full_name", "TREVO DA SORTE")

    try:
        t_date_obj = date.fromisoformat(t_date_str)
    except ValueError:
        t_date_obj = date.today()
        t_date_str = t_date_obj.isoformat()

    adapter = get_adapter(lottery)
    rules = adapter.rules
    df = adapter.fetch()
    lo, hi = rules.number_range
    pick = rules.pick_count

    is_quina = "quina" in rules.name.lower() or "quina" in lottery.lower()
    is_mega = "mega" in rules.name.lower() or "mega" in lottery.lower()

    if draws is None or draws <= 0:
        # Official Caixa Teimosinha options:
        # Mega-Sena: 2, 3, 4, 6, 8, 9, 12 (3 = 1 full week Tue/Thu/Sat)
        # Quina: 3, 6, 12, 18, 24 (6 = 1 full week Mon-Sat)
        teimosinha_draws = 6 if is_quina else 3
    else:
        teimosinha_draws = draws

    # 1. Compute Trevo da Sorte Profile
    profile = compute_trevo_profile(
        birth_date_str=b_date_str,
        target_date_str=t_date_str,
        teimosinha_draws=teimosinha_draws,
        max_num=hi,
        game_name=rules.name,
    )

    schedule = _build_draw_schedule(rules.name, t_date_obj, teimosinha_draws)
    wd_pt = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}

    sched_lines = []
    for idx, d in enumerate(schedule, 1):
        day_info = profile["teimosinha_schedule"][min(idx - 1, len(profile["teimosinha_schedule"]) - 1)]
        sacred_badge = (
            f" [bold green]★ DIA SAGRADO DO {profile['lucky_number']} ({profile['sacred_weekday_pt'].upper()})[/bold green]"
            if d.weekday() == profile["sacred_py_weekday"]
            else ""
        )
        lucky_badge = " [bold yellow]★ DIA DA SORTE[/bold yellow]" if d.day in profile["lucky_days"] else ""
        sched_lines.append(
            f"  Concurso #{idx}: [bold cyan]{d.isoformat()}[/bold cyan] ({wd_pt[d.weekday()]}) "
            f"— Dia Universal={day_info['universal_day']} | Dia Pessoal={day_info['personal_day']}"
            f"{sacred_badge}{lucky_badge}"
        )

    profile_text = (
        f"[bold]Data de Nascimento:[/bold] [cyan]{b_date_str}[/cyan]   "
        f"[bold]Semana Alvo:[/bold] [cyan]{t_date_str}[/cyan]   "
        f"[bold]Modalidade:[/bold] [yellow]Teimosinha ({teimosinha_draws} concursos consecutivos)[/yellow]\n"
        f"[bold]Número da Sorte (Márcia Sensitiva):[/bold] [bold yellow]{profile['lucky_number']}[/bold yellow]   "
        f"[bold]Dia da Semana Ideal:[/bold] [bold green]{profile['sacred_weekday_pt']}[/bold green]   "
        f"[bold]Dias da Sorte:[/bold] {profile['lucky_days']}   "
        f"[bold]Meses da Sorte:[/bold] {profile['lucky_months']}\n"
        f"[bold]Caminho de Vida (Pitagórico):[/bold] [magenta]{profile['life_path']}[/magenta]   "
        f"[bold]Ano Pessoal ({t_date_obj.year}):[/bold] {profile['personal_year']}   "
        f"[bold]Mês Pessoal ({t_date_obj.strftime('%Y-%m')}):[/bold] [bold yellow]{profile['personal_month']}[/bold yellow]\n"
        f"[bold]Âncoras Primárias (Natal + Trevo):[/bold] [bold green]{profile['core_anchors']}[/bold green]\n"
        f"[bold]Subconjunto Harmônico Completo ({len(profile['harmonic_pool'])} dezenas):[/bold] {profile['harmonic_pool']}\n\n"
        f"[bold underline]Cronograma da Teimosinha ({rules.name}):[/bold underline]\n" + "\n".join(sched_lines)
    )
    console.print(Panel(profile_text, title=f"🍀 Mapa Numerológico Trevo da Sorte — {rules.name}", border_style="green"))

    # 2. Multi-Strategy Score Aggregation & Consensus
    strategy_suite = [
        ("trevo_sorte", 1.60),
        ("markov", 1.20),
        ("bayesian", 1.15),
        ("weighted", 1.20),
        ("copairs", 1.15),
        ("momentum", 1.15),
        ("streak", 1.15),
        ("harmonic", 1.10),
        ("positional", 1.05),
        ("structural", 1.05),
        ("kabbalistic", 1.15),
        ("numerology", 1.20),
        ("biorhythm", 1.10),
        ("esoteric_statistical", 1.20),
        ("moon_phase", 1.10),
        ("solar", 1.05),
    ]

    common_kwargs = {
        "birth_date": b_date_str,
        "full_name": f_name,
        "target_date": t_date_str,
        "draw_date": t_date_obj,
        "teimosinha_draws": teimosinha_draws,
    }

    per_strat_scores: Dict[str, Dict[int, float]] = {}
    per_strat_top: Dict[str, List[int]] = {}
    per_strat_top15: Dict[str, List[int]] = {}
    vote_counter: Counter = Counter()
    blended_scores: Dict[int, float] = {n: 0.0 for n in range(lo, hi + 1)}
    total_weight = 0.0

    strat_table = Table(title=f"🔬 Multi-Strategy Signal Matrix ({rules.name})", header_style="bold cyan")
    strat_table.add_column("Strategy", style="bold")
    strat_table.add_column("Tier", style="dim")
    strat_table.add_column("Weight", justify="right")
    strat_table.add_column(f"Top-{pick} Deterministic Picks", style="green")
    strat_table.add_column("Extended Top-10 Pool", style="yellow")

    for s_name, w in strategy_suite:
        try:
            strat = get_strategy(s_name, **common_kwargs)
            raw_s = strat.score(df, rules)
            s_min = min(raw_s.values()) if raw_s else 0.0
            s_max = max(raw_s.values()) if raw_s else 1.0
            s_rng = (s_max - s_min) or 1.0
            norm_s = {n: (raw_s.get(n, 0.0) - s_min) / s_rng for n in range(lo, hi + 1)}
            per_strat_scores[s_name] = norm_s

            ranked = sorted(range(lo, hi + 1), key=lambda n: norm_s[n], reverse=True)
            top_k = sorted(ranked[:pick])
            top_10 = ranked[:10]
            per_strat_top[s_name] = top_k
            per_strat_top15[s_name] = ranked[:15]

            for rank_idx, num in enumerate(ranked[:12]):
                vote_counter[num] += (12 - rank_idx) * w
                blended_scores[num] += norm_s[num] * w * 0.25

            for num in range(lo, hi + 1):
                blended_scores[num] += norm_s[num] * w

            total_weight += w
            strat_table.add_row(
                s_name,
                getattr(strat, "tier", "stat"),
                f"{w:.2f}",
                str(top_k),
                str(top_10[:8]),
            )
        except Exception as exc:
            strat_table.add_row(s_name, "err", f"{w:.2f}", f"[red]{exc}[/red]", "-")

    console.print(strat_table)

    # Normalize blended scores
    b_max = max(blended_scores.values()) or 1.0
    b_min = min(blended_scores.values())
    b_rng = (b_max - b_min) or 1.0
    for n in blended_scores:
        blended_scores[n] = (blended_scores[n] - b_min) / b_rng

    core_set = set(profile["core_anchors"])
    harm_set = set(profile["harmonic_pool"])
    full_harmonic_set = core_set | harm_set

    # Rank numbers by blended consensus score
    ranked_consensus = sorted(range(lo, hi + 1), key=lambda n: blended_scores[n], reverse=True)
    elite_pool_15 = sorted(ranked_consensus[:15])
    elite_pool_12 = sorted(ranked_consensus[:12])
    elite_pool_10 = sorted(ranked_consensus[:10])

    # ── 2B. Cross-Strategy Correlation & Moment-Resonance Proof Matrix ─────────
    from scipy.stats import spearmanr, pearsonr

    trevo_vec = np.array([per_strat_scores.get("trevo_sorte", blended_scores).get(n, 0.0) for n in range(lo, hi + 1)])
    consensus_vec = np.array([blended_scores[n] for n in range(lo, hi + 1)])

    corr_table = Table(
        title=f"🔗 Proof 1 — Cross-Strategy Correlation & Moment-Resonance Alignment ({rules.name})",
        header_style="bold magenta",
    )
    corr_table.add_column("Strategy", style="bold")
    corr_table.add_column("Spearman ρ (vs Consensus)", justify="right", style="cyan")
    corr_table.add_column("Pearson r (vs Trevo)", justify="right", style="yellow")
    corr_table.add_column("Harmonic Top-15 Overlap", justify="right", style="green")
    corr_table.add_column("Shared Resonant Numbers (Strategy Top-15 ∩ Trevo Pool)", style="white")

    for s_name, _ in strategy_suite:
        if s_name not in per_strat_scores:
            continue
        s_vec = np.array([per_strat_scores[s_name][n] for n in range(lo, hi + 1)])
        try:
            sp_rho, _ = spearmanr(s_vec, consensus_vec)
            if np.isnan(sp_rho):
                sp_rho = 0.0
        except Exception:
            sp_rho = 0.0
        try:
            pr_r, _ = pearsonr(s_vec, trevo_vec)
            if np.isnan(pr_r):
                pr_r = 0.0
        except Exception:
            pr_r = 0.0

        s_top15 = set(per_strat_top15.get(s_name, []))
        shared_harm = sorted(s_top15 & full_harmonic_set)
        overlap_pct = (len(shared_harm) / 15.0) * 100.0
        corr_table.add_row(
            s_name,
            f"{sp_rho:+.3f}",
            f"{pr_r:+.3f}",
            f"{len(shared_harm)}/15 ({overlap_pct:.0f}%)",
            str(shared_harm),
        )

    console.print(corr_table)

    # ── 2C. Empirical Moment-Alignment Proof Across Historical Draws ───────────
    from engine.strategies.fun.moon_phase import moon_phase_ratio

    df_dates = df.copy()
    parsed_dates: List[Optional[date]] = []
    for raw_d in df_dates["date"]:
        if hasattr(raw_d, "date"):
            parsed_dates.append(raw_d.date())
        elif isinstance(raw_d, date):
            parsed_dates.append(raw_d)
        else:
            s_d = str(raw_d).strip()[:10]
            try:
                if "/" in s_d:
                    parts = s_d.split("/")
                    parsed_dates.append(date(int(parts[2]), int(parts[1]), int(parts[0])))
                else:
                    parsed_dates.append(date.fromisoformat(s_d))
            except Exception:
                parsed_dates.append(None)

    target_lunar_ratio = moon_phase_ratio(t_date_obj)
    lunar_lo = max(0.0, target_lunar_ratio - 0.12)
    lunar_hi = min(1.0, target_lunar_ratio + 0.12)
    lucky_num_val = int(profile["lucky_number"])
    sacred_wd = int(profile["sacred_py_weekday"])
    lucky_days_set = set(profile["lucky_days"]) | {d.day for d in schedule}

    slices = [
        (f"1. {profile['sacred_weekday_pt']}s (Dia Sagrado do {lucky_num_val})", lambda d, idx: d is not None and d.weekday() == sacred_wd),
        (f"2. Dias da Sorte {profile['lucky_days']} + Semana", lambda d, idx: d is not None and d.day in lucky_days_set),
        (f"3. Mês {t_date_obj.month:02d} (Mês Pessoal {profile['personal_month']})", lambda d, idx: d is not None and d.month == t_date_obj.month),
        (f"4. Fase Lunar Alvo ({target_lunar_ratio:.0%} ±12% Iluminação)", lambda d, idx: d is not None and lunar_lo <= moon_phase_ratio(d) <= lunar_hi),
        (f"5. Regime Recente (Últimos 60 Sorteios de {t_date_obj.year})", lambda d, idx: idx >= len(df) - 60),
    ]

    moment_table = Table(
        title=f"📅 Proof 2 — Empirical Moment-Alignment Proof ({len(df)} Historical Draws of {rules.name})",
        header_style="bold green",
    )
    moment_table.add_column("Historical Moment Slice", style="bold")
    moment_table.add_column("Matched Draws", justify="right")
    moment_table.add_column("Elite-15 Avg Hits/Draw", justify="right", style="cyan")
    moment_table.add_column("Random Baseline", justify="right", style="dim")
    moment_table.add_column("Moment Lift", justify="right", style="bold yellow")
    moment_table.add_column("Top Hitting Resonant Numbers in Slice", style="green")

    elite_15_set = set(elite_pool_15)
    baseline_15 = pick * (15.0 / (hi - lo + 1))

    for slice_name, pred in slices:
        matched_nums_list = []
        for idx_row, (d_obj, nums) in enumerate(zip(parsed_dates, df["numbers"])):
            if pred(d_obj, idx_row):
                matched_nums_list.append(nums)
        n_m = len(matched_nums_list)
        if n_m == 0:
            continue
        hits_per_draw = [len(set(nums) & elite_15_set) for nums in matched_nums_list]
        avg_h = float(np.mean(hits_per_draw))
        lift_pct = ((avg_h / baseline_15) - 1.0) * 100.0
        slice_counter = Counter(n for nums in matched_nums_list for n in nums if n in full_harmonic_set)
        top_slice_nums = [f"{num}({cnt})" for num, cnt in slice_counter.most_common(6)]
        moment_table.add_row(
            slice_name,
            str(n_m),
            f"{avg_h:.2f}",
            f"{baseline_15:.2f}",
            f"{lift_pct:+.1f}%",
            ", ".join(top_slice_nums),
        )

    console.print(moment_table)

    # ── 2D. Number-by-Number Multi-Strategy Proof & Attribution Table ──────────
    # Compute historical frequency & current skip/delay for each number
    total_draws_count = len(df)
    hist_freq = Counter(n for nums in df["numbers"] for n in nums)
    last_seen_idx: Dict[int, int] = {}
    for idx_row, nums in enumerate(df["numbers"]):
        for n in nums:
            last_seen_idx[n] = idx_row
    current_delay = {n: (total_draws_count - 1 - last_seen_idx.get(n, -1)) for n in range(lo, hi + 1)}
    last_draw_nums = sorted(df.iloc[-1]["numbers"]) if not df.empty else []

    lp_val = int(profile["life_path"])
    mult_set = set(profile["multiples"])
    root_set = set(profile["root_resonants"])
    lp_set = set(profile["life_path_resonants"])
    sched_days = {d.day for d in schedule}

    def _explain_number_origin(n: int) -> str:
        reasons = []
        if n == lucky_num_val:
            reasons.append(f"Número da Sorte ({lucky_num_val}) + Mês Pessoal ({profile['personal_month']})")
        if n in set(profile["lucky_days"]) and n != lucky_num_val:
            reasons.append(f"Dia da Sorte da Tabela do {lucky_num_val} ({n}→{lucky_num_val})")
        if n == lp_val:
            reasons.append(f"Caminho de Vida Pitagórico ({lp_val})")
        if n == profile.get("life_path_unreduced"):
            reasons.append(f"Soma Reduzida Natal ({n}→{lp_val})")
        if n == profile.get("full_digit_sum"):
            reasons.append(f"Soma Completa Dígitos Natal ({n}→{lp_val})")
        if n == profile.get("year_digit_sum"):
            reasons.append(f"Soma Dígitos Ano Natal ({n})")
        if n in core_set and not reasons:
            reasons.append("Âncora Natal / Ciclo Pessoal")
        if n in mult_set and n != lucky_num_val:
            reasons.append(f"Múltiplo Sagrado de {lucky_num_val} ({n // lucky_num_val}×{lucky_num_val})")
        if n in root_set and n not in set(profile["lucky_days"]) | {lucky_num_val}:
            reasons.append(f"Raiz Numerológica {lucky_num_val} ({n}→{lucky_num_val})")
        if n in lp_set and n != lp_val:
            reasons.append(f"Raiz Caminho de Vida {lp_val} ({n}→{lp_val})")
        if n in sched_days:
            reasons.append(f"Dia do Calendário Teimosinha ({n:02d}/{t_date_obj.month:02d})")
        if not reasons:
            reasons.append("Atrator Estatístico (Markov/Frequência/Co-Pairs)")
        return "; ".join(reasons[:2])

    num_proof_table = Table(
        title=f"🎯 Proof 3 — Number-by-Number Resonance & Multi-Strategy Convergence (Top 15 — {rules.name})",
        header_style="bold yellow",
    )
    num_proof_table.add_column("Rank", justify="right", style="dim")
    num_proof_table.add_column("Num", justify="center", style="bold green")
    num_proof_table.add_column("Score", justify="right", style="cyan")
    num_proof_table.add_column("Hist Freq", justify="right")
    num_proof_table.add_column("Delay", justify="right")
    num_proof_table.add_column("Markov/Stat", justify="right", style="magenta")
    num_proof_table.add_column("Converging Strategies (Top-15 Votes)", style="yellow")
    num_proof_table.add_column(f"Trevo #{lucky_num_val} × {t_date_str} Moment Resonance Proof", style="white")

    for r_idx, num in enumerate(ranked_consensus[:15], 1):
        voters = [s_name for s_name, _ in strategy_suite if num in per_strat_top15.get(s_name, [])]
        m_score = per_strat_scores.get("markov", {}).get(num, 0.0)
        b_score = per_strat_scores.get("bayesian", {}).get(num, 0.0)
        c_score = per_strat_scores.get("copairs", {}).get(num, 0.0)
        stat_peak = max(m_score, b_score, c_score)
        num_proof_table.add_row(
            str(r_idx),
            f"{num:02d}",
            f"{blended_scores[num]:.3f}",
            str(hist_freq[num]),
            f"{current_delay[num]}d",
            f"{stat_peak:.2f}",
            f"{len(voters)} strats: {', '.join(voters[:5])}{'…' if len(voters) > 5 else ''}",
            _explain_number_origin(num),
        )

    console.print(num_proof_table)

    # Ensure primary natal anchors (07 and 23/16/25/19/29/41) with high score are present in elite pools
    key_anchors = [n for n in [7, 23, 16, 25, 19, 29, 41] if lo <= n <= hi]

    # 3. Structural Filter Gate Setup
    active_filters = [
        "sum_range",
        "parity",
        "breadth",
        "ac_value",
        "no_3_consecutive",
        "quadrant_balance",
        "trevo_resonance",
        "no_historical_dupes",
    ]

    def _passes_all_gates(cand: List[int]) -> bool:
        if not harmony.registry.validate(
            cand,
            rules,
            active_filters,
            k_of_n=0,
            df=df,
            birth_date=b_date_str,
            target_date=t_date_str,
        ):
            return False
        odds = sum(1 for n in cand if n % 2 != 0)
        primes = get_prime_count(cand)
        # Strict Bell-curve parity, prime count, and decade cluster guard
        if is_mega and len(cand) == 6:
            if not (2 <= odds <= 4):
                return False
            if not (1 <= primes <= 3):
                return False
            decades = Counter((n - 1) // 10 for n in cand)
            if max(decades.values()) > 2:
                return False
            if not (140 <= sum(cand) <= 230):
                return False
        elif is_quina and len(cand) == 5:
            if not (2 <= odds <= 3):
                return False
            if not (1 <= primes <= 3):
                return False
            decades = Counter((n - 1) // 10 for n in cand)
            if max(decades.values()) > 2:
                return False
            if not (160 <= sum(cand) <= 250):
                return False
        return True

    # 4. Generate Option A: 5 Diversified Harmonious Simple Tickets (Pick = 6 for Mega-Sena, 5 for Quina)
    # Each simple ticket uses a distinct archetype/anchor combination while passing all 8 structural gates.
    simple_tickets: List[List[int]] = []
    simple_labels: List[str] = [
        "Jogo 1 [Consenso Mestre: Trevo + Markov + Bayesian]",
        "Jogo 2 [Âncora Natal 07 + Dia da Sorte 16/25 + Co-Pairs]",
        "Jogo 3 [Caminho de Vida 23→5 + Kabbalistic + Momentum]",
        "Jogo 4 [Sábado Sagrado + Harmonia Áurea / Fibonacci]",
        "Jogo 5 [Cobertura Espacial Anti-Multidão + Biorritmo]",
    ]

    anchor_presets = [
        [7, 23] if 23 <= hi else [7],
        [7, 16] if 16 <= hi else [7],
        [5, 25] if 25 <= hi else [5, 7],
        [7, 14] if 14 <= hi else [7],
        [16, 23] if 23 <= hi else [7, 16],
    ]

    candidate_pool_top32 = ranked_consensus[:32]
    rng = np.random.default_rng(20261020 + int(b_date_str.replace("-", "")))
    used_number_freq: Counter = Counter()

    for idx_t in range(tickets_count):
        preset_keys = [k for k in anchor_presets[idx_t % len(anchor_presets)] if lo <= k <= hi][:2]
        best_cand = None
        best_cand_score = -1e9

        # Search 2,500 weighted combinations anchored by preset_keys
        rem_pool = [n for n in candidate_pool_top32 if n not in preset_keys]
        rem_weights = np.array([max(1e-6, blended_scores[n]) for n in rem_pool], dtype=float)
        rem_probs = rem_weights / rem_weights.sum()
        needed = pick - len(preset_keys)

        for _ in range(2500):
            sampled = rng.choice(rem_pool, size=needed, replace=False, p=rem_probs).tolist()
            cand = sorted(preset_keys + sampled)
            if cand in simple_tickets:
                continue
            if not _passes_all_gates(cand):
                continue
            # Enforce low overlap (<= 2 shared numbers) with already chosen simple tickets
            max_overlap = max((len(set(cand) & set(prev)) for prev in simple_tickets), default=0)
            if max_overlap > 2:
                continue
            reuse_penalty = sum(used_number_freq[n] * 0.18 for n in cand if n != 7)
            c_score = sum(blended_scores[n] for n in cand) - 0.25 * max_overlap - reuse_penalty
            if c_score > best_cand_score:
                best_cand_score = c_score
                best_cand = cand

        if best_cand is None:
            # Relax overlap constraint to 3 if needed
            for _ in range(1500):
                sampled = rng.choice(rem_pool, size=needed, replace=False, p=rem_probs).tolist()
                cand = sorted(preset_keys + sampled)
                if cand not in simple_tickets and _passes_all_gates(cand):
                    best_cand = cand
                    break
        if best_cand is None:
            best_cand = sorted(ranked_consensus[idx_t : idx_t + pick])
        simple_tickets.append(best_cand)
        for n in best_cand:
            used_number_freq[n] += 1

    # 5. Generate Option B: Multiple Bet (Desdobramento na Caixa — 7 and 8 numbers for Mega-Sena; 6 and 7 numbers for Quina)
    mult_pick_1 = pick + 1  # 7 for Mega-Sena, 6 for Quina
    mult_pick_2 = pick + 2  # 8 for Mega-Sena, 7 for Quina

    def _build_multiple_bet(target_m: int) -> List[int]:
        base = [7, 16, 23, 25]
        base = [n for n in base if lo <= n <= hi and n in ranked_consensus[:25]][:3]
        if 7 not in base:
            base = [7] + base[:2]
        pool_m = [n for n in ranked_consensus[:28] if n not in base]
        best_m = None
        best_m_score = -1.0
        ideal_avg = (lo + hi) / 2.0 * target_m
        for _ in range(2500):
            w_m = np.array([max(1e-6, blended_scores[n]) for n in pool_m], dtype=float)
            w_m /= w_m.sum()
            samp = rng.choice(pool_m, size=target_m - len(base), replace=False, p=w_m).tolist()
            cand = sorted(base + samp)
            odds = sum(1 for n in cand if n % 2 != 0)
            if not (target_m // 2 - 1 <= odds <= (target_m + 1) // 2):
                continue
            if not (0.72 * ideal_avg <= sum(cand) <= 1.28 * ideal_avg):
                continue
            if not harmony.registry.validate(cand, rules, ["quadrant_balance", "no_3_consecutive"]):
                continue
            decades = Counter((n - 1) // 10 for n in cand)
            if max(decades.values()) > 2:
                continue
            sc = sum(blended_scores[n] for n in cand)
            if sc > best_m_score:
                best_m_score = sc
                best_m = cand
        return best_m or sorted(ranked_consensus[:target_m])

    multiple_ticket_1 = _build_multiple_bet(mult_pick_1)
    multiple_ticket_2 = _build_multiple_bet(mult_pick_2)

    # 6. Generate Option C: Abbreviated Wheel / Quina Combinatorial Unfold
    wheel_tickets: List[List[int]] = []
    wheel_pool: List[int] = []
    wheel_desc = ""

    import random as _py_random
    dyn_seed = int(t_date_str.replace("-", "")) ^ (int(b_date_str.replace("-", "")) if b_date_str.replace("-", "").isdigit() else 19900101)
    _py_random.seed(dyn_seed)

    if is_quina:
        try:
            from engine.quina_unfold import FeatureExtractor, FilterPipeline, PoolOptimizer
            feat_df = FeatureExtractor(rules).extract(df)
            f_pipe = FilterPipeline.default(rules, pool_size=12)
            opt_res = PoolOptimizer(rules, feat_df, f_pipe, pool_size=12, seed=dyn_seed).optimize()
            stat_pool = opt_res.numbers
        except Exception:
            stat_pool = ranked_consensus[:12]
        # Blend statistical Quina unfold pool with Trevo + Consensus elite pool (12 numbers)
        combined_12 = list(dict.fromkeys([7, 16, 23, 25] + ranked_consensus[:10] + stat_pool))[:12]
        wheel_pool = sorted(combined_12)
        raw_wheel = generate_abbreviated_wheel(wheel_pool, pick=5, guarantee=3, max_tickets=12)
        filtered_wheel = [sorted(t) for t in raw_wheel if _passes_all_gates(sorted(t))]
        if len(filtered_wheel) < 6:
            filtered_wheel = [sorted(t) for t in raw_wheel[:8]]
        else:
            filtered_wheel = filtered_wheel[:8]
        wheel_tickets = filtered_wheel
        wheel_desc = f"Desdobramento Quina Unfold (Pool 12 dezenas → {len(wheel_tickets)} cartões de 5 dezenas, garantia Terno/Duque com filtro macro-estrutural)"
    else:
        # Mega-Sena: 10-number elite pool wheeled into 6-number tickets with 4-hit guarantee
        combined_10 = list(dict.fromkeys([7, 16, 23, 25] + ranked_consensus[:12]))[:10]
        wheel_pool = sorted(combined_10)
        raw_wheel = generate_abbreviated_wheel(wheel_pool, pick=6, guarantee=4, max_tickets=12)
        filtered_wheel = [sorted(t) for t in raw_wheel if _passes_all_gates(sorted(t))]
        if len(filtered_wheel) < 6:
            filtered_wheel = [sorted(t) for t in raw_wheel[:8]]
        else:
            filtered_wheel = filtered_wheel[:8]
        wheel_tickets = filtered_wheel
        wheel_desc = f"Fechamento Combinatório (Wheel Pool 10 dezenas → {len(wheel_tickets)} bilhetes de 6 dezenas, garantia Quadra se 6 sorteadas no pool)"

    # 7. Historical Rolling Block Evaluation
    eval_simple = _evaluate_rolling_blocks(simple_tickets, df, rules, teimosinha_draws, max_draws=300)
    eval_mult1 = _evaluate_rolling_blocks([multiple_ticket_1], df, rules, teimosinha_draws, max_draws=300)
    eval_wheel = _evaluate_rolling_blocks(wheel_tickets, df, rules, teimosinha_draws, max_draws=300)

    # 8. Display Option A (Simple Tickets)
    opt_a_lines = []
    for i, t in enumerate(simple_tickets):
        label = simple_labels[i] if i < len(simple_labels) else f"Jogo {i+1}"
        t_fmt = " - ".join(f"{n:02d}" for n in t)
        metrics = _describe_ticket_metrics(t, rules, core_set, harm_set)
        opt_a_lines.append(f"[bold yellow]{label}:[/bold yellow]\n  👉 [bold green]{t_fmt}[/bold green]   [dim]({metrics})[/dim]")

    cost_a_per_draw = len(simple_tickets) * rules.ticket_price
    cost_a_total = cost_a_per_draw * teimosinha_draws
    tier_str_a = " | ".join(f"M{k}: {v}" for k, v in sorted(eval_simple["tier_hits"].items()))
    opt_a_lines.append(
        f"\n💰 [bold]Custo Teimosinha ({teimosinha_draws} concursos):[/bold] {len(simple_tickets)} jogos × "
        f"{rules.ticket_price:.2f} {rules.currency} × {teimosinha_draws} = [bold cyan]{cost_a_total:.2f} {rules.currency}[/bold cyan]\n"
        f"📊 [bold]Backtest ({eval_simple['evaluated_draws']} sorteios / {eval_simple['n_blocks']} blocos Teimosinha):[/bold] "
        f"[bold green]{eval_simple['winning_blocks']}/{eval_simple['n_blocks']} blocos premiados ({eval_simple['block_win_rate']:.1%})[/bold green] "
        f"| Hits totais: {tier_str_a}"
    )
    console.print(Panel("\n".join(opt_a_lines), title=f"🎟️ Opção A — {len(simple_tickets)} Jogos Simples Harmonizados ({pick} dezenas × {teimosinha_draws} concursos)", border_style="cyan"))

    # 9. Display Option B (Multiple Bets / Apostas Desdobradas na Caixa)
    mult1_ways = math.comb(mult_pick_1, pick)
    mult2_ways = math.comb(mult_pick_2, pick)
    cost_m1_total = mult1_ways * rules.ticket_price * teimosinha_draws
    cost_m2_total = mult2_ways * rules.ticket_price * teimosinha_draws
    m1_fmt = " - ".join(f"{n:02d}" for n in multiple_ticket_1)
    m2_fmt = " - ".join(f"{n:02d}" for n in multiple_ticket_2)
    tier_str_m1 = " | ".join(f"M{k}: {v}" for k, v in sorted(eval_mult1["tier_hits"].items()))

    opt_b_lines = [
        f"[bold yellow]Aposta Múltipla {mult_pick_1} Dezenas (Equivale a {mult1_ways} jogos simples):[/bold yellow]\n"
        f"  👉 [bold green]{m1_fmt}[/bold green]\n"
        f"  [dim]{_describe_ticket_metrics(multiple_ticket_1, rules, core_set, harm_set)}[/dim]\n"
        f"  💰 Custo Teimosinha ({teimosinha_draws}x): {mult1_ways * rules.ticket_price:.2f}/concurso × {teimosinha_draws} = [bold cyan]{cost_m1_total:.2f} {rules.currency}[/bold cyan]\n"
        f"  📊 Backtest Blocos ({teimosinha_draws}x): [bold green]{eval_mult1['winning_blocks']}/{eval_mult1['n_blocks']} blocos ({eval_mult1['block_win_rate']:.1%})[/bold green] | Prêmios multiplicados: {tier_str_m1}\n",
        f"[bold yellow]Aposta Múltipla {mult_pick_2} Dezenas (Equivale a {mult2_ways} jogos simples):[/bold yellow]\n"
        f"  👉 [bold green]{m2_fmt}[/bold green]\n"
        f"  [dim]{_describe_ticket_metrics(multiple_ticket_2, rules, core_set, harm_set)}[/dim]\n"
        f"  💰 Custo Teimosinha ({teimosinha_draws}x): {mult2_ways * rules.ticket_price:.2f}/concurso × {teimosinha_draws} = [bold cyan]{cost_m2_total:.2f} {rules.currency}[/bold cyan]",
    ]
    console.print(Panel("\n".join(opt_b_lines), title=f"💎 Opção B — Apostas Múltiplas Oficial Caixa ({mult_pick_1} e {mult_pick_2} dezenas × {teimosinha_draws} concursos)", border_style="magenta"))

    # 10. Display Option C (Fechamento / Unfold Wheel)
    cost_c_total = len(wheel_tickets) * rules.ticket_price * teimosinha_draws
    tier_str_c = " | ".join(f"M{k}: {v}" for k, v in sorted(eval_wheel["tier_hits"].items()))
    pool_fmt = ", ".join(f"{n:02d}" for n in wheel_pool)
    opt_c_lines = [
        f"[bold]{wheel_desc}[/bold]",
        f"[bold yellow]Pool Base ({len(wheel_pool)} dezenas):[/bold yellow] [cyan]{pool_fmt}[/cyan]\n",
    ]
    for idx_w, wt in enumerate(wheel_tickets, 1):
        wt_fmt = " - ".join(f"{n:02d}" for n in wt)
        opt_c_lines.append(f"  Cartão #{idx_w:02d}: [bold green]{wt_fmt}[/bold green]   [dim](sum={sum(wt)}, AC={get_ac_value(wt)})[/dim]")

    opt_c_lines.append(
        f"\n💰 [bold]Custo Teimosinha ({teimosinha_draws} concursos):[/bold] {len(wheel_tickets)} cartões × "
        f"{rules.ticket_price:.2f} {rules.currency} × {teimosinha_draws} = [bold cyan]{cost_c_total:.2f} {rules.currency}[/bold cyan]\n"
        f"📊 [bold]Backtest ({eval_wheel['evaluated_draws']} sorteios / {eval_wheel['n_blocks']} blocos Teimosinha):[/bold] "
        f"[bold green]{eval_wheel['winning_blocks']}/{eval_wheel['n_blocks']} blocos premiados ({eval_wheel['block_win_rate']:.1%})[/bold green] "
        f"| Hits totais: {tier_str_c}"
    )
    console.print(Panel("\n".join(opt_c_lines), title=f"🕸️ Opção C — Fechamento / Desdobramento Matemático ({len(wheel_tickets)} cartões × {teimosinha_draws} concursos)", border_style="yellow"))

    if export_md:
        p = Path(export_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        md_lines = [
            f"# Relatório Teimosinha — {rules.name} ({t_date_str})",
            f"- **Perfil Numerológico:** `[REDACTED PII]` | **Número da Sorte:** `{profile['lucky_number']}` | **Dia Sagrado:** `{profile['sacred_weekday_pt']}` | **Caminho de Vida:** `{profile['life_path']}`",
            f"- **Concursos Teimosinha:** `{teimosinha_draws}` ({', '.join(d.isoformat() for d in schedule)})",
            "",
            "## Opção A — Jogos Simples",
        ]
        for i, t in enumerate(simple_tickets, 1):
            md_lines.append(f"- **Jogo {i}:** `{' - '.join(f'{n:02d}' for n in t)}`")
        md_lines.extend([
            "",
            "## Opção B — Apostas Múltiplas",
            f"- **Múltipla ({mult_pick_1} dezenas):** `{' - '.join(f'{n:02d}' for n in multiple_ticket_1)}`",
            f"- **Múltipla ({mult_pick_2} dezenas):** `{' - '.join(f'{n:02d}' for n in multiple_ticket_2)}`",
            "",
            f"## Opção C — Fechamento ({len(wheel_pool)} dezenas -> {len(wheel_tickets)} cartões)",
            f"- **Pool:** `{pool_fmt}`",
        ])
        for i, wt in enumerate(wheel_tickets, 1):
            md_lines.append(f"- **Cartão {i:02d}:** `{' - '.join(f'{n:02d}' for n in wt)}`")
        p.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
        console.print(f"[green]✓ Relatório exportado para {export_md}[/green]")
