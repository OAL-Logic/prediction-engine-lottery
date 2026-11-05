"""
Unit Tests for Mobile PWA Cockpit & Edge Computing Module (Track L)
===================================================================
Tests Progressive Web App manifest, Service Worker offline caching,
touch gesture controls, cryptographic SHA-256 bet receipts, and CLI lab integration.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from engine.cli.main import app
from engine.modules.edge_pwa import (
    audit_pwa_integrity,
    compute_bet_receipt_hash,
    format_ascii_bet_receipt,
    generate_mini_qr_ascii,
)

runner = CliRunner()


def test_manifest_json_spec():
    """Verify that docs/reference/manifest.json conforms to PWA specification."""
    manifest_path = Path("docs/reference/manifest.json")
    assert manifest_path.is_file(), "manifest.json must exist in docs/reference/"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert data.get("name")
    assert data.get("short_name") == "p4lottery"
    assert data.get("display") == "standalone"
    assert data.get("start_url") == "./frontier-synthesis-lab.html"
    assert "theme_color" in data
    assert "background_color" in data
    assert len(data.get("icons", [])) > 0


def test_service_worker_lifecycle():
    """Verify sw.js contains cache lifecycle handlers."""
    sw_path = Path("docs/reference/sw.js")
    assert sw_path.is_file(), "sw.js must exist in docs/reference/"
    text = sw_path.read_text(encoding="utf-8")

    assert "install" in text
    assert "activate" in text
    assert "fetch" in text
    assert "frontier-synthesis-lab.html" in text
    assert "caches.open" in text


def test_html_cockpit_pwa_integration():
    """Verify HTML cockpit references manifest, registers SW, and has touch controls."""
    html_path = Path("docs/reference/frontier-synthesis-lab.html")
    text = html_path.read_text(encoding="utf-8")

    # Manifest link and PWA meta tags
    assert '<link rel="manifest" href="manifest.json">' in text
    assert '<meta name="theme-color"' in text
    assert '<meta name="apple-mobile-web-app-capable" content="yes">' in text

    # Service Worker registration
    assert "navigator.serviceWorker.register('./sw.js')" in text

    # Touch listeners and Edge Bet Receipt card
    assert "function initLorenzTouchControls()" in text
    assert "touchstart" in text
    assert "touchmove" in text
    assert "generateEdgeBetReceipt()" in text
    assert 'id="edge-pwa-card"' in text
    assert 'id="pwa-receipt-display"' in text


def test_edge_pwa_module_audit():
    """Verify audit_pwa_integrity passes for the repository."""
    audit = audit_pwa_integrity()
    assert audit.is_compliant is True
    assert audit.html_exists is True
    assert audit.manifest_exists is True
    assert audit.sw_exists is True
    assert "install" in audit.service_worker_events
    assert "fetch" in audit.service_worker_events


def test_cryptographic_receipt_hashing():
    """Verify deterministic SHA-256 computation for edge bet receipts."""
    h1 = compute_bet_receipt_hash("br/mega-sena", [8, 11, 15, 28, 58, 60], "2026-11-05T00:00:00Z", "TERM-01")
    h2 = compute_bet_receipt_hash("br/mega-sena", [60, 58, 28, 15, 11, 8], "2026-11-05T00:00:00Z", "TERM-01")
    # Order-invariant sorting
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex string

    receipt_str = format_ascii_bet_receipt("br/mega-sena", [8, 11, 15, 28, 58, 60], "2026-11-05T00:00:00Z", "TERM-01")
    assert "P4LOTTERY OFFLINE EDGE BET RECEIPT" in receipt_str
    assert "BR/MEGA-SENA" in receipt_str
    assert h1[:30] in receipt_str


def test_cli_lab_pwa_commands():
    """Verify CLI --audit-pwa, --receipt, and --pwa flags."""
    res_audit = runner.invoke(app, ["lab", "--audit-pwa"])
    assert res_audit.exit_code == 0
    assert "100% PWA COMPLIANT" in res_audit.output

    res_receipt = runner.invoke(app, ["lab", "--receipt", "5,12,23,34,45,56", "--game", "br/mega-sena"])
    assert res_receipt.exit_code == 0
    assert "P4LOTTERY OFFLINE EDGE BET RECEIPT" in res_receipt.output
    assert "SHA256" in res_receipt.output

    res_pwa = runner.invoke(app, ["lab", "--pwa", "--no-browser"])
    assert res_pwa.exit_code == 0
    assert "edge-pwa-card" in res_pwa.output


def test_mini_qr_ascii_and_wallet_features():
    """Verify visual 9x9 mini-QR generation and edge wallet/share integration."""
    digest = compute_bet_receipt_hash("br/mega-sena", [8, 11, 15, 28, 58, 60], "2026-11-05T00:00:00Z", "TERM-01")
    qr_lines = generate_mini_qr_ascii(digest)
    assert len(qr_lines) == 9
    assert all(len(line) == 18 for line in qr_lines)  # 9 cells of width 2 ("██" or "  ")

    receipt = format_ascii_bet_receipt("br/mega-sena", [8, 11, 15, 28, 58, 60], "2026-11-05T00:00:00Z", "TERM-01")
    assert "VISUAL SCANNER QR MATRIX:" in receipt
    assert "██" in receipt

    html_text = Path("docs/reference/frontier-synthesis-lab.html").read_text(encoding="utf-8")
    assert "pwa-wallet-list" in html_text
    assert "saveToEdgeWallet" in html_text
    assert "shareCurrentReceipt" in html_text
    assert "generateSvgQr" in html_text
    assert "toggleIsingSpin" in html_text
