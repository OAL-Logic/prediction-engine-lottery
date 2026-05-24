# Architecture: go-gateway

The high-performance security and routing hub.

## 🏛️ Technical Stack
- **Language**: Go 1.23+
- **Router**: Go-Chi v5
- **Security**: HTTPrate (Rate limiting)

## 📐 Responsibility
- **Edge Security**: Validates `X-API-KEY` before requests reach the engine.
- **Triad Bridge**: Normalizes communication between the Expo frontend and Python backend.
- **Deadline Propagation**: Ensures the engine respects client-side timeouts.

---
_Generated: 2026-05-14_
