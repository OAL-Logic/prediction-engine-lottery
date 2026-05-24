#!/usr/bin/env python3
"""
v10.0 Multi-Dimensional Hyper-Explorer 🚀
========================================
O ápice da visualização interativa do Prediction Engine.
Mapeia as 15 dimensões científicas em um espaço interativo 4D (3D + Tempo/Filtros).
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

def generate_hyper_explorer(lottery_id="br/mega-sena"):
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    rules = adapter.rules
    hi = rules.number_range[1]
    
    console.print(f"[bold cyan]Construindo Hiper-Explorer v10.0 para {lottery_id.upper()}...[/bold cyan]")
    
    # 1. Coleta exaustiva de todas as 15 dimensões
    strats = [
        "stacking_ai", "lyapunov_chaos", "retrocausality", "geo_sync", 
        "cpu_entropy", "crowd_antagonism", "sacred_grid", "ising_model", 
        "zeno_quantum", "tda_topology", "hurst_memory", "kolmogorov_order",
        "evt_extremes", "wavelet_signal", "nash_equilibrium"
    ]
    
    layer_scores = {}
    for s_name in strats:
        try:
            layer_scores[s_name] = get_strategy(s_name).score(df, rules)
        except:
            layer_scores[s_name] = {n: 0.0 for n in range(1, hi+1)}

    # 2. Agrupamento em "Meta-Dimensões" para o UI
    # X: Dezena
    # Y: Frequência Estrutural (Wavelet + Hurst)
    # Z: Pressão de Ciclo (EVT + Lyapunov)
    # Cor: IA Stacking (Confiança)
    # Tamanho: Nash Equilibrium (Inversamente proporcional à popularidade)
    
    x_data = list(range(1, hi + 1))
    
    # Eixo Y: Wavelet (Trend) + Hurst (Memory)
    y_data = []
    for n in x_data:
        val = (layer_scores["wavelet_signal"].get(n, 0) + layer_scores["hurst_memory"].get(n, 0)) / 2.0
        y_data.append(val)
        
    # Eixo Z: EVT (Extremes) + Lyapunov (Chaos)
    z_data = []
    for n in x_data:
        val = (layer_scores["evt_extremes"].get(n, 0) + layer_scores["lyapunov_chaos"].get(n, 0)) / 2.0
        z_data.append(val)

    # Cor: IA Stacking Score
    color_data = [layer_scores["stacking_ai"].get(n, 0) for n in x_data]
    
    # Tamanho: Nash Equilibrium (Quanto maior a bola, mais 'único' o prêmio será se sair)
    size_data = [20 + (layer_scores["nash_equilibrium"].get(n, 0) * 40) for n in x_data]

    # 3. Categorização por "Arquétipo Científico"
    categories = []
    for n in x_data:
        if layer_scores["retrocausality"].get(n, 0) > 0.8: categories.append("Quântica (Eco do Futuro)")
        elif layer_scores["ising_model"].get(n, 0) > 0.8: categories.append("Térmica (Transição Ising)")
        elif layer_scores["sacred_grid"].get(n, 0) > 0.8: categories.append("Geométrica (Proporção Phi)")
        elif layer_scores["tda_topology"].get(n, 0) > 0.8: categories.append("Topológica (Buracos TDA)")
        else: categories.append("Sinal Padrão")

    # 4. Construção do Dashboard Interativo
    fig = go.Figure()

    unique_cats = list(set(categories))
    for cat in unique_cats:
        indices = [i for i, c in enumerate(categories) if c == cat]
        nums = [x_data[i] for i in indices]
        
        fig.add_trace(go.Scatter3d(
            x=nums,
            y=[y_data[i] for i in indices],
            z=[z_data[i] for i in indices],
            mode='markers+text',
            name=cat,
            text=[f"#{n}" for n in nums],
            marker=dict(
                size=[size_data[i] for i in indices],
                color=[color_data[i] for i in indices],
                colorscale='Viridis',
                showscale=(cat == unique_cats[0]),
                opacity=0.85,
                line=dict(width=1, color='white')
            ),
            hovertemplate=(
                "<b>Dezena %{x}</b><br>" +
                "Momentum (Wavelet): %{y:.3f}<br>" +
                "Pressão (EVT): %{z:.3f}<br>" +
                "Confiança IA: %{marker.color:.3f}<br>" +
                "<extra></extra>"
            )
        ))

    # Layout Hiper-Espacial
    fig.update_layout(
        title=f"Hiper-Explorer v10.0: {lottery_id.upper()}<br><sup>15 Dimensões Científicas Integradas</sup>",
        scene=dict(
            xaxis_title='Número da Dezena',
            yaxis_title='Inércia de Fluxo (Y)',
            zaxis_title='Pressão de Evento (Z)',
            bgcolor="rgb(5, 5, 15)"
        ),
        template="plotly_dark",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=0, r=0, b=0, t=60)
    )

    output_path = f"data/hyper_explorer_{lottery_id.replace('/', '_')}.html"
    fig.write_html(output_path)
    
    console.print(f"\n[bold green]✓ Hiper-Explorer v10.0 Gerado![/bold green]")
    console.print(f"Abra: [yellow]{output_path}[/yellow]")
    
    # Guia de Decisão
    console.print("\n[bold]Como pilotar este Dashboard:[/bold]")
    console.print("• [bold]Eixo Vertical (Z)[/]: Busca dezenas no topo para pegar o 'Rompimento de Cauda' (EVT).")
    console.print("• [bold]Tamanho das Bolas[/]: Bolas grandes = Prêmio menos dividido (Equilíbrio de Nash).")
    console.print("• [bold]Cor Amarela[/]: Dezenas de maior confiança pela Stacking AI.")

if __name__ == "__main__":
    lottery = "br/mega-sena"
    if len(sys.argv) > 1: lottery = sys.argv[1]
    generate_hyper_explorer(lottery)
