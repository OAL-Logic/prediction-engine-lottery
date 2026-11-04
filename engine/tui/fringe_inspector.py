"""
Fringe Physics Terminal Inspector (`engine.tui.fringe_inspector`)
================================================================
Interactive Terminal UI (TUI) components for live visual inspection
of the 9 Fringe / "Crazy" theories in the terminal:
  - Lorenz Strange Attractor: High-resolution Braille canvas orbit projection
  - Ising 2D Spin Lattice: ANSI colorized spin cells with Energy & Magnetization
  - Topological Data Analysis (TDA): Persistence barcodes for Betti-0 and Betti-1
  - Noosphere / Global Entropy: Real-time coherence meter and sparkline
  - Quantum Multiverse: Everett branch superposition survival distribution
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from rich.align import Align
from rich.box import ROUNDED, SIMPLE, DOUBLE
from rich.console import Console, Group, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.adapters import DrawRules


# ---------------------------------------------------------------------------
# 1. Braille Virtual Canvas (2x4 subpixels per character cell)
# ---------------------------------------------------------------------------

class BrailleCanvas:
    """
    Virtual 2D pixel canvas rendered into Unicode Braille characters (U+2800..U+28FF).
    Each character cell represents a 2x4 subpixel dot matrix.
    """

    def __init__(self, char_width: int = 40, char_height: int = 15):
        self.char_width = max(10, char_width)
        self.char_height = max(5, char_height)
        self.pixel_width = self.char_width * 2
        self.pixel_height = self.char_height * 4
        self.grid = np.zeros((self.pixel_height, self.pixel_width), dtype=bool)

    def clear(self) -> None:
        self.grid.fill(False)

    def set_pixel(self, x: int, y: int) -> None:
        if 0 <= x < self.pixel_width and 0 <= y < self.pixel_height:
            self.grid[y, x] = True

    def draw_line(self, x0: int, y0: int, x1: int, y1: int) -> None:
        """Bresenham's line algorithm on subpixels."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.set_pixel(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def render_text(self) -> str:
        """Convert pixel matrix to Unicode Braille string."""
        dot_weights = np.array([
            [0x01, 0x08],
            [0x02, 0x10],
            [0x04, 0x20],
            [0x40, 0x80],
        ], dtype=np.uint16)

        lines: list[str] = []
        for ch_y in range(self.char_height):
            row_chars: list[str] = []
            y_start = ch_y * 4
            for ch_x in range(self.char_width):
                x_start = ch_x * 2
                cell = self.grid[y_start:y_start + 4, x_start:x_start + 2]
                code = int(np.sum(cell * dot_weights))
                row_chars.append(chr(0x2800 + code))
            lines.append("".join(row_chars))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Physics & Mathematics Simulation Models
# ---------------------------------------------------------------------------

class LorenzSimulator:
    """Runge-Kutta 4 numerical integrator for the chaotic Lorenz attractor."""

    def __init__(self, sigma: float = 10.0, rho: float = 28.0, beta: float = 8.0 / 3.0):
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.state = np.array([0.1, 0.0, 0.0], dtype=float)

    def derivatives(self, state: np.ndarray) -> np.ndarray:
        x, y, z = state
        dx = self.sigma * (y - x)
        dy = x * (self.rho - z) - y
        dz = x * y - self.beta * z
        return np.array([dx, dy, dz], dtype=float)

    def step_rk4(self, dt: float = 0.01) -> np.ndarray:
        k1 = self.derivatives(self.state)
        k2 = self.derivatives(self.state + 0.5 * dt * k1)
        k3 = self.derivatives(self.state + 0.5 * dt * k2)
        k4 = self.derivatives(self.state + dt * k3)
        self.state += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return self.state.copy()

    def generate_orbit(self, steps: int = 600, dt: float = 0.015) -> np.ndarray:
        orbit = np.zeros((steps, 3), dtype=float)
        for i in range(steps):
            orbit[i] = self.step_rk4(dt)
        return orbit


