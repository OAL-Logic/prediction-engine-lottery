#!/usr/bin/env python3
"""
3D Correlation Visualization - Mega-Sena
========================================
Gera uma representação espacial das dezenas da Mega-Sena em 3 dimensões:
X: Número da dezena (1-60)
Y: Frequência Histórica (%)
Z: Atraso Atual (Draws since last hit)

Cor: Engine Score (Probabilidade)
Tamanho: Consenso dos Algoritmos
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy
from rich.console import Console

console = Console()

def generate_3d_viz():
    lottery_id = "br/mega-sena"
    adapter = get_adapter(lottery_id)
    df = adapter.fetch()
    rules = adapter.rules
    
    console.print("[bold cyan]Calculando dimensões espaciais para 60 dezenas...[/bold cyan]")
    
    # 1. Obter Scores e Consenso (Blend de estratégias)
    strat_names = ["weighted", "pattern", "monte_carlo", "spectral"]
    all_scores = {n: {} for n in strat_names}
    consensus_counts = {i: 0 for i in range(1, 61)}
    final_scores = {i: 0.0 for i in range(1, 61)}
    
    for name in strat_names:
        strat = get_strategy(name)
        scores = strat.score(df, rules)
        # Top 15 de cada estratégia ganha ponto de consenso
        top_15 = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:15]
        for num in top_15:
            consensus_counts[num] += 1
        for num, val in scores.items():
            final_scores[num] += val
            
    # 2. Calcular Frequência e Atraso
    history_len = len(df)
    freqs = {i: 0 for i in range(1, 61)}
    last_seen = {i: history_len for i in range(1, 61)}
    
    for idx, row in df.iterrows():
        nums = row['numbers']
        for n in nums:
            freqs[n] += 1
            if last_seen[n] == history_len: # First time seeing it from the top
                last_seen[n] = idx

    # 3. Preparar dados para o Plot
    x = list(range(1, 61))
    y = [freqs[i] / history_len * 100 for i in x] # Freq %
    z = [last_seen[i] for i in x] # Delay
    colors = [final_scores[i] for i in x]
    sizes = [10 + (consensus_counts[i] * 50) for i in x]
    
    # 4. Criar o Gráfico 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(x, y, z, c=colors, s=sizes, cmap='viridis', alpha=0.8, edgecolors='w')
    
    # Destacar o "Jogo Perfeito"
    perfect_game = [6, 15, 25, 27, 32, 55]
    for pg_num in perfect_game:
        idx = pg_num - 1
        ax.text(x[idx], y[idx], z[idx], f" {pg_num}", color='red', fontweight='bold')
        ax.scatter([x[idx]], [y[idx]], [z[idx]], color='red', s=200, edgecolors='black', marker='*')

    ax.set_xlabel('Dezena (1-60)')
    ax.set_ylabel('Frequência Histórica (%)')
    ax.set_zlabel('Atraso (Sorteios)')
    ax.set_title('Mapa de Correlação 3D: Mega-Sena\nEstrela Vermelha = Bilhete de Elite')
    
    fig.colorbar(scatter, label='Engine Probability Score')
    
    output_path = "data/mega_sena_3d_map.png"
    plt.savefig(output_path)
    console.print(f"\n[bold green]✓ Visualização 3D gerada com sucesso![/bold green]")
    console.print(f"Arquivo salvo em: [yellow]{output_path}[/yellow]")
    
    # Resumo em modo texto para o usuário
    console.print("\n[bold]Interpretando o Espaço 3D:[/bold]")
    console.print("• [bold red]Estrela Vermelha[/]: Números do seu Jogo Perfeito.")
    console.print("• [bold green]Eixo Z (Altura)[/]: Quanto mais alto, mais 'atrasado' o número (Oportunidade de Ciclo).")
    console.print("• [bold cyan]Eixo Y[/]: Quanto maior, mais frequente o número (Momentum).")
    console.print("• [bold]Tamanho da Esfera[/]: Representa o Consenso dos algoritmos.")

if __name__ == "__main__":
    generate_3d_viz()
