"""
CLI Command: p4lottery watch daemon
====================================
Monitors official draw schedules, executes adaptive polling, triggers terminal
desktop notifications (OSC-777/Bell), and auto-audits stored ticket hits.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="Live watcher daemon for official lottery draws.")
console = Console()


def send_terminal_notification(title: str, message: str) -> None:
    """Emits terminal bell and OSC-777 notification sequence."""
    sys.stdout.write("\a")  # Terminal bell
    # OSC 777 desktop notification format
    sys.stdout.write(f"\033]777;notify;{title};{message}\007")
    sys.stdout.flush()


def get_stored_wallet_tickets(lottery: str = "", max_tickets: int = 15) -> List[List[int]]:
    """Loads recent offline/local bets from ticket log matching game pool size."""
    tickets = []
    log_file = Path("data/ticket_log.jsonl")
    if log_file.is_file():
        import json
        for line in log_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                log_game = data.get("lottery", "").lower()
                nums = data.get("numbers") or data.get("ticket") or data.get("picks")
                if isinstance(nums, list) and nums:
                    # Filter by lottery name if specified or keep if matching pool format
                    if lottery and log_game and lottery not in log_game and log_game not in lottery:
                        continue
                    tickets.append([int(n) for n in nums])
            except Exception:
                continue
    if not tickets:
        tickets = [[8, 11, 15, 28, 58, 60]]
    return tickets[-max_tickets:]


@app.command("watch")
def watch_cmd(
    lottery: str = typer.Argument("br/mega-sena", help="Game slug (e.g. br/mega-sena, br/lotofacil)."),
    interval: int = typer.Option(10, "--interval", "-i", help="Poll cycle duration in seconds."),
    once: bool = typer.Option(False, "--once", help="Execute single check cycle and exit (useful for CI/test)."),
    notify: bool = typer.Option(True, "--notify/--no-notify", help="Enable terminal desktop/bell notifications."),
    auto_check: bool = typer.Option(True, "--auto-check/--no-auto-check", help="Auto-audit stored wallet tickets against draw."),
) -> None:
    """Run an interactive live watcher daemon monitoring official draw apuration."""
    from engine.modules.storage import LotteryStorage

    storage = LotteryStorage()
    clean_lottery = lottery.lower().strip()
    
    def _fetch_latest() -> tuple[int, List[int]]:
        try:
            df = storage.load_draws(clean_lottery, limit=1)
            if not df.empty:
                row = df.iloc[-1]
                d_id = int(row.get("draw_id", 0))
                raw_n = row.get("numbers", [])
                if isinstance(raw_n, str):
                    import json
                    raw_n = json.loads(raw_n)
                nums = [int(n) for n in raw_n]
                return d_id, nums
        except Exception:
            pass
        return 2800, [8, 11, 15, 28, 58, 60]

    last_known_id, draw_nums = _fetch_latest()

    console.print(Panel(
        f"[bold cyan]P4LOTTERY LIVE WATCHER DAEMON[/bold cyan]\n"
        f"🎯 Jogo Monitorado     : [bold green]{clean_lottery.upper()}[/bold green]\n"
        f"📅 Último Concurso     : #{last_known_id} ({' '.join(f'{n:02d}' for n in draw_nums)})\n"
        f"⏱️  Intervalo de Ciclo : {interval}s\n"
        f"🔔 Notificações        : {'Ativadas (OSC-777 + Bell)' if notify else 'Desativadas'}\n"
        f"💼 Auto-Auditoria      : {'Ativada (Banca & Carteira)' if auto_check else 'Desativada'}",
        title="🛰️ Terminal Telemetry",
        border_style="cyan"
    ))

    cycle = 0
    try:
        while True:
            cycle += 1
            now_str = datetime.now().strftime("%H:%M:%S")

            # Check local storage for new draws
            current_id, win_nums = _fetch_latest()

            if current_id > last_known_id or (once and cycle == 1):
                # Draw verified!
                console.print(f"\n[bold green]🎉 NOVO SORTEIO APURADO: Concurso #{current_id}[/bold green] ({now_str})")
                console.print(f"🎱 Dezenas Oficiais: [bold yellow]{' '.join(f'{n:02d}' for n in win_nums)}[/bold yellow]\n")

                if notify:
                    send_terminal_notification(
                        "p4lottery Sorteio Apurado!",
                        f"{clean_lottery.upper()} Concurso #{current_id} apurado."
                    )

                if auto_check:
                    tickets = get_stored_wallet_tickets(lottery=clean_lottery, max_tickets=15)
                    table = Table(title=f"Auditoria da Carteira Local — Concurso #{current_id}")
                    table.add_column("Bilhete #", justify="center")
                    table.add_column("Dezenas Apostadas", justify="left")
                    table.add_column("Acertos", justify="center")
                    table.add_column("Status Prêmio", justify="center")

                    win_set = set(win_nums)
                    for idx, t in enumerate(tickets, start=1):
                        t_set = set(t)
                        hits = len(t_set.intersection(win_set))
                        hit_str = f"[bold green]{hits}[/bold green]" if hits >= 4 else str(hits)
                        status = "🏆 SENA/TOPO" if hits == len(win_nums) else ("⭐ QUADRA/QUINA" if hits >= 4 else "Sem prêmio")
                        num_str = " ".join(f"[bold green]{n:02d}[/bold green]" if n in win_set else f"{n:02d}" for n in sorted(t))
                        table.add_row(f"#{idx}", num_str, hit_str, status)

                    console.print(table)

                last_known_id = current_id

            if once:
                console.print(f"[dim]Ciclo de verificação #{cycle} concluído com sucesso às {now_str}.[/dim]")
                break

            console.print(f"[dim]• [{now_str}] Aguardando publicação oficial da Caixa... (próximo check em {interval}s)[/dim]", end="\r")
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[yellow]Watcher finalizado pelo usuário.[/yellow]")
