#!/usr/bin/env python3
"""
Estratégia Cyclical Wheel (The "Lottery Wheel" Cycle)
=====================================================
Mapeia conceitos de Trading (Wheeling Strategy) para a Lotofácil.

Conceitos Aplicados:
--------------------
1. Phase 1: Cash-Secured Put -> "Aposta em Ciclo"
   Focamos nos números que ainda não saíram no ciclo atual (estão 'vencidos').
   Eles são nossas "âncoras" (Keys).

2. Phase 2: Stock Ownership -> "Trend Following"
   Completamos o jogo com números que estão em tendência de alta (Hot numbers).

3. Phase 3: Covered Call -> "Profit/Structural Exit"
   Aplicamos filtros SRE (Circuit Breakers) para garantir que o jogo seja
   matematicamente provável (Soma, Ímpar/Par, Primos).
"""

import sys
import os
import pandas as pd
from typing import List, Set

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from engine.adapters.registry import registry
from engine.strategies import get_strategy
from engine.cli.utils import get_adapter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_current_cycle_missing(df: pd.DataFrame) -> Set[int]:
    """Identifica quais números faltam para fechar o ciclo atual da Lotofácil."""
    all_numbers = set(range(1, 26))
    seen = set()
    
    # Percorre os sorteios de trás para frente até ver todos os 25 números
    for _, row in df.iterrows():
        draw = set(row['numbers'])
        seen.update(draw)
        if len(seen) == 25:
            # Ciclo anterior fechou. O ciclo ATUAL começou no sorteio DEPOIS deste.
            break
            
    # Reinicia para o ciclo ATUAL
    current_cycle_seen = set()
    for _, row in df.iterrows():
        draw = set(row['numbers'])
        current_cycle_seen.update(draw)
        # Se ao adicionar este sorteio chegamos a 25, o ciclo ACABOU de fechar.
        # Mas queremos os que faltam para o PRÓXIMO sorteio fechar o ciclo.
        # Por simplicidade, pegamos os sorteios recentes e vemos o que falta.
        pass

    # Lógica simplificada: últimos sorteios até o ciclo resetar
    # Na Lotofácil, um ciclo dura em média 4 a 6 sorteios.
    seen_recent = set()
    for i in range(len(df)):
        draw = set(df.iloc[i]['numbers'])
        seen_recent.update(draw)
        if len(seen_recent) == 25:
            # O ciclo fechou no sorteio i. Os sorteios 0 até i-1 são o ciclo atual.
            # Se i=0, o ciclo fechou no último sorteio e um novo começou.
            if i == 0:
                return set() # Novo ciclo, nada falta ainda (ou tudo falta)
            
            # Recalcula apenas o que foi visto do sorteio 0 até i-1
            actual_seen = set()
            for j in range(i):
                actual_seen.update(set(df.iloc[j]['numbers']))
            return all_numbers - actual_seen
            
    return all_numbers - seen_recent

def apply_circuit_breakers(ticket: List[int]) -> bool:
    """Filtros de Segurança (SRE) - Rejeita jogos estatisticamente improváveis."""
    soma = sum(ticket)
    impares = len([n for n in ticket if n % 2 != 0])
    primos = len([n for n in ticket if n in [2, 3, 5, 7, 11, 13, 17, 19, 23]])
    
    # Filtro de Soma (Média 180-210 para 15 números)
    if not (160 <= soma <= 220): return False
    # Filtro de Ímpares (Média 7-9)
    if not (7 <= impares <= 9): return False
    # Filtro de Primos (Média 4-7)
    if not (4 <= primos <= 7): return False
    
    return True

def generate_cyclical_wheel(count=3):
    lottery_id = "br/lotofacil"
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    rules = adapter.rules

    # 1. Identificar números do Ciclo (Phase 1: Put/Missing)
    missing = get_current_cycle_missing(df)
    
    console.print(f"[bold blue]🌀 Análise de Ciclo:[/bold blue] Faltam {len(missing)} números para fechar: {sorted(list(missing))}")

    # 2. Obter Tendências (Phase 2: Ownership/Trend)
    # Usamos o Score do motor para completar o jogo
    strat = get_strategy("weighted")
    scores = strat.score(df, rules)
    sorted_by_score = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    # 3. Gerar Jogos com Filtros (Phase 3: Covered Call/Exit)
    final_tickets = []
    attempts = 0
    
    while len(final_tickets) < count and attempts < 1000:
        attempts += 1
        
        # Base: Números que faltam no ciclo (âncoras)
        ticket_base = list(missing)
        
        # Completa com os melhores do ranking (com um pouco de aleatoriedade/jitter)
        # para não gerar jogos idênticos
        import random
        pool = sorted_by_score[:18] # Top 18
        
        needed = 15 - len(ticket_base)
        if needed > 0:
            # Amostra dos melhores que não estão no ticket_base
            candidates = [n for n in pool if n not in ticket_base]
            if len(candidates) < needed:
                 candidates = [n for n in range(1,26) if n not in ticket_base]
            
            extra = random.sample(candidates, needed)
            ticket = sorted(ticket_base + extra)
        else:
            # Se faltarem mais de 15 pro ciclo (raro), pegamos 15 do ciclo
            ticket = sorted(random.sample(ticket_base, 15))

        # Aplica Circuit Breakers
        if apply_circuit_breakers(ticket):
            if ticket not in final_tickets:
                final_tickets.append(ticket)

    return missing, final_tickets

def main():
    console.print(Panel.fit(
        "[bold cyan]📈 Lotofácil: Cyclical Wheeling Strategy[/bold cyan]\n"
        "[dim]Mapeamento de Trading de Opções para Probabilidade de Loteria[/dim]",
        border_style="blue"
    ))

    missing, tickets = generate_cyclical_wheel(count=3)

    # Explicação Técnica
    table_exp = Table(show_header=False, border_style="dim")
    table_exp.add_row("Phase 1 (CSP)", f"Números do Ciclo: {len(missing)} dezenas 'vencidas' como âncoras.")
    table_exp.add_row("Phase 2 (Trend)", "Números de tendência (Hot) completando o volume.")
    table_exp.add_row("Phase 3 (SRE)", "Circuit Breakers aplicados (Soma, Ímpar, Primos).")
    console.print(table_exp)

    # Exibição dos Jogos
    table = Table(title="\n🚀 Seus 3 Jogos de Ciclo Otimizados", title_style="bold yellow")
    table.add_column("Portfolio", justify="center", style="cyan")
    table.add_column("Números", justify="left", style="white")
    table.add_column("Soma", justify="center", style="dim")
    
    # Busca os top números para colorir como 'Trend' (Hot)
    adapter = get_adapter("br/lotofacil")
    df = adapter.fetch()
    strat = get_strategy("weighted")
    scores = strat.score(df, adapter.rules)
    hot_numbers = set(sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:10])

    for i, t in enumerate(tickets):
        formatted_nums = []
        for n in t:
            if n in missing:
                formatted_nums.append(f"[bold green]{n:02d}[/bold green]")
            elif n in hot_numbers:
                formatted_nums.append(f"[bold cyan]{n:02d}[/bold cyan]")
            else:
                formatted_nums.append(f"{n:02d}")
        
        nums_str = " ".join(formatted_nums)
        table.add_row(f"Game {i+1}", nums_str, str(sum(t)))
        
    console.print(table)
    console.print("\n[dim]Legenda: [bold green]Verde[/bold green] = Dezenas do Ciclo | [bold cyan]Ciano[/bold cyan] = Dezenas de Tendência (Hot) | Branco = Complemento.[/dim]")

if __name__ == "__main__":
    main()
