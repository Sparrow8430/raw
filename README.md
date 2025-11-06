# PURE — Minimal MVP (v0.1)

PURE is a minimal local-first environment: a local search API, a simple protocol server with node identity, and a lightweight UI.

This repo is the clean baseline for v0.1. It is intentionally minimal to demonstrate:
- Node identity generation
- Local search endpoint
- Simple P2P handshake shape

## Quick run (after `install.sh`)
1. Start the protocol server:
   source ~/.pure_env/bin/activate    # if you used a venv; otherwise vendor instructions in install.sh
   python3 protocol/server.py

2. Start the search API:
   python3 search/server.py

3. Open UI:
   xdg-open browser/index.html

## Goals
- Local-first: data lives on the node
- Identity: nodes have keys and present a public key to peers
- Extendable: later we add peer discovery, WebSocket proxies, and Electron packaging

