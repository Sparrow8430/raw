#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------
# PURE bootstrap installer v0.4
# ---------------------------------------------------------
# - Works on any Linux (apt-based) system
# - Creates Python virtual environment and installs dependencies
# - Installs Node/Electron dependencies
# - Creates helper scripts to run servers
# ---------------------------------------------------------

REPO_REMOTE="https://github.com/Sparrow8430/pure.git"
WORKDIR="$(pwd)"      # Use current directory for portability
VENV_DIR="$WORKDIR/.venv"

info() { printf "\e[36m[*]\e[0m %s\n" "$1"; }
warn() { printf "\e[33m[!]\e[0m %s\n" "$1"; }
err() { printf "\e[31m[-]\e[0m %s\n" "$1"; exit 1; }

# Check for apt
command -v apt >/dev/null 2>&1 || err "Requires apt-based system"

info "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

info "Installing system dependencies..."
sudo apt install -y python3 python3-venv python3-pip git curl build-essential \
    nodejs npm libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev xdg-utils

# Clone repo if missing
if [ ! -d "$WORKDIR/.git" ]; then
    info "Cloning PURE repo into $WORKDIR..."
    git clone "$REPO_REMOTE" "$WORKDIR"
else
    info "Using existing repo at $WORKDIR"
fi

# Fix server filename typo if present
if [ -f "pure-lang/server,py" ]; then
    info "Fixing typo server,py -> server.py"
    mv -f pure-lang/server,py pure-lang/server.py
fi

# Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

# Install Python requirements
[ -f "search/requirements.txt" ] && pip install -r search/requirements.txt
[ -f "protocol/requirements.txt" ] && pip install -r protocol/requirements.txt || true

# Runtime packages
pip install flask flask-cors pygame

# Make ritual executable (no sudo needed)
if [ -f "pure-lang/ritual_esolang.py" ]; then
    info "Making ritual executable locally"
    chmod +x pure-lang/ritual_esolang.py
    ln -sf "$WORKDIR/pure-lang/ritual_esolang.py" "$WORKDIR/ritual"
else
    warn "pure-lang/ritual_esolang.py not found."
fi

# Make ritual server executable
[ -f "pure-lang/server.py" ] && chmod +x pure-lang/server.py

# Seed demo ritual if missing
DEMORIT="$WORKDIR/pure-lang/ritual.txt"
if [ ! -f "$DEMORIT" ]; then
    info "Seeding demo ritual..."
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
fi

# Electron/browser setup
if [ -d "browser" ]; then
    info "Installing browser dependencies..."
    cd browser
    [ ! -f package.json ] && npm init -y >/dev/null 2>&1
    npm install --no-audit --no-fund electron socks-proxy-agent --save-dev
    cd "$WORKDIR"
else
    warn "browser/ missing — skipping npm install"
fi

# Optional: Tor
command -v tor >/dev/null 2>&1 || {
    info "Installing Tor..."
    sudo apt install -y tor torsocks || warn "Tor install failed"
}

# Create helper scripts
mkdir -p "$WORKDIR/bin"

cat > "$WORKDIR/bin/start-all.sh" <<'SH'
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
mkdir -p logs
./bin/start-protocol.sh
sleep 0.4
./bin/start-search.sh
sleep 0.4
./bin/start-ritual-server.sh
sleep 0.4
./bin/start-browser-http.sh
echo "All services started. Use 'tail -f logs/*.log' to watch logs."
SH

chmod +x "$WORKDIR/bin/"*.sh
mkdir -p "$WORKDIR/logs"

# Gitignore
[ -f .gitignore ] || cat > .gitignore <<'GIT'
.venv/
node_modules/
logs/
npm-debug.log
dist/
GIT

deactivate 2>/dev/null || true
info "Installation complete."