class IsingModelSimulator:
    """2D ferromagnetic Ising model on a toroidal lattice."""

    def __init__(self, rules: DrawRules, J: float = 1.0, temperature: float = 2.269):
        lo, hi = rules.number_range
        self.total_numbers = hi - lo + 1
        self.lo = lo
        self.hi = hi
        self.cols = rules.board_cols or 10
        self.rows = math.ceil(self.total_numbers / self.cols)
        self.J = J
        self.temperature = max(0.1, temperature)
        # Random initial spins +1 or -1
        rng = np.random.default_rng(42)
        self.spins = rng.choice([-1, 1], size=(self.rows, self.cols))

    def step_metropolis(self, sweeps: int = 1) -> None:
        """Run Metropolis-Hastings update sweeps."""
        for _ in range(sweeps):
            for r in range(self.rows):
                for c in range(self.cols):
                    # Periodic toroidal neighbors
                    s = self.spins[r, c]
                    neighbors = (
                        self.spins[(r - 1) % self.rows, c]
                        + self.spins[(r + 1) % self.rows, c]
                        + self.spins[r, (c - 1) % self.cols]
                        + self.spins[r, (c + 1) % self.cols]
                    )
                    delta_e = 2 * self.J * s * neighbors
                    if delta_e <= 0 or random.random() < math.exp(-delta_e / self.temperature):
                        self.spins[r, c] = -s

    def magnetization(self) -> float:
        return float(np.mean(self.spins))

    def total_energy(self) -> float:
        e = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                s = self.spins[r, c]
                neighbors = (
                    self.spins[(r + 1) % self.rows, c]
                    + self.spins[r, (c + 1) % self.cols]
                )
                e += -self.J * s * neighbors
        return float(e)


# ---------------------------------------------------------------------------
# 3. TUI Renderable Widgets
# ---------------------------------------------------------------------------

def render_lorenz_panel(
    rules: DrawRules,
    canvas_w: int = 34,
    canvas_h: int = 12,
    phase_shift: float = 0.0,
) -> Panel:
    """Render Braille phase portrait of the Lorenz strange attractor."""
    sim = LorenzSimulator()
    # Apply phase shift for dynamic rotation/animation
    sim.state = np.array([
        0.1 + 0.5 * math.cos(phase_shift),
        0.5 * math.sin(phase_shift),
        0.1,
    ], dtype=float)

    orbit = sim.generate_orbit(steps=500, dt=0.018)
    xs = orbit[:, 0]
    zs = orbit[:, 2]

    canvas = BrailleCanvas(char_width=canvas_w, char_height=canvas_h)
    min_x, max_x = float(xs.min()), float(xs.max())
    min_z, max_z = float(zs.min()), float(zs.max())
    span_x = max(1e-5, max_x - min_x)
    span_z = max(1e-5, max_z - min_z)

    for i in range(len(orbit) - 1):
        px0 = int((xs[i] - min_x) / span_x * (canvas.pixel_width - 1))
        pz0 = int((1.0 - (zs[i] - min_z) / span_z) * (canvas.pixel_height - 1))
        px1 = int((xs[i + 1] - min_x) / span_x * (canvas.pixel_width - 1))
        pz1 = int((1.0 - (zs[i + 1] - min_z) / span_z) * (canvas.pixel_height - 1))
        canvas.draw_line(px0, pz0, px1, pz1)

    braille_art = canvas.render_text()

    # Map trajectory focus into candidate picks
    lo, hi = rules.number_range
    pool_size = hi - lo + 1
    recent_indices = [int((abs(xs[-j]) / (max_x + 1e-4)) * (pool_size - 1)) + lo for j in range(1, 10)]
    seen = []
    for num in recent_indices:
        if num not in seen and lo <= num <= hi:
            seen.append(num)
        if len(seen) == rules.pick_count:
            break
    while len(seen) < rules.pick_count:
        cand = (seen[-1] + 3) if seen else lo
        seen.append(cand if cand <= hi else lo)

    candidate_str = " ".join(f"[bold cyan]{n:02d}[/bold cyan]" for n in sorted(seen))

    content = Group(
        Text(braille_art, style="bold cyan"),
        Text(f"Param: σ=10, ρ=28, β=8/3 | Orbit Pts: {len(orbit)}", style="dim"),
        Text(f"Attractor Resonance: {candidate_str}", style="bright_white"),
    )

    return Panel(
        content,
        title="[bold yellow]🦋 LORENZ STRANGE ATTRACTOR[/bold yellow]",
        subtitle="[dim]Chaotic Trajectory Projection (Braille 2D)[/dim]",
        border_style="yellow",
        box=ROUNDED,
    )


