#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geração de jogo para teimosinha: Mega-Sena (x12) e Lotofácil (x24).

Este script:
  1. Carrega os dados históricos mais recentes do DuckDB.
  2. Executa múltiplas estratégias do CLI e avalia cada candidato.
  3. Roda backtest em janela recente para medir desempenho.
  4. Calcula frequências, ciclos, lacunas (gaps), números quentes/frios.
  5. Aplica filtros estruturais (soma, paridade, dezenas, colunas, sequências).
  6. Usa votação ponderada entre estratégias para escolher o jogo final.
  7. Exporta relatório Markdown com justificativa e ressalvas.

Uso:
  cd lottery
  PYTHONPATH=. python scripts/gerar_teimosinha.py
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Saída desbufferizada para logs em tempo real
sys.stdout.reconfigure(line_buffering=True)
from engine.adapters import DrawRules
from engine.adapters.registry import registry
from engine.cli.utils import get_adapter
from engine.modules.storage import storage
from engine.strategies import get_strategy

# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------

REPORT_PATH = Path("reports/teimosinha_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".md")
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

MEGA_STRATEGIES = [
    "weighted",
    "markov",
    "bayesian",
    "monte_carlo",
    "spectral",
    "cycle",
    "crowd_avoidance",
    "streak",
    "advanced",
    "structural",
]

LOTOFACIL_STRATEGIES = [
    "weighted",
    "markov",
    "bayesian",
    "crowd_avoidance",
    "structural",
    "positional",
]

# Janela de backtest (últimos N sorteios para testar as estratégias)
BACKTEST_WINDOW = 20

# Pesos para o score final de um bilhete
WEIGHTS = {
    "backtest_hits": 0.25,        # acertos históricos recentes
    "strategy_votes": 0.25,       # quantas estratégias concordam
    "freq_score": 0.20,           # frequência histórica dos números
    "gap_score": 0.15,            # números em ciclos favoráveis
    "structural": 0.15,           # filtros estruturais (soma, paridade, etc.)
}

# ---------------------------------------------------------------------------
# Carregamento de dados
# ---------------------------------------------------------------------------


def load_data(lottery_id: str) -> pd.DataFrame:
    """Carrega dados históricos do storage local."""
    df = storage.load_draws(lottery_id)
    if df.empty:
        raise RuntimeError(f"Sem dados para {lottery_id}. Rode 'lottery fetch {lottery_id}' primeiro.")
    df["numbers"] = df["numbers"].apply(lambda x: [int(n) for n in x])
    return df


# ---------------------------------------------------------------------------
# Estratégias e candidatos
# ---------------------------------------------------------------------------


def get_rules(lottery_id: str) -> DrawRules:
    """Obtém as regras do jogo via adapter."""
    adapter = get_adapter(lottery_id)
    return adapter.rules


def generate_candidates(df: pd.DataFrame, rules: DrawRules, strategies: list[str], count: int = 2) -> dict[str, list]:
    """
    Gera candidatos para cada estratégia.
    Usa temperatura baixa (0.3) para maior determinismo e alta (1.0) para variedade.
    """
    candidates: dict[str, list] = defaultdict(list)
    for name in strategies:
        try:
            strat = get_strategy(name)
            for temp in [0.3, 1.0]:
                result = strat.suggest(df, rules, count=count, temperature=temp)
                for ticket in result.tickets:
                    ticket_set = tuple(sorted(ticket))
                    if ticket_set not in [tuple(sorted(t)) for t in candidates[name]]:
                        candidates[name].append(list(ticket_set))
        except Exception as exc:
            print(f"  ⚠ Estratégia {name} falhou: {exc}")
    return dict(candidates)


# ---------------------------------------------------------------------------
# Métricas estatísticas
# ---------------------------------------------------------------------------


def frequency_analysis(df: pd.DataFrame, rules: DrawRules, last_n: int = 100) -> dict[int, dict]:
    """Calcula frequência, atraso e gap médio por número na janela recente."""
    lo, hi = rules.number_range
    recent = df.tail(last_n)
    flat = [n for draw in recent["numbers"] for n in draw]
    total = len(recent)
    freq = Counter(flat)

    # Última aparição (em sorteios atrás)
    last_seen = {n: total for n in range(lo, hi + 1)}
    for offset, draw in enumerate(recent["numbers"].iloc[::-1]):
        for n in draw:
            if last_seen[n] == total:
                last_seen[n] = offset

    # Gap médio histórico completo
    all_flat = [n for draw in df["numbers"] for n in draw]
    all_total = len(df)
    hist_freq = Counter(all_flat)
    gap_mean = {
        n: all_total / max(hist_freq.get(n, 1), 1) for n in range(lo, hi + 1)
    }

    stats = {}
    for n in range(lo, hi + 1):
        stats[n] = {
            "freq": freq.get(n, 0),
            "freq_pct": freq.get(n, 0) / total * 100,
            "last_seen": last_seen[n],
            "mean_gap": gap_mean[n],
            "overdue_ratio": last_seen[n] / max(gap_mean[n], 1),
        }
    return stats


def pair_cooccurrence(df: pd.DataFrame, rules: DrawRules, top_n: int = 20) -> list[tuple]:
    """Retorna os pares de números que mais aparecem juntos."""
    pair_counts = Counter()
    for draw in df["numbers"]:
        nums = sorted(draw)
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pair_counts[(nums[i], nums[j])] += 1
    return pair_counts.most_common(top_n)


def hot_numbers(freq_stats: dict[int, dict], top_n: int = 10) -> list[int]:
    """Números mais frequentes na janela recente."""
    return [n for n, _ in sorted(freq_stats.items(), key=lambda x: x[1]["freq"], reverse=True)[:top_n]]


def overdue_numbers(freq_stats: dict[int, dict], top_n: int = 10) -> list[int]:
    """Números cujo atraso atual supera o gap médio."""
    scored = [(n, s["overdue_ratio"]) for n, s in freq_stats.items() if s["overdue_ratio"] > 1.0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [n for n, _ in scored[:top_n]]


# ---------------------------------------------------------------------------
# Filtros estruturais
# ---------------------------------------------------------------------------


def sum_range_score(ticket: list[int], rules: DrawRules) -> float:
    """Avalia se a soma está próxima da média histórica esperada."""
    lo, hi = rules.number_range
    pick = len(ticket)
    expected_mean = (lo + hi) / 2
    expected_sum = expected_mean * pick
    actual_sum = sum(ticket)
    std = math.sqrt((hi - lo + 1) ** 2 / 12) * math.sqrt(pick)
    z = abs(actual_sum - expected_sum) / std
    return max(0.0, 1.0 - z / 2.0)


def parity_balance_score(ticket: list[int]) -> float:
    """Avalia equilíbrio entre pares e ímpares."""
    n_even = sum(1 for n in ticket if n % 2 == 0)
    n_odd = len(ticket) - n_even
    ideal = len(ticket) / 2
    return max(0.0, 1.0 - abs(n_even - ideal) / ideal)


def decade_balance_score(ticket: list[int], rules: DrawRules) -> float:
    """Avalia distribuição por dezenas (1-10, 11-20, ...)."""
    lo, hi = rules.number_range
    decades = defaultdict(int)
    for n in ticket:
        decades[(n - 1) // 10] += 1
    n_decades = math.ceil(hi / 10)
    covered = sum(1 for v in decades.values() if v > 0)
    return covered / n_decades


def consecutive_score(ticket: list[int]) -> float:
    """Penaliza muitos números consecutivos (mais de 3 seguidos é raro)."""
    consecutive = 0
    for i in range(len(ticket) - 1):
        if ticket[i] + 1 == ticket[i + 1]:
            consecutive += 1
    # Até 2 pares consecutivos é normal; mais que isso penaliza
    return max(0.0, 1.0 - consecutive / 3.0)


def column_balance_score(ticket: list[int]) -> float:
    """Avalia distribuição pelas colunas finais (0-9)."""
    cols = defaultdict(int)
    for n in ticket:
        cols[n % 10] += 1
    # Entropia normalizada
    counts = list(cols.values())
    total = sum(counts)
    if total == 0:
        return 0.0
    entropy = -sum((c / total) * math.log(c / total + 1e-12) for c in counts)
    max_entropy = math.log(len(ticket))
    return entropy / max_entropy if max_entropy > 0 else 0.0


def structural_score(ticket: list[int], rules: DrawRules) -> float:
    """Combina vários filtros estruturais."""
    scores = [
        sum_range_score(ticket, rules),
        parity_balance_score(ticket),
        decade_balance_score(ticket, rules),
        consecutive_score(ticket),
        column_balance_score(ticket),
    ]
    return statistics.mean(scores)


# ---------------------------------------------------------------------------
# Backtest
# ---------------------------------------------------------------------------


def backtest_strategy(df: pd.DataFrame, rules: DrawRules, strategy_name: str, window: int = BACKTEST_WINDOW) -> dict[str, Any]:
    """
    Testa a estratégia em janela deslizante: para cada sorteio nos últimos `window`,
    treina com os dados anteriores e verifica quantos acertos teria.
    """
    if len(df) < window + 10:
        return {"strategy": strategy_name, "mean_hits": 0.0, "details": []}

    try:
        strat = get_strategy(strategy_name)
    except Exception as exc:
        return {"strategy": strategy_name, "mean_hits": 0.0, "error": str(exc), "details": []}

    hits_list = []
    details = []
    for i in range(window):
        if i % 10 == 0 and i > 0:
            print(f"    backtest {strategy_name}: {i}/{window}")
        idx = len(df) - window + i
        train_df = df.iloc[:idx]
        target = set(df.iloc[idx]["numbers"])
        try:
            result = strat.suggest(train_df, rules, count=1, temperature=0.3)
            predicted = set(result.tickets[0])
            hits = len(predicted & target)
            hits_list.append(hits)
            details.append({
                "draw_id": int(df.iloc[idx]["draw_id"]),
                "predicted": sorted(predicted),
                "actual": sorted(target),
                "hits": hits,
            })
        except Exception:
            continue

    if not hits_list:
        return {"strategy": strategy_name, "mean_hits": 0.0, "details": []}

    return {
        "strategy": strategy_name,
        "mean_hits": statistics.mean(hits_list),
        "median_hits": statistics.median(hits_list),
        "max_hits": max(hits_list),
        "hits_4plus": sum(1 for h in hits_list if h >= 4),
        "details": details,
    }


def evaluate_candidate(
    ticket: list[int],
    candidates_by_strategy: dict[str, list],
    backtest_results: dict[str, dict],
    freq_stats: dict[int, dict],
    rules: DrawRules,
) -> dict[str, float]:
    """Calcula score composto para um bilhete candidato."""
    ticket_set = set(ticket)

    # 1. Votos das estratégias
    votes = 0
    for strategy_name, tickets in candidates_by_strategy.items():
        for t in tickets:
            overlap = len(set(t) & ticket_set)
            votes += overlap / len(ticket)
    strategy_votes = min(1.0, votes / max(len(candidates_by_strategy), 1))

    # 2. Score de backtest (média ponderada das estratégias que votaram)
    bt_scores = []
    for strategy_name in candidates_by_strategy:
        bt = backtest_results.get(strategy_name, {})
        mean_hits = bt.get("mean_hits", 0)
        bt_scores.append(mean_hits / rules.pick_count)
    backtest_score = statistics.mean(bt_scores) if bt_scores else 0.0

    # 3. Score de frequência
    freq_score = statistics.mean([freq_stats[n]["freq_pct"] / 100 for n in ticket])

    # 4. Score de lacunas (preferência por números próximos ao gap médio ou levemente atrasados)
    gap_scores = []
    for n in ticket:
        ratio = freq_stats[n]["overdue_ratio"]
        # 0.8 a 1.5 é a "zona de interesse"
        gap_scores.append(1.0 - min(abs(ratio - 1.1), 1.0))
    gap_score = statistics.mean(gap_scores)

    # 5. Estrutural
    struct = structural_score(ticket, rules)

    final = (
        WEIGHTS["strategy_votes"] * strategy_votes
        + WEIGHTS["backtest_hits"] * backtest_score
        + WEIGHTS["freq_score"] * freq_score
        + WEIGHTS["gap_score"] * gap_score
        + WEIGHTS["structural"] * struct
    )

    return {
        "final": final,
        "strategy_votes": strategy_votes,
        "backtest_score": backtest_score,
        "freq_score": freq_score,
        "gap_score": gap_score,
        "structural": struct,
    }


# ---------------------------------------------------------------------------
# Geração do jogo final
# ---------------------------------------------------------------------------


def build_final_ticket(
    lottery_id: str,
    strategies: list[str],
    top_pool_size: int = 20,
) -> tuple[list[int], dict[str, Any]]:
    """Executa todo o pipeline e retorna o melhor bilhete + metadados."""
    print(f"\n=== {lottery_id.upper()} ===")
    df = load_data(lottery_id)
    rules = get_rules(lottery_id)
    print(f"Dados: {len(df)} sorteios ({df['draw_date'].min()} a {df['draw_date'].max()})")

    # 1. Candidatos por estratégia
    print("Gerando candidatos...")
    candidates = generate_candidates(df, rules, strategies, count=3)
    print(f"  Estratégias com candidatos: {sum(1 for v in candidates.values() if v)}")

    # 2. Backtest
    print("Rodando backtest...")
    backtest_results = {}
    for name in strategies:
        res = backtest_strategy(df, rules, name)
        if res.get("mean_hits", 0) > 0 or not res.get("error"):
            backtest_results[name] = res
    for name, res in backtest_results.items():
        print(f"  {name}: média {res['mean_hits']:.2f} acertos | max {res.get('max_hits', 0)}")

    # 3. Análise de frequência
    print("Analisando frequências e ciclos...")
    freq_stats = frequency_analysis(df, rules, last_n=100)
    hot = hot_numbers(freq_stats, top_n=10)
    overdue = overdue_numbers(freq_stats, top_n=10)
    pairs = pair_cooccurrence(df, rules, top_n=15)

    # 4. Constrói pool de números promissores
    # Pega os top-scored de cada estratégia e une com hot/overdue
    scored_counter = Counter()
    for name, tickets in candidates.items():
        for ticket in tickets:
            for n in ticket:
                scored_counter[n] += 1
    for n in hot:
        scored_counter[n] += 0.5
    for n in overdue:
        scored_counter[n] += 0.5

    top_pool = [n for n, _ in scored_counter.most_common(top_pool_size)]
    print(f"Pool selecionado ({len(top_pool)} números): {sorted(top_pool)}")

    # 5. Gera combinações dentro do pool e avalia
    print("Otimizando bilhete final...")
    best_ticket = None
    best_score = -1.0
    best_metrics = None

    # Gera amostras do pool respeitando pick_count
    iterations = 2000 if rules.pick_count <= 6 else 500
    for i in range(iterations):
        if i % 500 == 0 and i > 0:
            print(f"  ...iteração {i}/{iterations}")
        ticket = sorted(random.sample(top_pool, rules.pick_count))
        metrics = evaluate_candidate(ticket, candidates, backtest_results, freq_stats, rules)
        if metrics["final"] > best_score:
            best_score = metrics["final"]
            best_ticket = ticket
            best_metrics = metrics

    # 6. Refinamento local: tenta trocar um número por vez
    if best_ticket:
        improved = True
        while improved:
            improved = False
            current_score = best_score
            for i, old in enumerate(best_ticket):
                for new in range(rules.number_range[0], rules.number_range[1] + 1):
                    if new in best_ticket:
                        continue
                    candidate = best_ticket[:]
                    candidate[i] = new
                    candidate = sorted(candidate)
                    metrics = evaluate_candidate(candidate, candidates, backtest_results, freq_stats, rules)
                    if metrics["final"] > current_score:
                        best_ticket = candidate
                        best_score = metrics["final"]
                        best_metrics = metrics
                        current_score = best_score
                        improved = True
                        break
                if improved:
                    break

    metadata = {
        "rules": rules,
        "df": df,
        "candidates": candidates,
        "backtest": backtest_results,
        "freq_stats": freq_stats,
        "hot": hot,
        "overdue": overdue,
        "pairs": pairs,
        "metrics": best_metrics,
        "top_pool": top_pool,
    }
    return best_ticket, metadata


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def _fmt_list(lst: list[int]) -> str:
    return ", ".join(f"{n:02d}" for n in lst)


def generate_report(
    mega_ticket: list[int],
    mega_meta: dict[str, Any],
    loto_ticket: list[int],
    loto_meta: dict[str, Any],
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "---",
        "type: prediction-report",
        "subtype: teimosinha",
        f"date: {now}",
        "tags: [lottery, teimosinha, mega-sena, lotofacil, prediction-engine]",
        "---",
        "",
        "# Relatório de Jogo para Teimosinha",
        f"\nGerado em: **{now}**",
        "\n> ⚠️ **Aviso importante:** Loterias são eventos aleatórios e independentes. Este relatório usa análise estatística, backtest e filtros estruturais para escolher jogos com maior alinhamento a padrões históricos, mas **não há garantia de prêmio**. Jogue com responsabilidade.",
        "",
        "## Resumo dos Jogos Escolhidos",
        "",
        "| Loteria | Números | Teimosinha |",
        "|---------|---------|------------|",
        f"| Mega-Sena | {_fmt_list(mega_ticket)} | 12 sorteios consecutivos |",
        f"| Lotofácil | {_fmt_list(loto_ticket)} | 24 sorteios consecutivos |",
        "",
        "---",
        "",
        "## 1. Mega-Sena",
        "",
        f"- **Números:** {_fmt_list(mega_ticket)}",
        f"- **Soma:** {sum(mega_ticket)}",
        f"- **Média histórica esperada:** {((mega_meta['rules'].number_range[0] + mega_meta['rules'].number_range[1]) / 2) * mega_meta['rules'].pick_count:.1f}",
        f"- **Score composto:** {mega_meta['metrics']['final']:.4f}",
        "",
        "### Estratégias testadas e backtest",
        "",
        "| Estratégia | Média de acertos | Máx. acertos | Sorteios com 4+ |",
        "|------------|------------------|--------------|-----------------|",
    ]
    for name, res in mega_meta["backtest"].items():
        lines.append(
            f"| {name} | {res['mean_hits']:.2f} | {res.get('max_hits', 0)} | {res.get('hits_4plus', 0)} |"
        )

    lines += [
        "",
        "### Contribuição do score",
        "",
        "| Componente | Valor |",
        "|------------|-------|",
        f"| Votos das estratégias | {mega_meta['metrics']['strategy_votes']:.4f} |",
        f"| Backtest | {mega_meta['metrics']['backtest_score']:.4f} |",
        f"| Frequência | {mega_meta['metrics']['freq_score']:.4f} |",
        f"| Lacunas/ciclos | {mega_meta['metrics']['gap_score']:.4f} |",
        f"| Filtros estruturais | {mega_meta['metrics']['structural']:.4f} |",
        "",
        f"### Números quentes (últimos 100 sorteios): {_fmt_list(mega_meta['hot'][:10])}",
        f"### Números atrasados: {_fmt_list(mega_meta['overdue'][:10])}",
        "",
        "### Pares mais frequentes",
        "",
        "| Par | Ocorrências |",
        "|-----|-------------|",
    ]
    for (a, b), count in mega_meta["pairs"][:10]:
        lines.append(f"| {a:02d}-{b:02d} | {count} |")

    lines += [
        "",
        "---",
        "",
        "## 2. Lotofácil",
        "",
        f"- **Números:** {_fmt_list(loto_ticket)}",
        f"- **Soma:** {sum(loto_ticket)}",
        f"- **Média histórica esperada:** {((loto_meta['rules'].number_range[0] + loto_meta['rules'].number_range[1]) / 2) * loto_meta['rules'].pick_count:.1f}",
        f"- **Score composto:** {loto_meta['metrics']['final']:.4f}",
        "",
        "### Estratégias testadas e backtest",
        "",
        "| Estratégia | Média de acertos | Máx. acertos | Sorteios com 11+ |",
        "|------------|------------------|--------------|------------------|",
    ]
    for name, res in loto_meta["backtest"].items():
        lines.append(
            f"| {name} | {res['mean_hits']:.2f} | {res.get('max_hits', 0)} | {res.get('hits_4plus', 0)} |"
        )

    lines += [
        "",
        "### Contribuição do score",
        "",
        "| Componente | Valor |",
        "|------------|-------|",
        f"| Votos das estratégias | {loto_meta['metrics']['strategy_votes']:.4f} |",
        f"| Backtest | {loto_meta['metrics']['backtest_score']:.4f} |",
        f"| Frequência | {loto_meta['metrics']['freq_score']:.4f} |",
        f"| Lacunas/ciclos | {loto_meta['metrics']['gap_score']:.4f} |",
        f"| Filtros estruturais | {loto_meta['metrics']['structural']:.4f} |",
        "",
        f"### Números quentes (últimos 100 sorteios): {_fmt_list(loto_meta['hot'][:10])}",
        f"### Números atrasados: {_fmt_list(loto_meta['overdue'][:10])}",
        "",
        "### Pares mais frequentes",
        "",
        "| Par | Ocorrências |",
        "|-----|-------------|",
    ]
    for (a, b), count in loto_meta["pairs"][:10]:
        lines.append(f"| {a:02d}-{b:02d} | {count} |")

    lines += [
        "",
        "---",
        "",
        "## 3. Metodologia",
        "",
        "1. **Dados históricos:** carregados do banco DuckDB local (`data/lottery.db`), com os sorteios mais recentes buscados da Caixa.",
        "2. **Estratégias:** cada estratégia do `lottery` CLI foi executada para gerar múltiplos candidatos, com temperaturas determinística (0.3) e exploratória (1.0).",
        "3. **Backtest:** para cada estratégia, simulou-se prever os últimos 50 sorteios usando apenas os dados anteriores, medindo acertos médios e máximos.",
        "4. **Frequências e ciclos:** calculou-se frequência, atraso e gap médio de cada número nos últimos 100 sorteios e no histórico completo.",
        "5. **Filtros estruturais:** cada candidato foi avaliado por soma, paridade, dezenas, colunas finais e consecutividade.",
        "6. **Score composto:** combinou-se votos das estratégias, desempenho no backtest, frequência, lacunas e harmonia estrutural com pesos fixos.",
        "7. **Otimização:** selecionou-se o melhor bilhete por loteria e refinou-se trocando um número por vez para maximizar o score.",
        "",
        "## 4. Ressalvas",
        "",
        "- Nenhum modelo consegue prever sorteios verdadeiramente aleatórios; o que se busca é **evitar combinações anômalas** e alinhar o jogo a padrões históricos estáveis.",
        "- 'Teimosinha' não altera a probabilidade por sorteio, apenas mantém a mesma aposta por vários sorteios consecutivos.",
        "- Resultados passados (backtest) não garantem resultados futuros.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    mega_ticket, mega_meta = build_final_ticket("br/mega-sena", MEGA_STRATEGIES)
    loto_ticket, loto_meta = build_final_ticket("br/lotofacil", LOTOFACIL_STRATEGIES)

    report = generate_report(mega_ticket, mega_meta, loto_ticket, loto_meta)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print("\n" + "=" * 60)
    print("JOGOS FINAIS")
    print("=" * 60)
    print(f"Mega-Sena (6 números): {_fmt_list(mega_ticket)}")
    print(f"Lotofácil (15 números): {_fmt_list(loto_ticket)}")
    print("=" * 60)
    print(f"\nRelatório salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()
