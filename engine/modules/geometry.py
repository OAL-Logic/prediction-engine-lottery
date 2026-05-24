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
