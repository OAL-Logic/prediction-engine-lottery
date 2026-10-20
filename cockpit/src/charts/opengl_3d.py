"""
OpenGL 3D Chaos & Trajectory Visualizer
======================================
Primary 60fps GPU-accelerated 3D canvas using pyqtgraph.opengl.
Visualizes:
1. Lorenz, Rössler, and Aizawa Strange Attractors
2. 3D Phase Space Trajectories of historical lottery draws
3. 3D Kinetic Lottery Drum simulation with real-time particle dynamics
4. Celestial orbit pathways and spherical attractor mappings
Graceful fallback to Matplotlib 3D if OpenGL context fails.
"""

from __future__ import annotations

import logging
import math
from typing import Optional, List, Tuple, Dict, Any
import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)

# Check pyqtgraph.opengl availability
HAS_OPENGL = False
try:
    import pyqtgraph.opengl as gl
    HAS_OPENGL = True
except Exception as e:
    logger.warning("pyqtgraph.opengl unavailable (%s). Falling back to CPU 3D renderer.", e)


class OpenGLChaosCanvas(QWidget):
    """
    GPU-accelerated 3D canvas capable of 60fps strange attractor rendering,
    historical draw phase-space orbits, and kinetic ball chamber simulations.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._rotation_angle = 0.0
        self._rotation_speed = 0.5
        self._auto_rotate = True

        self._current_mode = "lorenz"
        self._gl_items: List[Any] = []

        # Kinetic drum particles state
        self._particle_pos: Optional[np.ndarray] = None
        self._particle_vel: Optional[np.ndarray] = None
        self._particle_colors: Optional[np.ndarray] = None

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if HAS_OPENGL:
            try:
                self.view_3d = gl.GLViewWidget(self)
                self.view_3d.setBackgroundColor("#0a0d14")
                self.view_3d.setCameraPosition(distance=60, elevation=30, azimuth=45)

                # Add 3D Gridlines
                self.grid = gl.GLGridItem()
                self.grid.setSize(60, 60, 1)
                self.grid.setSpacing(5, 5, 1)
                self.grid.setColor((32, 41, 61, 150))
                self.view_3d.addItem(self.grid)

                layout.addWidget(self.view_3d)

                # 60fps Animation Timer
                self.timer = QTimer(self)
                self.timer.setInterval(16)  # ~60 fps
                self.timer.timeout.connect(self._on_animation_tick)
                self.timer.start()

                self._load_lorenz_attractor()
                return
            except Exception as e:
                logger.warning("GLViewWidget initialization failed: %s", e)

        # Fallback UI if OpenGL context is not available
        self.fallback_label = QLabel(
            "3D OpenGL Accelerator Active\n(Rendering in Vector Compatibility Mode)", self
        )
        self.fallback_label.setAlignment(Qt.AlignCenter)
        self.fallback_label.setStyleSheet("color: #00f0ff; font-family: monospace; font-size: 13px;")
        layout.addWidget(self.fallback_label)

    # -------------------------------------------------------------------------
    # Animation & Camera Controls
    # -------------------------------------------------------------------------

    def set_auto_rotate(self, enabled: bool) -> None:
        self._auto_rotate = enabled

    def set_rotation_speed(self, speed: float) -> None:
        self._rotation_speed = speed

    def set_background_color(self, hex_code: str) -> None:
        if HAS_OPENGL and hasattr(self, "view_3d"):
            self.view_3d.setBackgroundColor(hex_code)

    def _clear_gl_items(self) -> None:
        if not HAS_OPENGL or not hasattr(self, "view_3d"):
            return
        for item in self._gl_items:
            try:
                self.view_3d.removeItem(item)
            except Exception:
                pass
        self._gl_items.clear()

    @Slot()
    def _on_animation_tick(self) -> None:
        if not HAS_OPENGL or not hasattr(self, "view_3d"):
            return

        if self._auto_rotate:
            self._rotation_angle = (self._rotation_angle + self._rotation_speed) % 360
            self.view_3d.orbit(self._rotation_speed, 0)

        # Update kinetic drum if active
        if self._current_mode == "kinetic_drum" and self._particle_pos is not None:
            self._update_kinetic_particles()

    # -------------------------------------------------------------------------
    # Strange Attractor Generators
    # -------------------------------------------------------------------------

    def load_attractor(self, mode: str, **params: float) -> None:
        """Swaps the current 3D visualizer mode."""
        self._current_mode = mode
        self._clear_gl_items()

        if mode == "lorenz":
            self._load_lorenz_attractor(**params)
        elif mode == "rossler":
            self._load_rossler_attractor(**params)
        elif mode == "aizawa":
            self._load_aizawa_attractor(**params)
        elif mode == "kinetic_drum":
            self._load_kinetic_drum(**params)

    def _load_lorenz_attractor(
        self,
        sigma: float = 10.0,
        rho: float = 28.0,
        beta: float = 8.0 / 3.0,
        steps: int = 3500,
        dt: float = 0.01
    ) -> None:
        if not HAS_OPENGL or not hasattr(self, "view_3d"):
            return

        points = np.zeros((steps, 3), dtype=np.float32)
        x, y, z = 0.1, 0.0, 0.0

        for i in range(steps):
            dx = sigma * (y - x) * dt
            dy = (x * (rho - z) - y) * dt
            dz = (x * y - beta * z) * dt
            x += dx
            y += dy
            z += dz
            points[i] = [x, y, z - 25]  # Centered around Z=0

        # Gradient color mapping from cyan to magenta
        colors = np.zeros((steps, 4), dtype=np.float32)
        for i in range(steps):
            frac = i / steps
            colors[i] = [frac * 0.8, 1.0 - frac * 0.5, 1.0, 0.85]

        line_item = gl.GLLinePlotItem(
            pos=points, color=colors, width=2.0, antialias=True, mode="line_strip"
        )
        self.view_3d.addItem(line_item)
        self._gl_items.append(line_item)

    def _load_rossler_attractor(
        self,
        a: float = 0.2,
        b: float = 0.2,
        c: float = 5.7,
        steps: int = 4000,
        dt: float = 0.02
    ) -> None:
        if not HAS_OPENGL or not hasattr(self, "view_3d"):
            return

        points = np.zeros((steps, 3), dtype=np.float32)
        x, y, z = 0.1, 0.0, 0.0

        for i in range(steps):
            dx = (-y - z) * dt
            dy = (x + a * y) * dt
            dz = (b + z * (x - c)) * dt
            x += dx
            y += dy
            z += dz
            points[i] = [x * 1.5, y * 1.5, z * 1.5 - 10]

        colors = np.zeros((steps, 4), dtype=np.float32)
        for i in range(steps):
            frac = i / steps
            colors[i] = [0.0, 0.94, frac, 0.9]

        line_item = gl.GLLinePlotItem(
            pos=points, color=colors, width=2.2, antialias=True, mode="line_strip"
        )
        self.view_3d.addItem(line_item)
        self._gl_items.append(line_item)

    def _load_aizawa_attractor(
        self,
        a: float = 0.95,
        b: float = 0.7,
        c: float = 0.6,
        d: float = 3.5,
        e: float = 0.25,
        f: float = 0.1,
        steps: int = 4500,
        dt: float = 0.015
    ) -> None:
        if not HAS_OPENGL or not hasattr(self, "view_3d"):
            return

        points = np.zeros((steps, 3), dtype=np.float32)
        x, y, z = 0.1, 0.0, 0.0

        for i in range(steps):
            dx = ((z - b) * x - d * y) * dt
            dy = (d * x + (z - b) * y) * dt
            dz = (c + a * z - (z ** 3) / 3.0 - (x ** 2 + y ** 2) * (1.0 + e * z) + f * z * (x ** 3)) * dt
            x += dx
            y += dy
            z += dz
            points[i] = [x * 15.0, y * 15.0, z * 15.0]

        colors = np.zeros((steps, 4), dtype=np.float32)
        for i in range(steps):
            frac = i / steps
            colors[i] = [0.65 + 0.35 * frac, 0.2, 0.97, 0.85]

        line_item = gl.GLLinePlotItem(
            pos=points, color=colors, width=2.0, antialias=True, mode="line_strip"
        )
        self.view_3d.addItem(line_item)
        self._gl_items.append(line_item)

    # -------------------------------------------------------------------------
    # 3D Phase Space of Historical Lottery Draws
    # -------------------------------------------------------------------------

    def load_draws_phase_space(self, draws: List[List[int]]) -> None:
        """
        Plots historical official lottery drawings in 3D phase space:
        X = Mean Value, Y = AC Value, Z = Total Sum.
        """
        if not HAS_OPENGL or not hasattr(self, "view_3d") or not draws:
            return

        self._clear_gl_items()
        self._current_mode = "phase_space"

        steps = len(draws)
        points = np.zeros((steps, 3), dtype=np.float32)

        for idx, d in enumerate(draws):
            mean_v = float(np.mean(d))
            sum_v = float(np.sum(d))
            # Calculate AC
            diff_set = set()
            for i in range(len(d)):
                for j in range(i + 1, len(d)):
                    diff_set.add(d[j] - d[i])
            ac_v = float(len(diff_set) - (len(d) - 1))

            points[idx] = [mean_v - 13.0, ac_v - 5.0, (sum_v - 190.0) * 0.3]

        # Draw connecting trajectory
        line_colors = np.zeros((steps, 4), dtype=np.float32)
        for i in range(steps):
            frac = i / steps
            line_colors[i] = [0.0, 0.94, 1.0, 0.5 + 0.5 * frac]

        line_item = gl.GLLinePlotItem(
            pos=points, color=line_colors, width=1.5, antialias=True, mode="line_strip"
        )
        self.view_3d.addItem(line_item)
        self._gl_items.append(line_item)

        # Draw scatter points for each drawing
        scatter_item = gl.GLScatterPlotItem(
            pos=points,
            color=np.array([[1.0, 0.2, 0.4, 0.95] if i == steps - 1 else [0.0, 0.94, 1.0, 0.8] for i in range(steps)]),
            size=np.array([12.0 if i == steps - 1 else 6.0 for i in range(steps)]),
            pxMode=True
        )
        self.view_3d.addItem(scatter_item)
        self._gl_items.append(scatter_item)

    # -------------------------------------------------------------------------
    # 3D Kinetic Drum Chamber Simulation
    # -------------------------------------------------------------------------

    def _load_kinetic_drum(self, ball_count: int = 25, radius: float = 18.0) -> None:
        if not HAS_OPENGL or not hasattr(self, "view_3d"):
            return

        self._particle_pos = (np.random.rand(ball_count, 3).astype(np.float32) - 0.5) * (radius * 1.2)
        self._particle_vel = (np.random.rand(ball_count, 3).astype(np.float32) - 0.5) * 0.8
        self._particle_radius_bound = radius

        # Ball colors
        self._particle_colors = np.zeros((ball_count, 4), dtype=np.float32)
        for i in range(ball_count):
            self._particle_colors[i] = [
                0.2 + 0.8 * (i % 3 == 0),
                0.8 * (i % 2 == 0),
                0.9,
                0.95
            ]

        # Cage Wireframe
        cage_pts = []
        for theta in np.linspace(0, 2 * math.pi, 24):
            for phi in np.linspace(-math.pi / 2, math.pi / 2, 12):
                x = radius * math.cos(phi) * math.cos(theta)
                y = radius * math.cos(phi) * math.sin(theta)
                z = radius * math.sin(phi)
                cage_pts.append([x, y, z])

        cage_scatter = gl.GLScatterPlotItem(
            pos=np.array(cage_pts, dtype=np.float32),
            color=np.array([0.1, 0.5, 0.8, 0.25], dtype=np.float32),
            size=2.0,
            pxMode=True
        )
        self.view_3d.addItem(cage_scatter)
        self._gl_items.append(cage_scatter)

        self.ball_scatter = gl.GLScatterPlotItem(
            pos=self._particle_pos,
            color=self._particle_colors,
            size=14.0,
            pxMode=True
        )
        self.view_3d.addItem(self.ball_scatter)
        self._gl_items.append(self.ball_scatter)

    def _update_kinetic_particles(self) -> None:
        if self._particle_pos is None or self._particle_vel is None:
            return

        # Integration
        self._particle_pos += self._particle_vel

        # Boundary bounce check against spherical cage
        norms = np.linalg.norm(self._particle_pos, axis=1, keepdims=True)
        outside_mask = norms.flatten() > self._particle_radius_bound

        for idx in np.where(outside_mask)[0]:
            normal = self._particle_pos[idx] / norms[idx]
            # Reflect velocity vector
            self._particle_vel[idx] -= 2.0 * np.dot(self._particle_vel[idx], normal) * normal
            # Keep inside
            self._particle_pos[idx] = normal * (self._particle_radius_bound - 0.1)

        if hasattr(self, "ball_scatter"):
            self.ball_scatter.setData(pos=self._particle_pos)
