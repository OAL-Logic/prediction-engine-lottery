#!/usr/bin/env python3
"""
Interactive 3D Mega-Sena Explorer
=================================
Gera um Dashboard interativo em HTML/Plotly para análise de dezenas.
Permite rotacionar, dar zoom e filtrar dezenas por categorias.
"""

import sys
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy
from rich.console import Console

console = Console()

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

def generate_interactive_3d():
    lottery_id = "br/mega-sena"
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    rules = adapter.rules
    
    console.print("[bold cyan]Construindo motor de visualização interativa...[/bold cyan]")
    
    # 1. Extração de Dados (Mesma lógica do 3D estático)
    strat_names = ["weighted", "pattern", "monte_carlo", "spectral"]
    consensus_counts = {i: 0 for i in range(1, 61)}
    final_scores = {i: 0.0 for i in range(1, 61)}
    
    for name in strat_names:
        strat = get_strategy(name)
        scores = strat.score(df, rules)
        top_15 = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:15]
        for num in top_15:
            consensus_counts[num] += 1
        for num, val in scores.items():
            final_scores[num] += val

    history_len = len(df)
    freqs = {i: 0 for i in range(1, 61)}
    last_seen = {i: 0 for i in range(1, 61)} # Reset correctly
    
    # Calculate Delay from latest draw
    latest_draw_idx = 0
    for i in range(1, 61):
        found = False
        for idx, row in df.iterrows():
            if i in row['numbers']:
                freqs[i] += 1
                if not found:
                    last_seen[i] = idx # index is draws ago
                    found = True
        if not found:
            last_seen[i] = history_len

    # 2. Categorização para Filtros
    categories = {i: "Comum" for i in range(1, 61)}
    perfect_game = [6, 15, 25, 27, 32, 55]
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55]
    
    for i in range(1, 61):
        if i in perfect_game: categories[i] = "Elite (Bilhete Sugerido)"
        elif is_prime(i): categories[i] = "Primos"
        elif i in fibonacci: categories[i] = "Fibonacci"
        elif consensus_counts[i] >= 3: categories[i] = "Alto Consenso IA"

    # 3. Criar Gráfico com Plotly
    fig = go.Figure()

    # Adicionar traces por categoria para permitir ligar/desligar na legenda
    cat_list = ["Elite (Bilhete Sugerido)", "Alto Consenso IA", "Primos", "Fibonacci", "Comum"]
    colors = {"Elite (Bilhete Sugerido)": "red", "Alto Consenso IA": "gold", "Primos": "cyan", "Fibonacci": "magenta", "Comum": "gray"}

    for cat in cat_list:
        mask = [categories[i] == cat for i in range(1, 61)]
        indices = [i for i in range(1, 61) if categories[i] == cat]
        
        fig.add_trace(go.Scatter3d(
            x=indices,
            y=[freqs[i]/history_len*100 for i in indices],
            z=[last_seen[i] for i in indices],
            mode='markers+text',
            name=cat,
            text=[f"#{i}" for i in indices],
            marker=dict(
                size=[10 + consensus_counts[i]*8 for i in indices],
                color=colors[cat],
                opacity=0.8,
                line=dict(width=1, color='white')
            ),
            hovertemplate=(
                "<b>Dezena %{x}</b><br>" +
                "Frequência: %{y:.2f}%<br>" +
                "Atraso: %{z} sorteios<br>" +
                f"Categoria: {cat}<br>" +
                "<extra></extra>"
            )
        ))

    # Layout
    fig.update_layout(
        title="Mega-Sena 3D Interactive Explorer",
        scene=dict(
            xaxis_title='Dezena (1-60)',
            yaxis_title='Frequência (%)',
            zaxis_title='Atraso (Ciclo)',
            bgcolor="rgb(10, 10, 20)"
        ),
        template="plotly_dark",
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    output_path = "data/mega_sena_3d_interactive.html"
    fig.write_html(output_path)
    
    console.print(f"\n[bold green]✓ Dashboard Interativo gerado![/bold green]")
    console.print(f"Abra este arquivo no seu navegador: [yellow]{output_path}[/yellow]")
    console.print("\n[bold]Recursos Interativos:[/bold]")
    console.print("1. [bold]Legenda[/]: Clique nos nomes (ex: 'Primos') para ativar/desativar dezenas no mapa.")
    console.print("2. [bold]Zoom/Rotação[/]: Use o mouse para explorar o espaço de probabilidade.")
    console.print("3. [bold]Hover[/]: Passe o mouse sobre as esferas para ver o diagnóstico detalhado.")

if __name__ == "__main__":
    generate_interactive_3d()
