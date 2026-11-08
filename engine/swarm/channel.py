"""
PQC-signaled sealed channel for agent trajectories.

Simulation seam: mirrors the gateway's ``X-PQC-Active`` / ``X-PQC-Key-Version``
semantics. No real ML-KEM here; AES-256-GCM with an HKDF-derived session key
is the stand-in. Envelopes carry a per-sender monotonic counter (replay
protection) and bind all header fields as AEAD associated data (tamper
protection).
"""

from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass
from typing import Any, Dict, Optional

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class PQCChannelError(Exception):
    """Raised on tampered, replayed, or PQC-inactive envelopes."""


@dataclass(frozen=True)
class SealedEnvelope:
    sender: str
    counter: int
    key_version: str
    pqc_active: bool
    nonce: bytes
    ciphertext: bytes

    def headers(self) -> Dict[str, str]:
        """Gateway-equivalent signaling headers."""
        return {
            "X-PQC-Active": "true" if self.pqc_active else "false",
            "X-PQC-Key-Version": self.key_version,
        }


def _aad(sender: str, counter: int, key_version: str, pqc_active: bool) -> bytes:
    return b"|".join(
        [
            sender.encode("utf-8"),
            struct.pack(">Q", counter),
            key_version.encode("utf-8"),
            b"1" if pqc_active else b"0",
        ]
    )


class PQCChannel:
    """Session channel. Seal and open keep independent per-sender counters."""

    def __init__(self, session_secret: Optional[bytes] = None, key_version: str = "v1"):
        self._secret = session_secret if session_secret is not None else os.urandom(32)
        self.key_version = key_version
        self._aead = AESGCM(
            HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b"lottery-swarm-pqc-session:" + key_version.encode("utf-8"),
            ).derive(self._secret)
        )
        self._send_counters: Dict[str, int] = {}
        self._recv_counters: Dict[str, int] = {}

    def __getstate__(self) -> Dict[str, Any]:
        # AESGCM objects are not picklable (Ray ships actor args via cloudpickle):
        # carry the secret and rebuild the AEAD on the other side.
        return {
            "secret": self._secret,
            "key_version": self.key_version,
            "send": dict(self._send_counters),
            "recv": dict(self._recv_counters),
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__init__(state["secret"], state["key_version"])
        self._send_counters = dict(state["send"])
        self._recv_counters = dict(state["recv"])

    def seal(self, payload: Dict[str, Any], sender: str) -> SealedEnvelope:
        counter = self._send_counters.get(sender, 0) + 1
        self._send_counters[sender] = counter
        nonce = os.urandom(12)
        ciphertext = self._aead.encrypt(
            nonce,
            json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            _aad(sender, counter, self.key_version, True),
        )
        return SealedEnvelope(sender, counter, self.key_version, True, nonce, ciphertext)

    def open(self, envelope: SealedEnvelope) -> Dict[str, Any]:
        if not envelope.pqc_active:
            raise PQCChannelError("PQC signal inactive")
        if envelope.key_version != self.key_version:
            raise PQCChannelError("PQC key version mismatch")
        if envelope.counter <= self._recv_counters.get(envelope.sender, 0):
            raise PQCChannelError("replayed envelope")
        try:
            plaintext = self._aead.decrypt(
                envelope.nonce,
                envelope.ciphertext,
                _aad(envelope.sender, envelope.counter, envelope.key_version, envelope.pqc_active),
            )
        except (InvalidTag, ValueError) as exc:
            raise PQCChannelError("envelope authentication failed") from exc
        # Advance only after successful authentication.
        self._recv_counters[envelope.sender] = envelope.counter
        return json.loads(plaintext)
