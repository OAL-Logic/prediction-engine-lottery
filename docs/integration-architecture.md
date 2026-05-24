# Integration Architecture

The Lottery Engine utilizes a "Triad" architecture to separate user interaction, security, and intensive statistical logic.

## 📐 Triad Components

### 1. Frontend App (React Native/Expo)
- **Role**: High-fidelity "Nerd Mode" cockpit and "Chaos Mode" predictor.
- **Protocol**: HTTP/HTTPS (REST).
- **Endpoint**: Connects to the **Go Gateway**.

### 2. Security Gateway (Go)
- **Role**: High-performance proxy, rate limiter, and API key validator.
- **Protocol**: HTTP/HTTPS Proxy.
- **Interface**: Downstreams requests to the **Python Sidecar**.

### 3. Core Engine (Python/FastAPI)
- **Role**: Heavy statistical processing, deep learning modeling, and OSINT fetching.
- **Protocol**: REST API.
- **Forensic Flow**: Writes analysis reports directly to **Obsidian** via a one-way forensic data contract.

## 🛰️ External Integrations
- **NOAA**: Real-time geomagnetic (Kp-Index) data for Solar Jitter.
- **USGS**: Real-time tectonic resonance data for Seismic Jitter.
- **Open-Meteo**: Atmospheric physics (Air Density, Refractive Index).

---
_Generated: 2026-05-14_