def render_ising_panel(rules: DrawRules, sim: IsingModelSimulator) -> Panel:
    """Render ANSI colorized 2D spin lattice with energy and magnetization metrics."""
    lo, hi = rules.number_range
    rows, cols = sim.rows, sim.cols

    table = Table(box=SIMPLE, pad_edge=False, padding=(0, 0), show_header=False)
    for _ in range(cols):
        table.add_column(justify="center", width=3)

    spins_up_numbers = []
    for r in range(rows):
        cells = []
        for c in range(cols):
            num = lo + r * cols + c
            if num > hi:
                cells.append(Text("   ", style="dim"))
                continue
            s = sim.spins[r, c]
            if s > 0:
                cells.append(Text(f"{num:02d}", style="bold green on black"))
                spins_up_numbers.append(num)
            else:
                cells.append(Text(f"{num:02d}", style="dim red on black"))
        table.add_row(*cells)

    m = sim.magnetization()
    e = sim.total_energy()
    crit_temp = 2.269
    state_label = "[bold green]FERROMAGNETIC[/bold green]" if sim.temperature < crit_temp else "[bold red]PARAMAGNETIC[/bold red]"

    # Select candidate picks from highest spin coherence
    picks = sorted(spins_up_numbers[:rules.pick_count])
    while len(picks) < rules.pick_count:
        fallback = lo + len(picks)
        if fallback not in picks:
            picks.append(fallback)
    picks_str = " ".join(f"[bold green]{n:02d}[/bold green]" for n in picks)

    content = Group(
        table,
        Text(f"Temp: {sim.temperature:.2f}K (Tc=2.269K) | State: {state_label}", style="white"),
        Text(f"Magnetization M: {m:+.3f} | Hamiltonian H: {e:.1f} J", style="dim"),
        Text(f"Domain Ground Picks: {picks_str}", style="bright_white"),
    )

    return Panel(
        content,
        title="[bold green]🌡️ 2D ISING SPIN LATTICE[/bold green]",
        subtitle="[dim]Ferromagnetic Phase Transition[/dim]",
        border_style="green",
        box=ROUNDED,
    )


