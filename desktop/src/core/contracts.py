"""
Service Contracts & Protocols
=============================
Formal interface contracts connecting the PySide6 Desktop UI to the
headless core computational engine (`engine/`) and CLI pipelines.
"""

from __future__ import annotations

from typing import Protocol, List, Dict, Optional, Generator, Tuple, Callable
import numpy as np

from desktop.src.core.models import (
    GameSchema, FilterNode, ToleranceRule, WheelingConfig,
    TicketReceipt, GenerationTelemetry, ProfileBundle
)


class IGameRegistryService(Protocol):
    """Protocol for querying game metadata and active lottery adapters."""
    
    def list_games(self, only_available: bool = True) -> List[GameSchema]:
        """Lists all supported games from the engine registry."""
        ...

    def get_game(self, game_id: str) -> Optional[GameSchema]:
        """Retrieves schema for a specific game ID."""
        ...


class ICombinatorialEngine(Protocol):
    """
    Protocol for high-performance combinatorial generation and filtering.
    Must support chunked lazy streaming to prevent RAM exhaustion when handling
    large spaces (e.g. Mega-Sena ~50M, Powerball ~292M).
    """

    def stream_combinations(
        self,
        pool: List[int],
        pick_count: int,
        chunk_size: int = 500_000
    ) -> Generator[np.ndarray, None, None]:
        """Generates candidate combinations as chunked 2D NumPy arrays."""
        ...

    def evaluate_filters_vectorized(
        self,
        combinations_chunk: np.ndarray,
        active_filters: List[FilterNode],
        rules: Any
    ) -> Tuple[np.ndarray, Dict[str, int]]:
        """
        Evaluates active filters across a 2D chunk using vectorized NumPy logic.
        Returns:
            pass_matrix: 2D boolean array of shape (num_combos, num_filters)
            elimination_counts: Per-filter count of lines removed
        """
        ...

    def apply_tolerance_filter(
        self,
        pass_matrix: np.ndarray,
        tolerance: ToleranceRule
    ) -> np.ndarray:
        """
        Applies Fault Tolerance (Error Allowance) to the boolean pass matrix.
        Returns 1D boolean mask of surviving combinations.
        """
        ...


class IWheelingEngine(Protocol):
    """Protocol for mathematical covering designs and reduction systems."""

    def generate_wheel(
        self,
        config: WheelingConfig
    ) -> List[List[int]]:
        """Computes covering design lines fulfilling the target guarantee."""
        ...

    def compute_guarantee_report(
        self,
        config: WheelingConfig
    ) -> Dict[str, Any]:
        """Calculates win probabilities across all prize match tiers."""
        ...


class IPredictionEnsembleService(Protocol):
    """Protocol for running multi-strategy ensemble forecasts."""

    def predict_pool(
        self,
        game_id: str,
        weights: Dict[str, float],
        top_k: int
    ) -> List[int]:
        """Produces a recommended candidate number pool."""
        ...

    def scan_diagnostic_regime(
        self,
        game_id: str
    ) -> Dict[str, Any]:
        """Executes 6-layer diagnostic scan (GO/NO-GO verdict, entropy, gap pressure)."""
        ...


class IProfileManagerService(Protocol):
    """Protocol for bidirectional profile storage and preset management."""

    def load_desktop_profile(self, path: str) -> ProfileBundle:
        """Loads a rich .json desktop workspace profile."""
        ...

    def save_desktop_profile(self, profile: ProfileBundle, path: str) -> None:
        """Saves a rich .json desktop workspace profile."""
        ...

    def export_cli_preset(self, profile: ProfileBundle, path: str) -> None:
        """Exports headless CLI strategy preset compatible with `lottery suggest`."""
        ...

    def import_cli_preset(self, path: str) -> ProfileBundle:
        """Imports an engine CLI .yaml preset into a desktop profile."""
        ...
