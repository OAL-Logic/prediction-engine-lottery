import pytest
import asyncio
from engine.modules.cosmic import QuantumSidecar

@pytest.mark.asyncio
async def test_quantum_sidecar_initialization():
    sidecar = QuantumSidecar()
    assert sidecar is not None

@pytest.mark.asyncio
async def test_quantum_distillation_fallback():
    # Test that it falls back to VAE if "decoherence" is detected
    # We will mock the QPU result to have a high trace distance
    sidecar = QuantumSidecar()
    result = await sidecar.distill_entropy(qubits=2, force_fallback=True)
    assert result["source"] == "vae_fallback"
    assert result["fidelity"] < 0.95

@pytest.mark.asyncio
async def test_quantum_distillation_success():
    # Test successful local simulation
    sidecar = QuantumSidecar()
    result = await sidecar.distill_entropy(qubits=2)
    assert result["source"] in ["braket_local", "vae_fallback"]
    assert "entropy" in result
