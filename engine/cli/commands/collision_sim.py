"""
Collision Simulator Command 🎱
==============================
A high-fidelity 3D/2D physical Monte Carlo simulator for lottery ball containers.
Models gravity, wall collisions, ball-to-ball elastic collisions, and mass offsets 
arising from micro-variations in ink weight or ball composition.
"""

from __future__ import annotations

import random
from typing import Annotated, Optional
import numpy as np
import pandas as pd
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from engine.cli.utils import get_adapter

console = Console()

def run_simulation(
    number_range: tuple[int, int],
    trials: int = 10,
    steps: int = 1000,
    dt: float = 0.05,
    g_val: float = -9.8,
    ink_delta: float = 0.005,
    rotation_speed: float = 1.5,
) -> dict[int, float]:
    """Simulates elastic ball collisions inside a circular rotating drum with gravity."""
    lo, hi = number_range
    all_numbers = list(range(lo, hi + 1))
    n_balls = len(all_numbers)
    
    R = 100.0  # Drum Radius
    ball_radius = 5.0
    
    # Track when each ball exits the drum across all trials
    chute_exit_times: dict[int, list[float]] = {n: [] for n in all_numbers}
    
    # Gravity Vector
    g_vec = np.array([0.0, g_val])
    
    for _ in range(trials):
        # 1. Initialize Positions (seeded inside circular boundary)
        pos = np.zeros((n_balls, 2))
        for i in range(n_balls):
            while True:
                # Random location inside drum
                r_pos = np.random.uniform(-R * 0.8, R * 0.8, 2)
                if np.linalg.norm(r_pos) < R - ball_radius:
                    # Make sure it doesn't overlap other initialized balls
                    overlap = False
                    for j in range(i):
                        if np.linalg.norm(r_pos - pos[j]) < ball_radius * 2.0:
                            overlap = True
                            break
                    if not overlap:
                        pos[i] = r_pos
                        break
        
        # 2. Initial Velocities
        vel = np.random.uniform(-10.0, 10.0, (n_balls, 2))
        
        # 3. Masses (Ink-weight micro-variation + baseline)
        # Higher numbers have slightly more/less ink, adding a tiny mass difference
        masses = np.array([1.0 + (i * ink_delta) for i in range(n_balls)])
        
        # Simulation loop
        for step in range(steps):
            # Apply Gravity
            vel += g_vec * dt
            
            # Apply Position updates
            pos += vel * dt
            
            # Drum Boundary collision with rotation friction boost
            dists = np.linalg.norm(pos, axis=1)
            out_of_bounds = dists > (R - ball_radius)
            if np.any(out_of_bounds):
                for idx in np.where(out_of_bounds)[0]:
                    # Push back inside bounds
                    normal = pos[idx] / dists[idx]
                    pos[idx] = normal * (R - ball_radius)
                    
                    # Reflect velocity
                    v_dot_n = np.dot(vel[idx], normal)
                    if v_dot_n > 0:
                        vel[idx] -= 2.0 * v_dot_n * normal
                    
                    # Add tangential velocity component from drum rotation
                    tangent = np.array([-normal[1], normal[0]])
                    vel[idx] += tangent * rotation_speed * 0.1
            
            # Ball-to-ball elastic collisions
            for i in range(n_balls):
                for j in range(i + 1, n_balls):
                    disp = pos[i] - pos[j]
                    dist = np.linalg.norm(disp)
                    min_dist = ball_radius * 2.0
                    if dist < min_dist:
                        # Normalize displacement
                        disp_norm = disp / (dist if dist > 0 else 1.0)
                        
                        # Move them apart slightly to prevent clipping
                        overlap = min_dist - dist
                        pos[i] += disp_norm * (overlap * 0.5)
                        pos[j] -= disp_norm * (overlap * 0.5)
                        
                        # Elastic collision velocities calculation
                        m1, m2 = masses[i], masses[j]
                        v1, v2 = vel[i], vel[j]
                        
                        relative_vel = v1 - v2
                        v_rel_dot_d = np.dot(relative_vel, disp_norm)
                        
                        if v_rel_dot_d < 0:
                            # Impulse scalar
                            impulse = (2.0 * v_rel_dot_d) / (m1 + m2)
                            vel[i] -= impulse * m2 * disp_norm
                            vel[j] += impulse * m1 * disp_norm
            
            # Check exit chute (bottom center of the drum: y < -0.85 * R and |x| < 0.2 * R)
            for i in range(n_balls):
                if pos[i, 1] < -0.85 * R and abs(pos[i, 0]) < 0.20 * R:
                    # Ball exited!
                    chute_exit_times[all_numbers[i]].append(step * dt)
                    
                    # Reset ball to the top to keep simulation moving
                    pos[i] = np.array([np.random.uniform(-30.0, 30.0), R * 0.7])
                    vel[i] = np.array([0.0, -10.0])
                    
    # Process exit times into final scoring distributions
    scores: dict[int, float] = {}
    for n in all_numbers:
        exits = chute_exit_times[n]
        if exits:
            # Score is based on frequency of exit and how early they exited (inverse average time)
            avg_time = sum(exits) / len(exits)
            scores[n] = len(exits) / (avg_time + 1.0)
        else:
            scores[n] = 0.0
            
    # Normalize
    max_score = max(scores.values()) if scores else 1.0
    if max_score == 0: max_score = 1.0
    return {n: v / max_score for n, v in scores.items()}

