"""
Intelligence narrative Obsidian export (Story 4.4).

Read-only over the ledger: verifies the chain via ``build_replay`` and writes one
Markdown note per ledger entry with 3.2-style frontmatter, the narrative and a
``lottery://evidence/<seq>?hash=...&coords=...`` deep-link to the entry's
geodesic coordinates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from engine.modules.ledger import ForensicLedger
from engine.modules.replay import ReplayError, build_replay


class ObsidianExportError(ValueError):
    """Export refused: unverifiable chain, unknown seq or blank narrative."""


def build_evidence_link(payload: Dict[str, Any]) -> str:
    coords = ",".join(repr(float(c)) for c in payload["state_vector"])
    return f"lottery://evidence/{payload['seq']}?hash={payload['entry_hash']}&coords={coords}"


def export_to_obsidian(ledger: ForensicLedger, seq: int, narrative: str, out_dir) -> Path:
    if not isinstance(narrative, str) or not narrative.strip():
        raise ObsidianExportError("narrative must be a non-blank string")
    try:
        payload = build_replay(ledger, seq)
    except ReplayError as exc:
        raise ObsidianExportError(str(exc)) from exc

    link = build_evidence_link(payload)
    ticket_str = ", ".join(str(n) for n in payload["ticket"]) or "none"
    entry_hash = payload["entry_hash"]
    content = f"""---
type: pattern-log
subtype: intelligence-narrative
ledger-seq: {payload['seq']}
entry-hash: "{entry_hash}"
evidence-link: "{link}"
captured-at: "{payload['captured_at']}"
ticket: [{ticket_str}]
source-strategy: "synapse"
confidence-rating: {payload['qpu_fidelity']}
tags: [prediction-engine, intelligence-narrative, "#lottery/analysis"]
---

# Intelligence Narrative: Justified Number #{payload['seq']}

{narrative.strip()}

## Justified Number

**`{ticket_str}`**

- Ledger seq: {payload['seq']}
- Entry hash: `{entry_hash}`
- QPU fidelity: {payload['qpu_fidelity']}

## Evidence

[Open Forensic Replay]({link})

`{link}`
"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"evidence-{payload['seq']}-{entry_hash[:12]}.md"
    path.write_text(content, encoding="utf-8")
    return path
