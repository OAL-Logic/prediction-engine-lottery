#!/usr/bin/env python3
"""
Maxwell-Boltzmann 2D Evolution Simulation
A Python script that simulates 2D elastic collisions of gas particles to demonstrate
thermalization and entropy maximization (Boltzmann's H-theorem) toward the Rayleigh distribution.
Renders a live ASCII dashboard directly in the terminal using ANSI escape codes.
"""

import sys
import time
import argparse
import csv
import numpy as np
from scipy.stats import chisquare

def parse_args():
    parser = argparse.ArgumentParser(
        description="Maxwell-Boltzmann 2D Evolution Simulation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-n", "--particles", type=int, default=150,
                        help="Number of gas particles in the simulation")
    parser.add_argument("-s", "--initial-state", type=str, default="mono-energetic",
                        choices=["mono-energetic", "hot-cold", "single-bullet"],
                        help="Initial state profile to demonstrate evolution to equilibrium")
    parser.add_argument("-w", "--box-width", type=float, default=60.0,
                        help="Physical width of the 2D gas container")
    parser.add_argument("-H", "--box-height", type=float, default=25.0,
                        help="Physical height of the 2D gas container")
    parser.add_argument("-r", "--radius", type=float, default=0.5,
                        help="Radius of each particle")
    parser.add_argument("--fps", type=int, default=20,
                        help="Target frame rate for terminal rendering")
    parser.add_argument("--steps", type=int, default=0,
                        help="Number of steps to run (0 for infinite until Ctrl+C)")
    parser.add_argument("--export", type=str, default=None,
                        help="CSV file path to export simulation history metrics")
    return parser.parse_args()

def initialize_positions(N, radius, width, height, split=None):
    """
    Finds non-overlapping random positions for N particles inside the box.
    Uses rejection sampling, with optional split positioning (left vs right).
    """
    pos = np.zeros((N, 2))
    for i in range(N):
        placed = False
        attempts = 0
        while not placed and attempts < 2000:
            if split is None:
                x = np.random.uniform(radius[i], width - radius[i])
            elif split[i] == 'left':
                x = np.random.uniform(radius[i], width / 2.0 - radius[i] - 1.0)
            else:
                x = np.random.uniform(width / 2.0 + radius[i] + 1.0, width - radius[i])
            
            y = np.random.uniform(radius[i], height - radius[i])
            
            if i == 0:
                pos[i] = [x, y]
                placed = True
            else:
                # Pairwise distance check
                dists = np.sqrt(np.sum((pos[:i] - np.array([x, y]))**2, axis=1))
                radii_sums = radius[:i] + radius[i]
                if np.all(dists >= radii_sums + 0.1): # add small clearance
                    pos[i] = [x, y]
                    placed = True
            attempts += 1
            
        if not placed:
            # Fallback if box is too crowded: place randomly and let collision resolution resolve it
            if split is None:
                pos[i] = [np.random.uniform(radius[i], width - radius[i]), np.random.uniform(radius[i], height - radius[i])]
            elif split[i] == 'left':
                pos[i] = [np.random.uniform(radius[i], width / 2.0 - radius[i] - 1.0), np.random.uniform(radius[i], height - radius[i])]
            else:
                pos[i] = [np.random.uniform(width / 2.0 + radius[i] + 1.0, width - radius[i]), np.random.uniform(radius[i], height - radius[i])]
    return pos

