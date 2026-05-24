# Development Guide

## 🛠️ Environment Setup

### 1. Python Engine
```bash
# Setup venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[all]'
```

### 2. Go Gateway
```bash
cd gateway
go mod download
go build -o gateway-bin
```

### 3. Frontend App (Expo)
```bash
cd app
npm install
npm run start
```

### 4. Terminal Cockpit (TUI)
```bash
cd tui
bun install
bun run dev
```

## 🧪 Testing Protocol
- **Python**: `pytest tests/`
- **TUI**: `npm test`
- **Gateway**: `go test ./...`

## 📐 Architecture Rules
- **Lazy Loading**: No heavy imports at the top level of CLI commands.
- **Forensic Flow**: Engine results must be exported as valid YAML/MD for Obsidian.
- **Vectorized Protocol**: All filters must use the NumPy-based `VectorizedFilter` ABC.

---
_Generated: 2026-05-14_
