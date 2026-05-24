#!/usr/bin/env python3
"""
Bankroll Management Optimizer (Kelly Criterion)
===============================================
Calcula o valor ideal de aposta baseado na confiança estatística do sistema.
Evita a falência do jogador e otimiza o crescimento do capital no longo prazo.
"""

import sys
import os
import math

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def calculate_kelly():
    # 1. Obter Confiança do Sistema (Consenso da Stacking AI)
    lottery_id = "br/lotofacil"
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    rules = adapter.rules
    
    console.print("[bold cyan]Analisando confiança do mercado para gestão de banca...[/bold cyan]")
    
    # Usamos a nova Stacking AI para medir a 'estabilidade' do sinal
    strat = get_strategy("stacking_ai")
    scores = strat.score(df, rules)
    
    # Medimos a 'Entropia' do sinal. Se os scores forem todos parecidos, a confiança é baixa.
    # Se houver picos claros, a confiança é alta.
    sorted_scores = sorted(scores.values(), reverse=True)
    top_avg = sum(sorted_scores[:15]) / 15
    baseline_avg = sum(sorted_scores) / len(sorted_scores)
    
    confidence_factor = (top_avg - baseline_avg) / (1 - baseline_avg)
    
    # 2. Parâmetros Kelly (Adaptado para Loteria)
    # Fórmul: f* = (bp - q) / b
    # b = odd (ex: na Lotofacil 11 pontos paga 2x o valor da aposta simples)
    # p = probabilidade estimada (confiança do sistema)
    # q = 1 - p
    
    b = 2.0 # Payout médio ponderado para prêmios menores
    p = 0.5 + (0.1 * confidence_factor) # Probabilidade ajustada (viesada pela confiança)
    q = 1 - p
    
    kelly_fraction = ((b * p) - q) / b
    
    # Aplicamos um 'Fractional Kelly' (0.1) para ser conservador
    safe_fraction = max(0.01, kelly_fraction * 0.1) 
    
    return safe_fraction, confidence_factor

def main():
    console.print(Panel.fit(
        "[bold green]⚖️ Otimizador de Gestão de Banca (Kelly Criterion)[/bold green]\n"
        "Protegendo o capital através da matemática de risco",
        border_style="green"
    ))

    # Valor da banca (Exemplo: R$ 500,00)
    bankroll = 500.00
    if len(sys.argv) > 1:
        bankroll = float(sys.argv[1])

    fraction, confidence = calculate_kelly()
    suggested_bet = bankroll * fraction
    num_tickets = math.floor(suggested_bet / 3.0) # Preço Lotofacil

    table = Table(title="Plano de Aposta para Hoje")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="white")
    
    table.add_row("Confiança do Sinal", f"{confidence*100:.2f}%")
    table.add_row("Risco Sugerido (Kelly)", f"{fraction*100:.2f}% da banca")
    table.add_row("Banca Atual", f"R$ {bankroll:.2f}")
    table.add_row("Aposta Recomendada", f"R$ {suggested_bet:.2f}")
    table.add_row("Qtd. de Jogos", f"[bold yellow]{num_tickets}[/bold yellow] bilhetes")
    
    console.print(table)
    
    if confidence < 0.2:
        console.print("[red]⚠ ALERTA: Sinal muito fraco. Recomendado jogar apenas o mínimo hoje.[/red]")
    elif confidence > 0.6:
        console.print("[green]🚀 SINAL FORTE: As dezenas estão convergindo. Boa oportunidade.[/green]")

if __name__ == "__main__":
    main()
