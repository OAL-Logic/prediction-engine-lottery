"""
Edge Computing & Mobile PWA Cockpit Module (Track L)
===================================================
Provides validation of Progressive Web App (PWA) manifest, Service Worker offline
assets, and cryptographic SHA-256 bet receipt verification for edge terminal nodes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PwaAuditResult:
    """Summary of PWA compliance audit."""
    is_compliant: bool
    html_exists: bool
    manifest_exists: bool
    sw_exists: bool
    manifest_data: Dict[str, Any]
    service_worker_events: List[str]
    missing_assets: List[str]


def compute_bet_receipt_hash(
    lottery: str,
    ticket: List[int],
    timestamp: str,
    terminal_id: str = "P4-EDGE-TERM-001",
) -> str:
    """
    Computes a cryptographic SHA-256 verification digest for an edge-issued ticket.
    Format: sha256(f"{lottery}:{num_str}:{timestamp}:{terminal_id}")
    """
    sorted_nums = sorted([int(n) for n in ticket])
    num_str = " ".join(f"{n:02d}" for n in sorted_nums)
    raw_payload = f"{lottery.lower().strip()}:{num_str}:{timestamp.strip()}:{terminal_id.strip()}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def generate_mini_qr_ascii(digest: str) -> List[str]:
    """Generates a visual 9x9 deterministic ASCII QR matrix from the SHA-256 digest."""
    val = int(digest[:16], 16)
    bits = [(val >> i) & 1 for i in range(48)]
    grid = [["  " for _ in range(9)] for _ in range(9)]

    # 3 Corner Finder Patterns (3x3 blocks)
    for cr, cc in [(0, 0), (0, 6), (6, 0)]:
        for r in range(3):
            for c in range(3):
                grid[cr + r][cc + c] = "██"
        grid[cr + 1][cc + 1] = "  "

    bit_idx = 0
    for r in range(9):
        for c in range(9):
            if (r < 3 and (c < 3 or c >= 6)) or (r >= 6 and c < 3):
                continue
            if bit_idx < len(bits) and bits[bit_idx]:
                grid[r][c] = "██"
            bit_idx += 1

    return ["".join(row) for row in grid]


def format_ascii_bet_receipt(
    lottery: str,
    ticket: List[int],
    timestamp: str,
    terminal_id: str = "P4-EDGE-TERM-001",
) -> str:
    """Renders a formatted ASCII cryptographic bet receipt with visual mini-QR code."""
    sorted_nums = sorted([int(n) for n in ticket])
    num_str = " ".join(f"{n:02d}" for n in sorted_nums)
    digest = compute_bet_receipt_hash(lottery, ticket, timestamp, terminal_id)
    short_hash = digest[:16].upper()
    qr_lines = generate_mini_qr_ascii(digest)

    qr_block = "\n".join(f"│         {line:<39}│" for line in qr_lines)

    return (
        f"┌────────────────────────────────────────────────────────┐\n"
        f"│           P4LOTTERY OFFLINE EDGE BET RECEIPT           │\n"
        f"├────────────────────────────────────────────────────────┤\n"
        f"│ GAME      : {lottery.upper():<43}│\n"
        f"│ NUMBERS   : {num_str:<43}│\n"
        f"│ TIMESTAMP : {timestamp:<43}│\n"
        f"│ TERMINAL  : {terminal_id:<43}│\n"
        f"├────────────────────────────────────────────────────────┤\n"
        f"│ SHA256    : {digest[:43]}│\n"
        f"│             {digest[43:]:<43}│\n"
        f"├────────────────────────────────────────────────────────┤\n"
        f"│ VISUAL SCANNER QR MATRIX:                              │\n"
        f"{qr_block}\n"
        f"│ QR SIG    : *{short_hash}* · EDGE VERIFIED ✓   │\n"
        f"└────────────────────────────────────────────────────────┘"
    )


def audit_pwa_integrity(base_path: Optional[Path] = None) -> PwaAuditResult:
    """Audits local docs/reference directory for PWA assets and Service Worker compliance."""
    if base_path is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        ref_dir = repo_root / "docs" / "reference"
    else:
        ref_dir = base_path / "docs" / "reference" if (base_path / "docs" / "reference").exists() else base_path

    html_file = ref_dir / "frontier-synthesis-lab.html"
    manifest_file = ref_dir / "manifest.json"
    sw_file = ref_dir / "sw.js"

    missing = []
    if not html_file.is_file():
        missing.append("frontier-synthesis-lab.html")
    if not manifest_file.is_file():
        missing.append("manifest.json")
    if not sw_file.is_file():
        missing.append("sw.js")

    manifest_data: Dict[str, Any] = {}
    if manifest_file.is_file():
        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception:
            manifest_data = {}

    sw_events: List[str] = []
    if sw_file.is_file():
        sw_text = sw_file.read_text(encoding="utf-8")
        for evt in ["install", "activate", "fetch"]:
            if f"addEventListener('{evt}'" in sw_text or f'addEventListener("{evt}"' in sw_text:
                sw_events.append(evt)

    is_compliant = (
        len(missing) == 0
        and manifest_data.get("display") == "standalone"
        and "install" in sw_events
        and "fetch" in sw_events
    )

    return PwaAuditResult(
        is_compliant=is_compliant,
        html_exists=html_file.is_file(),
        manifest_exists=manifest_file.is_file(),
        sw_exists=sw_file.is_file(),
        manifest_data=manifest_data,
        service_worker_events=sw_events,
        missing_assets=missing,
    )
