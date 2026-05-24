#!/usr/bin/env python3
"""
Estratégia Cyclical Wheel (The "Lottery Wheel" Cycle) - MEGA-SENA
================================================================
Mapeia conceitos de Trading (Wheeling Strategy) para a Mega-Sena.
"""

import sys
import os
import pandas as pd
import random
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

def get_current_cycle_missing(df: pd.DataFrame, pool_size: int) -> Set[int]:
    """Identifica quais números faltam para fechar o ciclo atual."""
    all_numbers = set(range(1, pool_size + 1))
    seen_recent = set()
    
    # Na Mega-Sena o ciclo é muito longo (60 números, 6 por sorteio).
    # Olhamos os últimos sorteios até que o ciclo "quase" feche ou usamos uma janela de recência.
    for i in range(len(df)):
        draw = set(df.iloc[i]['numbers'])
        seen_recent.update(draw)
        if len(seen_recent) >= pool_size * 0.9: # 90% do ciclo
             break
             
    return all_numbers - seen_recent

def apply_circuit_breakers(ticket: List[int]) -> bool:
    """Filtros de Segurança (SRE) para Mega-Sena."""
    soma = sum(ticket)
    impares = len([n for n in ticket if n % 2 != 0])
    
    # Filtro de Soma para Mega-Sena (6 números, média ~183)
    if not (100 <= soma <= 260): return False
    # Filtro de Ímpares (Média 2-4)
    if not (2 <= impares <= 4): return False
    
    return True

def generate_mega_cycle(count=3):
    lottery_id = "br/mega-sena"
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    rules = adapter.rules

    # 1. Ciclo (Phase 1)
    missing = get_current_cycle_missing(df, rules.number_range[1])
    
    # 2. Tendências (Phase 2)
    strat = get_strategy("weighted")
    scores = strat.score(df, rules)
    sorted_by_score = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    hot_numbers = set(sorted_by_score[:10])

    # 3. Gerar Jogos
    final_tickets = []
    attempts = 0
    
    while len(final_tickets) < count and attempts < 1000:
        attempts += 1
        
        # Na Mega, como faltam muitos pro ciclo, pegamos apenas alguns 'missing' como âncoras
        num_anchors = min(len(missing), 2)
        ticket_base = random.sample(list(missing), num_anchors) if missing else []
        
        needed = 6 - len(ticket_base)
        pool = sorted_by_score[:15]
        candidates = [n for n in pool if n not in ticket_base]
        
        extra = random.sample(candidates, needed)
        ticket = sorted(ticket_base + extra)

        if apply_circuit_breakers(ticket):
            if ticket not in final_tickets:
                final_tickets.append(ticket)

    return missing, hot_numbers, final_tickets

def main():
    console.print(Panel.fit(
        "[bold green]🎰 Mega-Sena: Cyclical Wheeling Strategy[/bold green]\n"
        "[dim]Mapeamento de Trading de Opções para Mega-Sena[/dim]",
        border_style="green"
    ))

    missing, hot, tickets = generate_mega_cycle(count=3)

    # Exibição
    table = Table(title="\n🚀 Seus 3 Jogos de Mega-Sena (Ciclo + Tendência)", title_style="bold yellow")
    table.add_column("Portfólio", justify="center", style="cyan")
    table.add_column("Números", justify="left", style="white")
    table.add_column("Soma", justify="center", style="dim")
    
    for i, t in enumerate(tickets):
        formatted = []
        for n in t:
            if n in missing:
                formatted.append(f"[bold green]{n:02d}[/bold green]")
            elif n in hot:
                formatted.append(f"[bold cyan]{n:02d}[/bold cyan]")
            else:
                formatted.append(f"{n:02d}")
        table.add_row(f"Mega {i+1}", " ".join(formatted), str(sum(t)))
        
    console.print(table)
    console.print("\n[dim]Legenda: [bold green]Verde[/bold green] = Dezenas de Ciclo (Atrasadas) | [bold cyan]Ciano[/bold cyan] = Tendência (Quentes).[/dim]\n")

if __name__ == "__main__":
    main()
