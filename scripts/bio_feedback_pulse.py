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


def run_materialization_session(auto_mode: bool = False):
    """Sessão Guiada de Materialização, Coerência Cardíaca e Ancoragem Mental dos 17 Jogos."""
    from scripts.playwright_caixa_universal import PACOTE_ORCAMENTO_80

    console.print(Panel.fit(
        "[bold yellow]🥁 QUE RUFEM OS TAMBORES — SESSÃO DE MATERIALIZAÇÃO & SINCRONIA[/bold yellow]\n"
        "[cyan]Alinhamento Celestial: Lua Cheia (62.2%) • Sol 216.5° Escorpião • Terra 36.5° Touro • Júpiter (Quinta-feira)[/cyan]\n"
        "[dim]Semente Ambiental SHA-256: 2808670435  |  Regime Noosfera: High Focus (0.869)[/dim]",
        border_style="yellow",
    ))

    etapas = [
        (
            "FASE 1 — ATERRAMENTO & COERÊNCIA CARDÍACA (Terra em Touro 36.5° / 29.99 km/s)",
            "Inspire profundamente por 4 segundos... Segure por 4 segundos... Expire lentamente por 6 segundos.\n"
            "Sinta o peso do corpo conectado ao planeta Terra viajando a 29,99 km/s pelo espaço.\n"
            "Pensamento-semente: 'Minha mente está serena, focada e em perfeita harmonia com o fluxo de abundância.'",
        ),
        (
            "FASE 2 — RESSONÂNCIA LUNAR & INTUIÇÃO (Lua Cheia 86.2% Iluminação / Maré 51%)",
            "Visualize a luz prateada da Lua Cheia iluminando as esferas numeradas.\n"
            "Nas 8 fases históricas, este plenilúnio amplifica a clareza, a expansão (Spread) e a convergência.\n"
            "Sinta gratidão antecipada, como se o resultado já tivesse se concretizado no presente.",
        ),
        (
            "FASE 3 — IMantação DAS DEZENAS-NÚCLEO (Árvore da Vida / Sephirot & Geometria)",
            "Focalize mentalmente os pilares da nossa carteira:\n"
            " • MEGA-SENA Núcleo: [10 • 11 • 17 • 28 • 32 • 34 • 38 • 44]\n"
            "   (10 = Malkuth / Manifestação Física | 11 = Força & Justiça | 17 = A Estrela / Esperança | 32 = Os 32 Caminhos da Sabedoria)\n"
            " • LOTOFÁCIL Núcleo Fixo: [02 • 06 • 08 • 10 • 11 • 13 • 15 • 16 • 20 • 25]\n"
            "   (13 = Transformação & Unidade | 15 = Ressonância Orbital | 25 = Plenitude Quântica 5×5)",
        ),
        (
            "FASE 4 — COLAPSO DA FUNÇÃO DE ONDA & EMISSÃO DE INTENÇÃO",
            "Visualize o painel de conferência brilhando em verde.\n"
            "Declare mentalmente:\n"
            " 'A probabilidade encontra o propósito. A prosperidade flui com sabedoria, paz e equilíbrio.'",
        ),
    ]

    for titulo, texto in etapas:
        console.print(Panel(texto, title=f"[bold magenta]{titulo}[/bold magenta]", border_style="cyan"))
        if not auto_mode:
            time.sleep(1.2)

    console.print("\n[bold yellow]🥁 Rufando os tambores para os 17 Bilhetes Consagrados (R$ 79,50):[/bold yellow]")
    for item in PACOTE_ORCAMENTO_80:
        mod = item["modalidade"].upper()
        console.print(f"\n[bold green]✨ {mod} ({len(item['jogos'])} Jogos):[/bold green]")
        for idx, j in enumerate(item["jogos"], start=1):
            fmt = " - ".join(f"{n:02d}" for n in j)
            console.print(f"   [bold white]Jogo {idx:02d}:[/bold white] [yellow]{fmt}[/yellow]")

    console.print(Panel(
        "[bold green]✨ SESSÃO DE MATERIALIZAÇÃO SELADA COM SUCESSO! ✨[/bold green]\n"
        "Mantenha a mente leve, desapegada da ansiedade e aberta à sincronicidade.",
        border_style="green",
    ))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bio-Feedback Pulse & Sessão de Materialização")
    parser.add_argument("--materialize", "-m", action="store_true", help="Executa a sessão guiada de materialização dos 17 jogos")
    parser.add_argument("--auto", action="store_true", help="Executa sem pausas longas")
    args = parser.parse_args()
    if args.materialize:
        run_materialization_session(auto_mode=args.auto)
    else:
        run_bio_feedback()
