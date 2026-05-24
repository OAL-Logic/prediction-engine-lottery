#!/usr/bin/env python3
"""
Bio-Feedback Pulse Synchronizer 💓
=================================
Esta ferramenta captura a 'Intuição Motora' do usuário em milissegundos.
Baseado na teoria do 'Farol Biológico': o seu eu futuro envia micro-pulsos
de adrenalina que afetam o seu tempo de reação no presente.
"""

import sys
import os
import time
import statistics

# Adiciona o diretório raiz ao path
sys.path.append(os.getcwd())

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()

def run_bio_feedback():
    console.print(Panel.fit(
        "[bold magenta]💓 Sincronizador de Pulso Bio-Feedback[/bold magenta]\n"
        "Capture sua ressonância intuitiva através do tempo de reação.",
        border_style="magenta"
    ))
    
    console.print("\n[bold]Instruções:[/bold]")
    console.print("1. Respire fundo e relaxe.")
    console.print("2. Quando o prompt aparecer, pressione [bold yellow]ENTER[/] o mais rápido possível.")
    console.print("3. Repetiremos isso 5 vezes para capturar sua 'assinatura de jitter'.\n")
    
    input("Pressione ENTER para começar...")
    
    delays = []
    for i in range(5):
        time.sleep(1 + (i % 2)) # Randomish wait
        start = time.perf_counter()
        input(f" [{i+1}/5] AGORA! > ")
        end = time.perf_counter()
        delays.append(end - start)
        
    # Análise de Micro-Variações
    mean_delay = statistics.mean(delays)
    stdev = statistics.stdev(delays) if len(delays) > 1 else 0.1
    
    console.print(f"\n[cyan]Análise Concluída:[/cyan]")
    console.print(f" • Reação Média: {mean_delay*1000:.2f}ms")
    console.print(f" • Assinatura de Jitter: {stdev*1000:.4f}ms")
    
    # Gerar dezenas baseadas nos milissegundos exatos
    # Usamos os decimais para escolher números da Mega-Sena (1-60)
    suggested = set()
    for d in delays:
        # Pega os 3 primeiros dígitos após o ponto decimal
        val = int(str(d).split('.')[-1][:3])
        num = (val % 60) + 1
        suggested.add(num)
        
    # Completa até 6 números se houver duplicatas
    import random
    random.seed(int(stdev * 1000000))
    while len(suggested) < 6:
        suggested.add(random.randint(1, 60))
        
    final_ticket = sorted(list(suggested))
    
    console.print(Panel(
        f"[bold green]💎 Bilhete de Ressonância Bio-Rítmica:[/bold green]\n\n"
        f"       {' - '.join(f'{n:02d}' for n in final_ticket)}",
        title="Resultado da Sincronização",
        border_style="green"
    ))
    
    console.print("\n[dim]Teoria: Estes números foram 'pescados' do seu fluxo motor, filtrando o ruído do subconsciente.[/dim]\n")

if __name__ == "__main__":
    run_bio_feedback()
