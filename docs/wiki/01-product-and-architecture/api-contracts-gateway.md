# API Contracts: go-gateway

The Go Gateway acts as a high-performance proxy and security layer for the Python Engine.

## Endpoints

### 🛡️ Security & Proxy
- `GET /health`: Health check for the gateway and upstream connectivity.
- `ANY /*`: Proxies requests to the Python Sidecar (`localhost:8000`).

## Features
- **Rate Limiting**: Integrated `httprate` middleware for DDoS protection.
- **Header Propagation**: Standardizes headers (e.g., `X-Forwarded-Host`) for the Python sidecar.
- **Deadline Propagation**: Propagates `X-Request-Deadline` to enforce cross-triad timeouts.
- **API Key Validation**: Mandatory `X-API-KEY` verification for all non-health requests.

---
_Generated: 2026-05-14_
