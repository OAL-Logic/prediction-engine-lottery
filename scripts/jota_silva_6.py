#!/usr/bin/env python3
"""
Estratégia Jota Silva - Lotofácil (13 Fixos + 6 Pares)
====================================================
Gera 6 jogos cobrindo todos os 25 números, com 13 dezenas fixas
baseadas no motor de predição do Lottery Engine.
"""

import sys
import os
from datetime import date

# Adiciona o diretório raiz ao path para importar o engine
sys.path.append(os.getcwd())

from engine.adapters.registry import registry
from engine.strategies import get_strategy
from engine.cli.utils import get_adapter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def generate_jota_silva(full_name: str, birth_date: str):
    lottery_id = "br/lotofacil"
    adapter = get_adapter(lottery_id)
    
    console.print(f"[bold cyan]Solicitando análise para {full_name}...[/bold cyan]")
    
    # Busca dados históricos
    df = adapter.fetch()
    rules = adapter.rules
    
    # Blend de estratégias: Estatística (weighted) + Pessoal (kabbalistic)
    strat_names = ["weighted", "kabbalistic"]
    personal_data = {
        "full_name": full_name,
        "birth_date": birth_date
    }
    
    combined_scores = {}
    for name in strat_names:
        try:
            strat = get_strategy(name, **personal_data)
            scores = strat.score(df, rules)
            for num, val in scores.items():
                combined_scores[num] = combined_scores.get(num, 0) + val
        except Exception as e:
            console.print(f"[yellow]Aviso: Falha ao carregar estratégia {name}: {e}[/yellow]")

    # Normaliza e ordena
    sorted_nums = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)
    
    # Garante que temos todos os 25 números no pool (caso a estratégia ignore alguns)
    all_nums = set(range(1, 26))
    remaining_in_registry = sorted(list(all_nums - set(sorted_nums)))
    sorted_nums.extend(remaining_in_registry)
    
    # 1. Definir os 13 FIXOS (Top 13)
    fixed_nums = sorted(sorted_nums[:13])
    
    # 2. Definir os 12 RESTANTES (os que sobraram)
    variable_pool = sorted_nums[13:25]
    
    # 3. Criar os 6 PARES
    # (Pode ser sequencial ou embaralhado, mas vamos manter a ordem de força)
    pairs = []
    for i in range(0, 12, 2):
        pairs.append([variable_pool[i], variable_pool[i+1]])
    
    # 4. Gerar os 6 JOGOS
    tickets = []
    for p in pairs:
        ticket = sorted(fixed_nums + p)
        tickets.append(ticket)
        
    return fixed_nums, pairs, tickets

def main():
    # Dados padrão ou via argumentos
    name = "Operator D"
    bday = "1900-01-01"
    
    if len(sys.argv) > 1:
        name = sys.argv[1]
    if len(sys.argv) > 2:
        bday = sys.argv[2]
        
    console.print(Panel.fit(
        "[bold green]🧙 Estratégia Jota Silva: 13 Fixos + 6 Pares[/bold green]\n"
        f"Usuário: {name} | Nasc: {bday}",
        border_style="green"
    ))
    
    fixed, pairs, tickets = generate_jota_silva(name, bday)
    
    # Exibir os Fixos
    console.print(f"\n[bold yellow]📌 Seus 13 Números FIXOS (Âncoras):[/bold yellow]")
    console.print(f"   {', '.join(f'{n:02d}' for n in fixed)}")
    
    # Exibir os Pares
    console.print(f"\n[bold blue]🌓 Seus 6 Pares Dinâmicos (Cobertura):[/bold blue]")
    for i, p in enumerate(pairs):
        console.print(f"   Par {chr(65+i)}: {p[0]:02d} e {p[1]:02d}")
    
    # Exibir a Tabela de Jogos
    table = Table(title="\n🎟️ Seus 6 Jogos Prontos", title_style="bold magenta")
    table.add_column("Jogo", justify="center", style="cyan")
    table.add_column("Números", justify="left", style="white")
    table.add_column("Soma", justify="center", style="dim")
    
    for i, t in enumerate(tickets):
        nums_str = " ".join(f"[bold green]{n:02d}[/bold green]" if n in fixed else f"{n:02d}" for n in t)
        table.add_row(f"#{i+1}", nums_str, str(sum(t)))
        
    console.print(table)
    console.print("\n[dim italic]Dica: Os números em [bold green]verde[/bold green] são os seus 13 fixos.[/dim italic]")
    console.print("[dim italic]Todos os 25 números da Lotofácil estão cobertos nestes 6 jogos.[/dim italic]\n")

if __name__ == "__main__":
    main()
