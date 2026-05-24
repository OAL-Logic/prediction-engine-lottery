"""
CLI Utilities 🛠️
===============
Common helper functions for the Lottery Engine CLI.
"""

from __future__ import annotations

import importlib
import math
import json
import time
from pathlib import Path
from typing import Any, Optional, Callable, Awaitable, TYPE_CHECKING

import typer
from rich import print as rprint
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.prompt import IntPrompt

if TYPE_CHECKING:
    import numpy as np

from engine.adapters.registry import registry

def load_local_config() -> dict[str, Any]:
    """
    Search for personal.local.yaml or any *.local.yaml in the project root
    and return a merged dictionary of their contents.
    Used to inject private data (name, birth_date) into strategies.
    """
    import yaml
    config = {}
    # Look for files matching *.local.yaml or .local.yml
    local_files = sorted(list(Path(".").glob("*.local.y*ml")))
    for file_path in local_files:
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    config.update(data)
        except Exception as e:
            import logging
            logging.warning(f"Failed to load local config {file_path}: {e}")
    return config

console = Console()
DATA_DIR = Path(__file__).parent.parent.parent / "data"

# --- Caching Primitives 🗄️ ---

def get_cached_data(cache_name: str, fetch_func: Callable[[], Any], ttl: int = 3600) -> Any:
    """Generic disk-based cache for expensive calls (sync)."""
    cache_dir = DATA_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    file_path = cache_dir / f"{cache_name}.json"
    
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                cached = json.load(f)
            if time.time() - cached.get("timestamp", 0) < ttl:
                return cached.get("data")
        except (json.JSONDecodeError, KeyError): pass
            
    try:
        data = fetch_func()
        with open(file_path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    except Exception as e:
        import logging
        logging.error(f"Cache fetch failed for {cache_name}: {e}")
        return None

async def get_cached_data_async(cache_name: str, fetch_func: Callable[[], Awaitable[Any]], ttl: int = 3600) -> Any:
    """Generic disk-based cache for expensive calls (async)."""
    cache_dir = DATA_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    file_path = cache_dir / f"{cache_name}.json"
    
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                cached = json.load(f)
            if time.time() - cached.get("timestamp", 0) < ttl:
                return cached.get("data")
        except (json.JSONDecodeError, KeyError): pass
            
    try:
        data = await fetch_func()
        with open(file_path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    except Exception as e:
        import logging
        logging.error(f"Async cache fetch failed for {cache_name}: {e}")
        return None

def select_lottery_ui(console: Console, prompt: str = "Select a lottery") -> str:
    """Show a numbered list of available lotteries and return the selected ID."""
    games = registry.list_games()
    
    table = Table(title="Available Lotteries", box=None, padding=(0, 2))
    table.add_column("Index", style="cyan", justify="right")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Format", style="green")
    
    for i, g in enumerate(games):
        fmt = f"{g.pick_count}/{g.pool_size}"
        if g.bonus_count > 0: fmt += f" + {g.bonus_count}/{g.bonus_pool}"
        status = "[green]●[/green]" if g.data_available else "[dim]○[/dim]"
        table.add_row(str(i + 1), g.id, f"{status} {g.name}", fmt)
        
    console.print(table)
    
    choice = IntPrompt.ask(f"\n{prompt} (1-{len(games)})", default=1)
    if 1 <= choice <= len(games):
        return games[choice - 1].id
    return games[0].id


def print_command_summary(command: str, lottery: str, **params: Any) -> None:
    """Print a summary of the command parameters at the start."""
    game = registry.get_game(lottery)
    game_name = game.name if game else lottery
    
    summary = f"[bold cyan]Launching {command.upper()}[/bold cyan]\n"
    summary += f"  [bold]Lottery:[/bold]  {game_name} ({lottery})\n"
    
    for k, v in params.items():
        if v is None: continue
        label = k.replace("_", " ").title()
        summary += f"  [bold]{label}:[/bold]  {v}\n"
        
    rprint(Panel(summary.strip(), border_style="cyan"))


def format_confidence(score: float) -> str:
    """Return a color-coded percentage string for a confidence score (0-1)."""
    pct = score * 100
    color = "red"
    if score > 0.8: color = "bold green"
    elif score > 0.6: color = "green"
    elif score > 0.4: color = "yellow"
    elif score > 0.2: color = "orange3"
    
    return f"[{color}]{score:.3f} ({pct:.1f}%)[/{color}]"


def get_adapter(lottery_id: str):  # type: ignore[return]
    """Dynamically load an adapter by name (canonical or alias)."""
    # Ensure lottery_id is a string
    lottery_id = str(lottery_id)
    
    game = registry.get_game(lottery_id)
    if not game or not game.data_available or not game.adapter:
        available = [g.id for g in registry.list_games(only_available=True)]
        rprint(
            f"[red]Lottery '{lottery_id}' is not available or has no historical data adapter yet.[/red]\n"
            f"Available: {', '.join(available)}"
        )
        raise typer.Exit(1)

    # Resolve adapter class path
    adapter_map = {
        "mega_sena": "engine.adapters.br.mega_sena.MegaSenaAdapter",
        "lotofacil": "engine.adapters.br.lotofacil.LotofacilAdapter",
        "quina": "engine.adapters.br.quina.QuinaAdapter",
        "dupla_sena": "engine.adapters.br.dupla_sena.DuplaSenaAdapter",
        "dia_de_sorte": "engine.adapters.br.dia_de_sorte.DiaDeSorteAdapter",
        "mais_milionaria": "engine.adapters.br.mais_milionaria.MaisMilionariaAdapter",
        "lotomania": "engine.adapters.br.lotomania.LotomaniaAdapter",
        "powerball": "engine.adapters.us.powerball.PowerballAdapter",
    }
    
    path = adapter_map.get(game.adapter, game.adapter)
    if not path or "." not in path:
        rprint(f"[red]Error: Adapter path for '{lottery_id}' is invalid: {path}[/red]")
        raise typer.Exit(1)

    module_path, class_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()


def geocode(address: str) -> tuple[float, float] | None:
    """Simulate geocoding an address into (lat, lon) using OpenStreetMap (Nominatim)."""
    import httpx
    import urllib.parse
    
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(address)}&format=json&limit=1"
    headers = {"User-Agent": "lottery-engine-cli/1.0"}
    
    try:
        with httpx.Client(timeout=10.0, headers=headers) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


# --- TUI Design Language 🏛️ ---

class Theme:
    """Standard color palette and border styles."""
    HEADER_BG = "bold white on blue"
    PRIMARY = "cyan"
    SECONDARY = "gold1"
    SUCCESS = "spring_green3"
    WARNING = "orange_red1"
    DANGER = "red1"
    MUTED = "bright_black"
    DUMMY = "bold yellow"
    BORDER = "bright_black"


def ui_header(command_name: str, subtitle: str = "") -> None:
    """Draw a consistent top-level command header."""
    title = f" 🚀 [bold white]{command_name.upper()}[/] "
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    grid.add_row(
        f"[{Theme.HEADER_BG}]{title}[/]",
        f"[dim]{subtitle}[/]" if subtitle else ""
    )
    rprint(Panel(grid, border_style=Theme.BORDER, padding=(0, 1)))


def ui_panel(content: Any, title: str = "", subtitle: str = "", style: str = Theme.PRIMARY, expand: bool = True) -> Panel:
    """Standard container for output sections."""
    return Panel(
        content,
        title=f"[bold {style}] {title} [/]" if title else None,
        subtitle=f"[dim] {subtitle} [/]" if subtitle else None,
        border_style=Theme.BORDER,
        expand=expand,
        padding=(1, 2)
    )


def ui_table(title: str = "", columns: list[str] = None) -> Table:
    """Create a standardized table with consistent styling."""
    t = Table(title=f"[bold]{title}[/]" if title else None, box=None, header_style=f"bold {Theme.PRIMARY}")
    if columns:
        for col in columns:
            t.add_column(col)
    return t


def ui_dummy_block(category: str, message: str) -> None:
    """A high-visibility educational block following the 'Dummies' style."""
    icons = {
        "tip": "💡",
        "remember": "📌",
        "warning": "⚠️ ",
        "tech": "🧠"
    }
    colors = {
        "tip": Theme.SECONDARY,
        "remember": Theme.PRIMARY,
        "warning": Theme.WARNING,
        "tech": "magenta"
    }
    labels = {
        "tip": "TIP",
        "remember": "REMEMBER",
        "warning": "WATCH OUT",
        "tech": "TECH STUFF"
    }

    icon = icons.get(category.lower(), "•")
    color = colors.get(category.lower(), "white")
    label = labels.get(category.lower(), category.upper())

    rprint(f"\n[{color}]{icon} [bold]{label}:[/bold] {message}[/]")


def ui_section(title: str) -> None:
    """A minimal horizontal rule with a section title."""
    rprint(f"\n[bold {Theme.MUTED}]── {title.upper()} " + ("─" * (60 - len(title))) + "[/]")


# --- Legacy / Utility Helpers ---

def calculate_shannon_entropy(scores: dict[int, float]) -> float:
    """
    Calculates the Shannon Entropy of a score distribution.
    Lower = more focused/concentrated (good signal).
    Higher = more diffuse/random (noise).
    """
    import numpy as np
    vals = np.array(list(scores.values()), dtype=float)
    if vals.sum() == 0:
        return 0.0
    vals = vals / vals.sum()
    vals = vals[vals > 0]
    return float(-np.sum(vals * np.log(vals + 1e-12)))


def bar_chart(value: float, width: int = 15) -> str:
    """Simple terminal bar representation of a 0.0-1.0 value."""
    filled = int(round(value * width))
    return "█" * filled + "░" * (width - filled)


# ── Structural analysis helpers (shared by ticket-dna, draw-fingerprint, outlier-draws) ──

def percentile_rank(value: float, population: list[float]) -> float:
    """Fraction of population strictly below value (0–100)."""
    if not population:
        return 50.0
    below = sum(1 for v in population if v < value)
    return below / len(population) * 100


def decade_spread(nums: list[int], lo: int, hi: int) -> float:
    """Fraction of pool decades (tenths) covered by at least one number."""
    pool_range = hi - lo + 1
    decade_size = max(1, pool_range // 10)
    decades_covered = set((n - lo) // decade_size for n in nums)
    max_decades = pool_range // decade_size + 1
    return len(decades_covered) / max_decades


def symmetry_score(nums: list[int], lo: int, hi: int) -> float:
    """Mean absolute deviation from pool midpoint (lower = more symmetric)."""
    mid = (lo + hi) / 2.0
    return sum(abs(n - mid) for n in nums) / len(nums) if nums else 0.0


def sparkline(values: list[float], width: int = 20) -> str:
    """Map a sequence of floats to an 8-level block character sparkline."""
    _BLOCKS = "▁▂▃▄▅▆▇█"
    if not values:
        return ""
    lo_v, hi_v = min(values), max(values)
    rng = hi_v - lo_v or 1.0
    out = []
    for v in values[:width]:
        idx = int((v - lo_v) / rng * 7)
        out.append(_BLOCKS[idx])
    return "".join(out)