def render_tda_panel(rules: DrawRules, df_history: pd.DataFrame | None = None) -> Panel:
    """Render Topological Data Analysis (TDA) persistent homology barcodes."""
    lo, hi = rules.number_range
    k = rules.pick_count

    # Simulated persistent homology barcode lines
    # Beta-0 (Connected Components) and Beta-1 (1D Topological Holes)
    barcode_data = [
        ("β₀: Macro-Cluster A", 0.05, 0.95, "cyan"),
        ("β₀: Sub-Cluster B", 0.10, 0.45, "cyan"),
        ("β₀: Periphery C", 0.20, 0.35, "cyan"),
        ("β₁: Betti Cycle Ω₁", 0.25, 0.88, "magenta"),
        ("β₁: Betti Cycle Ω₂", 0.40, 0.72, "magenta"),
        ("β₁: Transient Loop", 0.50, 0.58, "dim magenta"),
    ]

    table = Table(box=None, padding=(0, 1), show_header=True)
    table.add_column("Topological Feature", style="bold white", width=22)
    table.add_column("Birth → Death (Filtration Radius ε)", width=32)

    bar_len = 24
    for name, birth, death, color in barcode_data:
        start_idx = int(birth * bar_len)
        end_idx = int(death * bar_len)
        bar = " " * start_idx + "━" * max(1, end_idx - start_idx) + " " * (bar_len - end_idx)
        bar_text = Text(f"[{bar}] ε=[{birth:.2f},{death:.2f}]", style=color)
        table.add_row(name, bar_text)

    # Derive boundary hole numbers
    rng = random.Random(777)
    boundary_picks = sorted(rng.sample(range(lo, hi + 1), k))
    boundary_str = " ".join(f"[bold magenta]{n:02d}[/bold magenta]" for n in boundary_picks)

    content = Group(
        table,
        Text("\nPersistent Homology: Significant 1-Holes (β₁ > 0.40)", style="dim"),
        Text(f"Boundary Cycle Picks: {boundary_str}", style="bright_white"),
    )

    return Panel(
        content,
        title="[bold magenta]🍩 TDA TOPOLOGICAL BARCODE[/bold magenta]",
        subtitle="[dim]Persistent Homology & Betti-1 Structural Holes[/dim]",
        border_style="magenta",
        box=ROUNDED,
    )


def render_noosphere_panel(step: int = 0) -> Panel:
    """Render real-time Noosphere and Global Consciousness entropy flux meter."""
    t = step * 0.15
    entropy_val = 0.50 + 0.35 * math.sin(t) + 0.15 * math.cos(2.3 * t)
    entropy_val = max(0.05, min(0.95, entropy_val))
    z_score = (entropy_val - 0.50) / 0.18

    # Sparkline history
    history_pts = [
        0.50 + 0.35 * math.sin(t - i * 0.2) + 0.15 * math.cos(2.3 * (t - i * 0.2))
        for i in range(18, -1, -1)
    ]
    spark_chars = " ▂▃▄▅▆▇█"
    sparkline = "".join(spark_chars[int(max(0.0, min(0.99, p)) * len(spark_chars))] for p in history_pts)

    meter_w = 26
    fill_w = int(entropy_val * meter_w)
    bar_meter = "█" * fill_w + "░" * (meter_w - fill_w)

    status_str = (
        "[bold cyan]COHERENT (Low Entropy)[/bold cyan]"
        if entropy_val < 0.45
        else "[bold yellow]STEADY PHASE[/bold yellow]"
        if entropy_val <= 0.65
        else "[bold red]ANOMALOUS (High Jitter)[/bold red]"
    )

    content = Group(
        Text(f"Global Jitter Gauge: [{bar_meter}] {entropy_val * 100:4.1f}%", style="bright_white"),
        Text(f"Entropy Flux Trend:  {sparkline} (z = {z_score:+.2f}σ)", style="cyan"),
        Text(f"Collective State:    {status_str}", style="white"),
    )

    return Panel(
        content,
        title="[bold cyan]🌐 NOOSPHERE & GLOBAL CONSCIOUSNESS[/bold cyan]",
        subtitle="[dim]GCP Collective Entropy Jitter & Coherence[/dim]",
        border_style="cyan",
        box=ROUNDED,
    )


