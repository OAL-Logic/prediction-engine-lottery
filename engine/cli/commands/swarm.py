"""
Swarm Intelligence Command 🐝
=============================
Uses a Genetic Algorithm (GA) to evolve the 'Alpha Ticket'.
Optimizes for a fitness function that combines strategy scores 
and structural DNA health (parity, sums, consecutive).
"""

from __future__ import annotations

import random
import numpy as np
from typing import Annotated, Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from engine.cli.utils import get_adapter
from engine.strategies import get_strategy

console = Console()

class TicketDNA:
    """Helper to calculate structural fitness."""
    def __init__(self, rules):
        self.rules = rules
        self.lo, self.hi = rules.number_range

    def get_fitness(self, ticket: list[int]) -> float:
        score = 1.0
        
        # 1. Sum Range (Penalty if outside typical 70% range)
        # For Mega-Sena (60), avg sum is ~183. 70% range is approx 130-240.
        s = sum(ticket)
        expected_avg_sum = (self.lo + self.hi) / 2 * len(ticket)
        # Very rough heuristic: penalty for deviation from expected mean
        deviation = abs(s - expected_avg_sum) / expected_avg_sum
        if deviation > 0.3:
            score *= 0.5
            
        # 2. Parity Balance
        evens = sum(1 for n in ticket if n % 2 == 0)
        target_evens = len(ticket) // 2
        if abs(evens - target_evens) > 1:
            score *= 0.8
            
        # 3. Consecutive (Avoid long chains)
        consecutive = 0
        sorted_t = sorted(ticket)
        for i in range(len(sorted_t) - 1):
            if sorted_t[i+1] - sorted_t[i] == 1:
                consecutive += 1
        if consecutive > 1:
            score *= 0.7
            
        return score

def swarm(
    lottery: Annotated[str, typer.Argument(help="Lottery name")],
    generations: Annotated[int, typer.Option("--gens", "-g", help="Evolution generations")] = 50,
    pop_size: Annotated[int, typer.Option("--pop", "-p", help="Population size")] = 100,
    strategy: Annotated[str, typer.Option("--strategy", "-s", help="Primary strategy for scoring")] = "weighted",
) -> None:
    """🐝 Evolve the 'Alpha Ticket' using Swarm Intelligence.

    Initializes a population of random tickets and evolves them over several 
    generations using mutation and crossover. Fitness is determined by 
    a combination of strategy scores and structural DNA health.
    """
    adapter = get_adapter(lottery)
    df = adapter.fetch()
    rules = adapter.rules
    lo, hi = rules.number_range
    pick = rules.pick_count
    
    # 1. Get Base Strategy Scores
    with console.status(f"[cyan]Priming {strategy} scores..."):
        strat = get_strategy(strategy)
        scores = strat.score(df.tail(100), rules)
        
    dna = TicketDNA(rules)
    
    # 2. Initialize Population
    population = []
    pool = list(range(lo, hi + 1))
    for _ in range(pop_size):
        population.append(random.sample(pool, pick))
        
    def fitness(ticket: list[int]) -> float:
        # Strategy Score (Average of number scores)
        strat_score = np.mean([scores.get(n, 0.0) for n in ticket])
        # DNA Score
        dna_score = dna.get_fitness(ticket)
        return float(strat_score * dna_score)

    # 3. Evolution Loop
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[yellow]Evolving {pop_size} bees over {generations} generations...", total=generations)
        
        for gen in range(generations):
            # Sort by fitness
            population.sort(key=lambda t: fitness(t), reverse=True)
            
            # Keep top 20%
            new_pop = population[:pop_size // 5]
            
            # Fill the rest with offspring
            while len(new_pop) < pop_size:
                # Crossover
                parent1, parent2 = random.sample(population[:pop_size // 2], 2)
                # Uniform crossover
                child = []
                for i in range(pick):
                    gene = random.choice([parent1, parent2])[i]
                    if gene not in child:
                        child.append(gene)
                
                # Fill missing if duplicates occurred
                while len(child) < pick:
                    r = random.choice(pool)
                    if r not in child:
                        child.append(r)
                
                # Mutation (10% chance)
                if random.random() < 0.1:
                    idx = random.randint(0, pick - 1)
                    while True:
                        m = random.choice(pool)
                        if m not in child:
                            child[idx] = m
                            break
                            
                new_pop.append(child)
            
            population = new_pop
            progress.advance(task)

    # 4. Results
    best_ticket = sorted(population[0])
    best_fitness = fitness(best_ticket)
    
    console.rule(f"[bold yellow]🐝 SWARM INTELLIGENCE ALPHA — {rules.name}[/bold yellow]")
    
    result_panel = (
        f"\n[bold green]🏆 ALPHA TICKET: {best_ticket}[/bold green]\n"
        f"[dim]Fitness Score: {best_fitness:.4f}  ·  Generation: {generations}  ·  Pool: {pop_size}[/dim]\n"
    )
    console.print(Panel(result_panel, border_style="green", title="🐝 Evolution Complete"))

if __name__ == "__main__":
    swarm("br/lotofacil")
