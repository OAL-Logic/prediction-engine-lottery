"""
Non-Euclidean Geometry Module 💠
===============================
Maps lottery numbers into 3D geometric structures to find 'Higher-Dimensional Neighbors'.
"""

import math
from typing import Any

def get_dodecahedron_neighbors(n: int, max_n: int = 60) -> list[int]:
    """
    Returns geometric neighbors of a number mapped to a Dodecahedron.
    
    A dodecahedron has 20 vertices. We map n -> vertex by (n % 20).
    The adjacency graph of a dodecahedron's vertices is used to find neighbors.
    """
    # Adjacency list for a dodecahedron's 20 vertices (0-19)
    # Each vertex has exactly 3 neighbors
    adj = {
        0: [1, 4, 10],   1: [0, 2, 7],    2: [1, 3, 9],    3: [2, 4, 12],
        4: [0, 3, 5],    5: [4, 6, 14],   6: [5, 7, 11],   7: [1, 6, 8],
        8: [7, 9, 17],   9: [2, 8, 13],   10: [0, 11, 19], 11: [6, 10, 12],
        12: [3, 11, 13], 13: [9, 12, 14], 14: [5, 13, 15], 15: [14, 16, 19],
        16: [15, 17, 18], 17: [8, 16, 18], 18: [16, 17, 19], 19: [10, 15, 18]
    }
    
    vertex = (n - 1) % 20
    v_neighbors = adj.get(vertex, [])
    
    # Map vertices back to possible numbers in the range
    # e.g., if vertex is 1, neighbors might be 1, 21, 41 (if max_n >= 41)
    results = []
    for vn in v_neighbors:
        for offset in [0, 20, 40, 60]:
            candidate = vn + 1 + offset
            if candidate <= max_n and candidate != n:
                results.append(candidate)
    
    return results


class BoardGeometry:
    """
    Standard 2D Grid Geometry for lottery boards.
    """
    def __init__(self, max_n: int, cols: int = 10):
        self.max_n = max_n
        self.cols = cols
        self.rows = math.ceil(max_n / cols)

    def get_coords(self, n: int) -> tuple[int, int]:
        """1-based (row, col)"""
        return ((n - 1) // self.cols + 1, (n - 1) % self.cols + 1)

    def is_frame(self, n: int) -> bool:
        r, c = self.get_coords(n)
        return r == 1 or r == self.rows or c == 1 or c == self.cols

    def get_neighbors(self, n: int) -> list[int]:
        """Get 2D grid neighbors (up, down, left, right, diagonals)"""
        r, c = self.get_coords(n)
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 1 <= nr <= self.rows and 1 <= nc <= self.cols:
                    candidate = (nr - 1) * self.cols + nc
                    if candidate <= self.max_n:
                        neighbors.append(candidate)
        return sorted(list(set(neighbors)))


def get_manifold_coords(n: int, rules: Any, manifold: str = "sphere") -> tuple[float, float, float]:
    """
    Maps a lottery number to 3D coordinates based on the selected manifold.
    """
    lo, hi = rules.number_range
    cols = rules.board_cols or 10
    rows = math.ceil((hi - lo + 1) / cols)
    
    # Standard grid mapping (0-based)
    val = n - lo
    row = val // cols
    col = val % cols
    
    if manifold == "cylinder":
        # Wrap columns circularly
        theta = 2.0 * math.pi * (col + 0.5) / cols
        x = math.cos(theta)
        y = math.sin(theta)
        z = (row + 0.5) / rows
        return x, y, z
    elif manifold == "hexagonal":
        # Offset odd rows
        x = col + 0.5 * (row % 2)
        y = row * (math.sqrt(3.0) / 2.0)
        return x, y, 0.0
    else: # default "sphere"
        # Wrap columns horizontally, rows vertically
        theta = 2.0 * math.pi * (col + 0.5) / cols
        phi = math.pi * (row + 0.5) / rows
        x = math.sin(phi) * math.cos(theta)
        y = math.sin(phi) * math.sin(theta)
        z = math.cos(phi)
        return x, y, z


def calculate_symmetry_metrics(ticket: list[int], rules: Any, manifold: str = "sphere") -> dict[str, Any]:
    """
    Calculates Center of Mass, Vector Balance (Resonance), and Reflection Symmetry for a ticket.
    """
    if not ticket:
        return {
            "center_of_mass": (0.0, 0.0, 0.0),
            "resonance": 0.0,
            "reflection_h": 0.0,
            "reflection_v": 0.0,
            "symmetry_grade": 0.0
        }
        
    coords = [get_manifold_coords(n, rules, manifold) for n in ticket]
    
    # 1. Center of Mass
    xs, ys, zs = zip(*coords)
    cm_x = float(sum(xs) / len(ticket))
    cm_y = float(sum(ys) / len(ticket))
    cm_z = float(sum(zs) / len(ticket))
    
    # 2. Vector Balance (Resonance)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_z = sum(zs)
    magnitude = math.sqrt(sum_x**2 + sum_y**2 + sum_z**2)
    norm_mag = magnitude / len(ticket)
    # Higher symmetry -> lower magnitude -> higher balance score
    resonance = 1.0 - norm_mag
    
    # 3. Reflection Symmetry (2D grid coordinate reflections)
    lo, hi = rules.number_range
    cols = rules.board_cols or 10
    rows = math.ceil((hi - lo + 1) / cols)
    
    cells = set()
    for n in ticket:
        val = n - lo
        cells.add((val // cols, val % cols))
        
    # Check vertical mirror symmetry (flip column)
    v_matches = 0
    for r, c in cells:
        mirrored_c = cols - 1 - c
        if (r, mirrored_c) in cells:
            v_matches += 1
    reflection_v = v_matches / len(cells) if cells else 0.0
    
    # Check horizontal mirror symmetry (flip row)
    h_matches = 0
    for r, c in cells:
        mirrored_r = rows - 1 - r
        if (mirrored_r, c) in cells:
            h_matches += 1
    reflection_h = h_matches / len(cells) if cells else 0.0
    
    # Composite symmetry grade
    symmetry_grade = (resonance * 0.5 + reflection_v * 0.25 + reflection_h * 0.25) * 100.0
    
    return {
        "center_of_mass": (cm_x, cm_y, cm_z),
        "resonance": resonance,
        "reflection_h": reflection_h,
        "reflection_v": reflection_v,
        "symmetry_grade": symmetry_grade
    }

