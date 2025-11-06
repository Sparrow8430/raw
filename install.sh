#!/usr/bin/env bash
set -e
echo "PURE v0.1 bootstrap starting..."

# Check Debian/Ubuntu family
if ! command -v apt >/dev/null 2>&1; then
  echo "This installer expects an apt-based Linux (Ubuntu/Debian/Linux Lite). Exiting."
  exit 1
fi

# Update & deps
echo "[*] Updating packages..."
sudo apt update -y

echo "[*] Installing dependencies..."
sudo apt install -y python3 python3-venv python3-pip git curl

# Create workspace
WORKDIR="$HOME/pure"
mkdir -p "$WORKDIR"
echo "[*] Workspace: $WORKDIR"

# Copy current repo into workspace if running from clone
# (If user runs via curl|bash, clone first)
REPO_PATH="$(pwd)"
if [ -f "$REPO_PATH/install.sh" ]; then
  echo "[*] Using repo at $REPO_PATH"
  rsync -a --exclude='.git' "$REPO_PATH/" "$WORKDIR/"
else
  echo "[*] Repo not found locally; cloning from GitHub..."
  git clone https://github.com/Slave88/pure.git "$WORKDIR"
fi

cd "$WORKDIR"

# Python venvs
echo "[*] Creating Python virtual env for search and protocol..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install python requirements for search and protocol
if [ -f "search/requirements.txt" ]; then
  pip install -r search/requirements.txt
fi
pip install -r protocol/requirements.txt || true

deactivate

echo
cat <<'EOF'
INSTALL COMPLETE.

To run:
1) Start protocol server:
   cd ~/pure
   source .venv/bin/activate
   python3 protocol/server.py
   (open another terminal)

2) Start search server:
   source .venv/bin/activate
   python3 search/server.py
   (open another terminal)

3) Open the UI in a browser (local file):
   xdg-open ~/pure/browser/index.html

Quick start is also in QUICK-START.md
EOF