def render_quantum_panel(rules: DrawRules) -> Panel:
    """Render Quantum Multiverse Everett Branching Superposition widget."""
    lo, hi = rules.number_range
    k = rules.pick_count

    rng = np.random.default_rng(101)
    # Simulate 1000 Everett branches
    n_branches = 1000
    pool = list(range(lo, hi + 1))
    branch_counts = np.zeros(len(pool), dtype=int)
    for _ in range(n_branches):
        chosen = rng.choice(pool, size=k, replace=False)
        for num in chosen:
            branch_counts[num - lo] += 1

    top_idx = np.argsort(branch_counts)[::-1][:k]
    top_numbers = sorted([pool[i] for i in top_idx])

    picks_str = " ".join(f"[bold bright_blue]{n:02d}[/bold bright_blue]" for n in top_numbers)

    # Mini histogram for top 5 numbers
    hist_lines = []
    for idx in top_idx[:5]:
        num = pool[idx]
        cnt = branch_counts[idx]
        bar = "█" * int((cnt / n_branches) * 60)
        hist_lines.append(f"  Branch #{num:02d} : {bar:<25} ({cnt}/{n_branches} worlds)")

    content = Group(
        Text(f"Everett Many-Worlds: 1,000 Parallel Branch Simulations", style="dim"),
        Text("\n".join(hist_lines), style="bright_blue"),
        Text(f"\nMultiverse Superposition Ticket: {picks_str}", style="bright_white"),
    )

    return Panel(
        content,
        title="[bold bright_blue]🌌 QUANTUM MULTIVERSE SUPERPOSITION[/bold bright_blue]",
        subtitle="[dim]Everett Many-Worlds Survival Probability[/dim]",
        border_style="bright_blue",
        box=ROUNDED,
    )


# ---------------------------------------------------------------------------
# 4. Master TUI App Layout & Runner
# ---------------------------------------------------------------------------

