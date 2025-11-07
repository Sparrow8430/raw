#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------
# PURE bootstrap installer v0.4
# ---------------------------------------------------------

REPO_REMOTE="https://github.com/Sparrow8430/pure.git"
WORKDIR="$HOME/pure"
VENV_DIR="$WORKDIR/.venv"

info(){ printf "\e[36m[*]\e[0m %s\n" "$1"; }
warn(){ printf "\e[33m[!]\e[0m %s\n" "$1"; }
err(){ printf "\e[31m[-]\e[0m %s\n" "$1"; exit 1; }

# Ensure apt-based system
command -v apt >/dev/null 2>&1 || err "This installer expects an apt-based system. Exiting."

info "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y
info "Installing dependencies..."
sudo apt install -y python3 python3-venv python3-pip git curl build-essential \
nodejs npm libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev xdg-utils

# Clone repo
if [ ! -d "$WORKDIR" ]; then
    info "Cloning repo into $WORKDIR..."
    git clone "$REPO_REMOTE" "$WORKDIR"
else
    info "Using existing repo at $WORKDIR"
fi
cd "$WORKDIR"

# Fix typo if present
[ -f "pure-lang/server,py" ] && mv -f pure-lang/server,py pure-lang/server.py

# Python virtual environment
[ ! -d "$VENV_DIR" ] && python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

# Python dependencies
[ -f "search/requirements.txt" ] && pip install -r search/requirements.txt
[ -f "protocol/requirements.txt" ] && pip install -r protocol/requirements.txt || true
pip install flask flask-cors pygame cryptography

# Make ritual executable & symlink
[ -f "pure-lang/ritual_esolang.py" ] && chmod +x pure-lang/ritual_esolang.py
sudo ln -sf "$WORKDIR/pure-lang/ritual_esolang.py" /usr/local/bin/ritual
[ -f "pure-lang/server.py" ] && chmod +x pure-lang/server.py

# Seed demo ritual
DEMORIT="$WORKDIR/pure-lang/ritual.txt"
if [ ! -f "$DEMORIT" ]; then
    cat > "$DEMORIT" <<'RITUAL'
# Demo ritual
CHIME
PAUSE 0.5
LIGHT 128 0 128
REPEAT 3 {
FLASH 255 0 0 1
ORB 200 200 50 0 0 255
SIGIL 50 50 100 100 0 255 0
}
INSCRIBE Ritual complete!
RITUAL
    info "Demo ritual seeded."
fi

# Electron/browser setup
if [ -d "browser" ]; then
    info "Installing browser dependencies..."
    cd browser
    [ ! -f package.json ] && npm init -y >/dev/null 2>&1
    npm install --no-audit --no-fund electron --save-dev
    npm install socks-proxy-agent --save
    cd "$WORKDIR"
fi

# Optional: install Tor
if ! command -v tor >/dev/null 2>&1; then
    info "Installing Tor..."
    sudo apt install -y tor torsocks || warn "Tor install failed."
fi

# Helper scripts
mkdir -p "$WORKDIR/bin"
for script in start-protocol.sh start-search.sh start-ritual-server.sh start-browser-http.sh start-electron.sh start-all.sh; do
    > "$WORKDIR/bin/$script"
done

# Create logs dir
mkdir -p "$WORKDIR/logs"

info "Installation complete. Use ./start_all.sh to launch all servers."
deactivate 2>/dev/null || true