def init_particles(args):
    """
    Initializes particles with positions and velocities based on the chosen profile.
    """
    N = args.particles
    W = args.box_width
    H = args.box_height
    r = args.radius
    
    radii = np.full(N, r)
    masses = np.ones(N) # Uniform mass
    
    # Position layout split check
    split = None
    if args.initial_state == "hot-cold":
        split = ['left' if i < N // 2 else 'right' for i in range(N)]
        
    pos = initialize_positions(N, radii, W, H, split=split)
    vel = np.zeros((N, 2))
    
    # Baseline speed parameter (temperature = 5.0 reference scale)
    v_base = np.sqrt(2.0 * 5.0) 
    
    if args.initial_state == "mono-energetic":
        # All particles start with identical speed but random direction
        angles = np.random.uniform(0, 2 * np.pi, N)
        vel[:, 0] = v_base * np.cos(angles)
        vel[:, 1] = v_base * np.sin(angles)
        
    elif args.initial_state == "hot-cold":
        # Left half start hot, right half start cold/near-rest
        angles = np.random.uniform(0, 2 * np.pi, N)
        for i in range(N):
            v_mag = v_base * 2.0 if i < N // 2 else v_base * 0.1
            vel[i, 0] = v_mag * np.cos(angles[i])
            vel[i, 1] = v_mag * np.sin(angles[i])
            
    elif args.initial_state == "single-bullet":
        # Particle 0 gets all kinetic energy, all others start stationary
        # Total energy E = 1/2 * m * v^2 = N * T_target (T=5.0) -> v_bullet = sqrt(2 * N * T_target)
        v_bullet = np.sqrt(2.0 * N * 5.0)
        angle = np.random.uniform(0, 2 * np.pi)
        vel[0, 0] = v_bullet * np.cos(angle)
        vel[0, 1] = v_bullet * np.sin(angle)
        # All other particles have vel = (0,0)
        
    return pos, vel, masses, radii

def update_physics(pos, vel, mass, radius, width, height, dt):
    """
    Updates the simulation physics by one dt interval.
    Processes wall reflections, pairwise collisions, and overlap correction.
    """
    N = len(pos)
    
    # 1. Coordinate update
    pos += vel * dt
    
    # 2. Wall Collisions (reflection and correction)
    # Left wall
    left_mask = pos[:, 0] - radius < 0
    pos[left_mask, 0] = radius[left_mask]
    vel[left_mask, 0] = np.abs(vel[left_mask, 0])
    
    # Right wall
    right_mask = pos[:, 0] + radius > width
    pos[right_mask, 0] = width - radius[right_mask]
    vel[right_mask, 0] = -np.abs(vel[right_mask, 0])
    
    # Bottom wall
    bottom_mask = pos[:, 1] - radius < 0
    pos[bottom_mask, 1] = radius[bottom_mask]
    vel[bottom_mask, 1] = np.abs(vel[bottom_mask, 1])
    
    # Top wall
    top_mask = pos[:, 1] + radius > height
    pos[top_mask, 1] = height - radius[top_mask]
    vel[top_mask, 1] = -np.abs(vel[top_mask, 1])
    
    # 3. Particle-Particle Collisions
    # Compute pairwise coordinate differences
    dx = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    dist_sq = np.sum(dx**2, axis=-1)
    
    r_sum = radius[:, np.newaxis] + radius[np.newaxis, :]
    r_sum_sq = r_sum**2
    
    # Overlap condition
    overlap_mask = dist_sq < r_sum_sq
    
    # Check if they are moving towards each other to prevent duplicate collisions
    dv = vel[:, np.newaxis, :] - vel[np.newaxis, :, :]
    rel_vel_dot_pos = np.sum(dv * dx, axis=-1)
    
    colliding = overlap_mask & (rel_vel_dot_pos < 0)
    
    # Filter for upper triangle (each pair evaluated once)
    i_idx, j_idx = np.where(colliding & (np.arange(N)[:, np.newaxis] < np.arange(N)[np.newaxis, :]))
    
    # Resolve momentum exchange and position overlap
    for i, j in zip(i_idx, j_idx):
        x_diff = pos[i] - pos[j]
        d_sq = dist_sq[i, j]
        d = np.sqrt(d_sq)
        if d == 0:
            continue
        v_diff = vel[i] - vel[j]
        
        m_i, m_j = mass[i], mass[j]
        m_sum = m_i + m_j
        
        # Momentum transfer projection
        impulse = (2.0 * m_j / m_sum) * np.dot(v_diff, x_diff) / d_sq * x_diff
        vel[i] -= impulse
        vel[j] += impulse * (m_i / m_j)
        
        # Position projection correction (prevent sticking)
        overlap = r_sum[i, j] - d
        if overlap > 0:
            push = (overlap / m_sum) * (x_diff / d)
            pos[i] += push * m_j
            pos[j] -= push * m_i

def calc_statistics(speeds, N, mass):
    """
    Computes thermodynamic metrics, Shannon entropy of speed distribution,
    and runs a Chi-squared goodness-of-fit test against the theoretical Rayleigh distribution.
    """
    m = mass[0]
    mean_v2 = np.mean(speeds**2)
    # Temperature: 1/2 * m * <v^2> = k_B * T (using k_B = 1)
    T = 0.5 * m * mean_v2
    sigma = np.sqrt(T / m)
    
    mean_speed = np.mean(speeds)
    total_energy = 0.5 * np.sum(m * (speeds**2))
    
    # Configure speed distribution bins (0 to 3.5 * sigma)
    num_bins = 10
    edges = np.linspace(0, 3.5 * sigma, num_bins + 1)
    
    # Add overflow bin boundary [3.5 * sigma, inf]
    bins_with_inf = list(edges) + [np.inf]
    observed_counts, _ = np.histogram(speeds, bins=bins_with_inf)
    
    # Probabilities
    probs = observed_counts / N
    entropy = -np.sum(probs * np.log(probs + 1e-9))
    
    # Expected probabilities from Rayleigh CDF: F(v) = 1 - exp(-v^2 / (2 * sigma^2))
    expected_probs = []
    for k in range(num_bins):
        v_start = edges[k]
        v_end = edges[k+1]
        p = np.exp(-v_start**2 / (2.0 * sigma**2)) - np.exp(-v_end**2 / (2.0 * sigma**2))
        expected_probs.append(p)
    # Overflow bin probability
    expected_probs.append(np.exp(-edges[-1]**2 / (2.0 * sigma**2)))
    
    expected_probs = np.array(expected_probs)
    # Clip to avoid numerical zero errors in Chi-squared division
    expected_probs = np.clip(expected_probs, 1e-5, None)
    expected_probs = expected_probs / np.sum(expected_probs)
    expected_counts = expected_probs * N
    
    # Perform Chi-squared test
    try:
        chi_stat, p_val = chisquare(observed_counts, f_exp=expected_counts)
    except Exception:
        chi_stat, p_val = 0.0, 0.0
        
    return {
        "temperature": T,
        "total_energy": total_energy,
        "mean_speed": mean_speed,
        "sigma": sigma,
        "entropy": entropy,
        "chi_stat": chi_stat,
        "p_value": p_val,
        "observed_counts": observed_counts,
        "expected_counts": expected_counts,
        "edges": edges
    }

def main():
    args = parse_args()
    
    # Initialize particles
    pos, vel, mass, radius = init_particles(args)
    N = len(pos)
    
    # Grid dimensions matching physical bounds for rendering
    grid_cols = int(args.box_width)
    grid_rows = int(args.box_height)
    
    # Simulation timing setup
    frame_time = 1.0 / args.fps
    sub_steps = 10
    dt = frame_time / sub_steps
    
    # CSV history log
    history = []
    
    # Terminal rendering initialization (Clear screen and hide cursor)
    sys.stdout.write("\033[2J\033[H\033[?25l")
    sys.stdout.flush()
    
    start_sim_time = time.time()
    step = 0
    
    try:
        while True:
            t_frame_start = time.time()
            elapsed_time = t_frame_start - start_sim_time
            
            # Physics updates (multiple sub-steps per visual frame)
            for _ in range(sub_steps):
                update_physics(pos, vel, mass, radius, args.box_width, args.box_height, dt)
                
            # Perform calculations
            speeds = np.linalg.norm(vel, axis=1)
            mean_speed = np.mean(speeds) if len(speeds) > 0 else 1.0
            stats = calc_statistics(speeds, N, mass)
            
            # Record step history
            history.append({
                "step": step,
                "time": elapsed_time,
                "temperature": stats["temperature"],
                "entropy": stats["entropy"],
                "chi_sq": stats["chi_stat"],
                "p_value": stats["p_value"]
            })
            
            # Calculate actual loop FPS
            t_frame_end = time.time()
            fps_actual = 1.0 / max(1e-5, t_frame_end - t_frame_start)
            
            # Initialize characters grid
            grid = [[" " for _ in range(grid_cols)] for _ in range(grid_rows)]
            
            # Draw particle locations in grid (colored by speed)
            for i in range(N):
                c = int(pos[i, 0] / args.box_width * (grid_cols - 1))
                r = int((args.box_height - pos[i, 1]) / args.box_height * (grid_rows - 1))
                
                c = max(0, min(grid_cols - 1, c))
                r = max(0, min(grid_rows - 1, r))
                
                speed = np.linalg.norm(vel[i])
                if speed > 1.8 * mean_speed:
                    grid[r][c] = "\033[91mO\033[0m" # Hot: Red 'O'
                elif speed > 0.8 * mean_speed:
                    grid[r][c] = "\033[93mo\033[0m" # Warm: Yellow 'o'
                else:
                    grid[r][c] = "\033[94m.\033[0m" # Cold: Blue '.'
            
            # Formulate stats and histogram lines for Right Panel
            right_lines = []
            right_lines.append(f"Step: {step:<8} | Time: {elapsed_time:.2f}s")
            right_lines.append(f"FPS: {fps_actual:.1f}  (Target: {args.fps})")
            right_lines.append(f"Particles (N): {N:<5} | Radius: {args.radius}")
            right_lines.append("")
            right_lines.append("--- Thermodynamics & Mechanics ---")
            right_lines.append(f"Total Energy: {stats['total_energy']:.4f}")
            right_lines.append(f"Temperature : {stats['temperature']:.4f}")
            right_lines.append(f"Mean Speed  : {stats['mean_speed']:.4f}")
            right_lines.append(f"Entropy (H) : {stats['entropy']:.4f}")
            right_lines.append("")
            right_lines.append("--- Statistical Mechanics ---")
            
            # Chi-squared Rayleigh distribution fit status
            verdict = "\033[92mRayleigh (Equilibrium)\033[0m" if stats['p_value'] > 0.05 else "\033[91mNon-Equilibrium\033[0m"
            right_lines.append(f"P-Value     : {stats['p_value']:.4f}")
            right_lines.append(f"State       : {verdict}")
            right_lines.append("")
            right_lines.append("Speed Distribution Histogram:")
            right_lines.append("  (Cyan # = Obs, Red | = Exp, Yellow X = Overlap)")
            
            # Build histogram visual lines
            edges = stats['edges']
            obs = stats['observed_counts']
            exp = stats['expected_counts']
            max_val = max(np.max(obs), np.max(exp))
            hist_scale = 22.0 / max(1, max_val) # Fits within right panel width constraints
            
            for k in range(len(obs)):
                obs_len = int(obs[k] * hist_scale)
                exp_len = int(exp[k] * hist_scale)
                
                bar_chars = []
                max_len = max(obs_len, exp_len)
                for idx in range(max_len + 1):
                    if idx < obs_len and idx == exp_len:
                        bar_chars.append("\033[93mX\033[0m")
                    elif idx < obs_len:
                        bar_chars.append("\033[96m#\033[0m")
                    elif idx == exp_len:
                        bar_chars.append("\033[91m|\033[0m")
                    else:
                        bar_chars.append(" ")
                        
                bar_str = "".join(bar_chars).rstrip()
                display_len = max_len + 1
                padding = " " * max(0, 24 - display_len)
                
                if k < len(obs) - 1:
                    bin_label = f"{edges[k]:3.1f}-{edges[k+1]:3.1f}"
                else:
                    bin_label = f"{edges[-1]:3.1f}+  "
                
                right_lines.append(f"  {bin_label}: {bar_str}{padding}({obs[k]:3d} vs {int(exp[k]):3d})")
                
            # Compile terminal render lines
            render_lines = []
            render_lines.append("=== MAXWELL-BOLTZMANN 2D EVOLUTION SIMULATION ===".center(grid_cols + 50) + "\033[K")
            render_lines.append("-" * (grid_cols + 50) + "\033[K")
            
            box_top = "+" + "-" * grid_cols + "+"
            box_bottom = "+" + "-" * grid_cols + "+"
            
            right_idx = 0
            render_lines.append(f"{box_top}  {right_lines[right_idx]}\033[K")
            right_idx += 1
            
            for r in range(grid_rows):
                row_str = "".join(grid[r])
                right_str = right_lines[right_idx] if right_idx < len(right_lines) else ""
                render_lines.append(f"|{row_str}|  {right_str}\033[K")
                right_idx += 1
                
            while right_idx < len(right_lines) or right_idx == len(right_lines):
                prefix = box_bottom if right_idx == len(right_lines) - 1 or right_idx == 1 else " " * (grid_cols + 2)
                right_str = right_lines[right_idx] if right_idx < len(right_lines) else ""
                render_lines.append(f"{prefix}  {right_str}\033[K")
                right_idx += 1
                
            # Move cursor to home and overwrite screen
            sys.stdout.write("\033[H" + "\n".join(render_lines) + "\n")
            sys.stdout.flush()
            
            # Step increment and checks
            step += 1
            if args.steps > 0 and step >= args.steps:
                break
                
            # Sync rendering rate
            t_frame_spent = time.time() - t_frame_start
            sleep_time = max(0.001, frame_time - t_frame_spent)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        pass
    finally:
        # Restore terminal defaults
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
        print("Simulation stopped.")
        
        # Export history data if file specified
        if args.export and len(history) > 0:
            print(f"Exporting metrics history to {args.export}...")
            try:
                with open(args.export, mode='w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=["step", "time", "temperature", "entropy", "chi_sq", "p_value"])
                    writer.writeheader()
                    writer.writerows(history)
                print("Export completed successfully.")
            except Exception as e:
                print(f"Error during export: {e}")

if __name__ == "__main__":
    main()