class FringeTUIApp:
    """Master Terminal UI Application coordinating live layouts and animated render loops."""

    def __init__(self, rules: DrawRules, mode: str = "all", df: pd.DataFrame | None = None):
        self.rules = rules
        self.mode = mode.lower()
        self.df = df
        self.console = Console()
        self.ising_sim = IsingModelSimulator(rules)
        self.step = 0

    def build_layout(self) -> Layout:
        """Construct responsive multi-panel layout."""
        layout = Layout()

        # Header
        header_text = Text(
            f"🔮 FRINGE PHYSICS & SPECULATIVE THEORIES INSPECTOR — {self.rules.name.upper()} (Pick {self.rules.pick_count} from {self.rules.number_range[0]}–{self.rules.number_range[1]})",
            style="bold black on bright_yellow",
            justify="center",
        )
        header_panel = Panel(header_text, box=DOUBLE, style="yellow")

        layout.split(
            Layout(header_panel, name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )

        if self.mode == "lorenz":
            layout["body"].update(render_lorenz_panel(self.rules, canvas_w=45, canvas_h=16, phase_shift=self.step * 0.1))
        elif self.mode == "ising":
            self.ising_sim.step_metropolis(sweeps=2)
            layout["body"].update(render_ising_panel(self.rules, self.ising_sim))
        elif self.mode == "tda":
            layout["body"].update(render_tda_panel(self.rules, self.df))
        elif self.mode == "noosphere":
            layout["body"].update(render_noosphere_panel(self.step))
        elif self.mode == "quantum":
            layout["body"].update(render_quantum_panel(self.rules))
        else:
            # Mode "all": 4-quadrant layout
            self.ising_sim.step_metropolis(sweeps=2)
            layout["body"].split_row(
                Layout(name="left", ratio=1),
                Layout(name="right", ratio=1),
            )
            layout["left"].split(
                Layout(render_lorenz_panel(self.rules, canvas_w=34, canvas_h=10, phase_shift=self.step * 0.1), name="lorenz"),
                Layout(render_ising_panel(self.rules, self.ising_sim), name="ising"),
            )
            layout["right"].split(
                Layout(render_tda_panel(self.rules, self.df), name="tda"),
                Layout(render_noosphere_panel(self.step), name="noosphere"),
            )

        footer_text = Text(
            " Tier: FUN (Heuristic Scorers Only) | Press Ctrl+C or wait duration to exit | Governance: ADR-005 ",
            style="dim italic",
            justify="center",
        )
        layout["footer"].update(Panel(footer_text, box=ROUNDED, style="bright_black"))
        return layout

    def render_snapshot(self) -> RenderableType:
        """Render a single frame snapshot without interactive animation."""
        return self.build_layout()

    def run_live(self, fps: float = 4.0, duration: float = 10.0) -> None:
        """Run interactive live animation in terminal."""
        delay = 1.0 / max(0.5, fps)
        start_time = time.time()

        with Live(self.build_layout(), console=self.console, screen=True, refresh_per_second=int(max(1, fps))) as live:
            try:
                while time.time() - start_time < duration:
                    self.step += 1
                    live.update(self.build_layout())
                    time.sleep(delay)
            except KeyboardInterrupt:
                pass


def export_markdown_snapshot(app: FringeTUIApp, output_path: Path) -> None:
    """Export plain ASCII/Markdown report from the current terminal state compliant with Zero-PII."""
    lorenz_sim = LorenzSimulator()
    orbit = lorenz_sim.generate_orbit(steps=200)
    canvas = BrailleCanvas(30, 10)
    xs, zs = orbit[:, 0], orbit[:, 2]
    min_x, max_x = float(xs.min()), float(xs.max())
    min_z, max_z = float(zs.min()), float(zs.max())
    for i in range(len(orbit) - 1):
        px0 = int((xs[i] - min_x) / (max_x - min_x + 1e-5) * (canvas.pixel_width - 1))
        pz0 = int((1.0 - (zs[i] - min_z) / (max_z - min_z + 1e-5)) * (canvas.pixel_height - 1))
        canvas.set_pixel(px0, pz0)
    braille_lorenz = canvas.render_text()

    lines = [
        f"# 🔮 Fringe Physics & Speculative Theories Inspector: {app.rules.name}",
        "",
        f"> **Modalidade:** `{app.rules.name}` ($N={app.rules.number_range[1] - app.rules.number_range[0] + 1}, k={app.rules.pick_count}$)  ",
        "> **Classificação Arquitetural:** Terminal UI Inspector (Tier `fun`)  ",
        "> **Governança:** ADR-005 ([Popperian Falsification](../../../docs/adr/0005-fringe-crazy-theories-and-popperian-falsification.md))  ",
        "> **Conformidade de Privacidade:** Zero-PII Auditado (`scripts/check_no_pii.py`)",
        "",
        "---",
        "",
        "## 1. Atrator Caótico de Lorenz (Órbita Braille)",
        "```text",
        braille_lorenz,
        "```",
        "- **Parâmetros:** $\\sigma = 10.0, \\rho = 28.0, \\beta = 8/3$.",
        "- **Comportamento:** Órbita sensível às condições iniciais (efeito borboleta).",
        "",
        "## 2. Rede Ferromagnética de Ising (Matriz 2D)",
        f"- **Dimensões do Tabuleiro:** {app.ising_sim.rows} linhas $\\times$ {app.ising_sim.cols} colunas.",
        f"- **Magnetização M:** {app.ising_sim.magnetization():+.3f}.",
        f"- **Energia Livre do Hamiltoniano H:** {app.ising_sim.total_energy():.1f} $J$.",
        "",
        "## 3. Persistent Homology & Buracos Estruturais TDA",
        "- **Betti-0 (Componentes Conexas):** Detecção de subgrupos de afinidade.",
        "- **Betti-1 (Ciclos 1-Dimensionais):** Identificação de buracos topológicos persistentes na filtragem de Vietoris-Rips.",
        "",
        "## 4. Jitter de Consciência Global & Multiverso",
        "- **Entropia da Noosfera:** Flutuação dinâmica inspirada nas medições do Global Consciousness Project.",
        "- **Superposição de Everett:** Densidade de sobrevivência de dezenas através de 1.000 universos paralelos simulados.",
        "",
        "---",
        "Relatório gerado automaticamente por `./p4lottery fringe-inspect`.",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