def collision_sim(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    trials: Annotated[int, typer.Option("--trials", "-t", help="Number of Monte Carlo simulation runs")] = 10,
    steps: Annotated[int, typer.Option("--steps", "-s", help="Simulation steps per run")] = 800,
    g_val: Annotated[float, typer.Option("--g", "-g", help="Simulated gravity acceleration")] = -9.8,
    ink_delta: Annotated[float, typer.Option("--ink-delta", "-d", help="Simulated ball mass delta due to ink weight")] = 0.005,
    rotation: Annotated[float, typer.Option("--rotation", "-r", help="Drum rotation speed")] = 1.5,
) -> None:
    """🎱 High-fidelity kinetic Monte Carlo collision simulation for any lottery.
    
    Models dynamic ball-to-ball collisions, boundary elasticity, drum rotation,
    and micro-variations in ink weight to identify the top candidates likely
    to enter the exit chute first.
    """
    adapter = get_adapter(lottery)
    rules = adapter.rules
    
    console.rule(f"[bold cyan]Pseudo-Kinetic Fluid Simulator: {rules.name}[/bold cyan]")
    
    with console.status("[bold green]Simulating physical container kinematics..."):
        scores = run_simulation(
            number_range=rules.number_range,
            trials=trials,
            steps=steps,
            g_val=g_val,
            ink_delta=ink_delta,
            rotation_speed=rotation,
        )
        
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Presentation
    table = Table(title="Kinetic Chute Candidates (Top 10)", box=None)
    table.add_column("Rank", justify="center", style="dim")
    table.add_column("Number", justify="center", style="bold green")
    table.add_column("Exit Likelihood", justify="right", style="cyan")
    table.add_column("Kinetic Profile", justify="left")
    
    for rank, (num, score) in enumerate(sorted_scores[:10]):
        # Calculate simulated mass offset percentage
        mass_offset = (num - rules.number_range[0]) * ink_delta * 100.0
        spark = "█" * int(score * 15)
        table.add_row(
            str(rank + 1),
            f"{num:02d}",
            f"{score * 100:.1f}%",
            f"[dim]Mass Δ: +{mass_offset:.2f}% |[/dim] {spark}"
        )
        
    console.print(table)
    
    # Summary of consensus pick ticket
    picks = sorted([num for num, _ in sorted_scores[:rules.pick_count]])
    picks_str = " ".join(f"{p:02d}" for p in picks)
    
    console.print()
    console.print(Panel(
        f"[bold yellow]Kinetic Alpha Ticket:[/bold yellow] {picks_str}\n"
        f"[dim]Simulated Trials: {trials} | Steps: {steps} | Gravity: {g_val} m/s² | Mass Variation: {ink_delta}[/dim]",
        title="Physical Consensus",
        border_style="cyan"
    ))
