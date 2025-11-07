#!/usr/bin/env bash
set -euo pipefail
# ---------------------------------------------------------
# PURE bootstrap installer (idempotent) - v0.2
# - Installs system deps (apt)
# - Creates Python venv and installs python deps
# - Fixes filenames, symlinks ritual binary
# - Installs electron deps in browser/
# - Creates small start scripts for convenience
# ---------------------------------------------------------

REPO_REMOTE="https://github.com/Slave88/pure.git"
WORKDIR="$HOME/pure"
VENV_DIR="$WORKDIR/.venv"

info(){ printf "\e[36m[*]\e[0m %s\n" "$1"; }
warn(){ printf "\e[33m[!]\e[0m %s\n" "$1"; }
err(){ printf "\e[31m[-]\e[0m %s\n" "$1"; exit 1; }

# Ensure apt-based
if ! command -v apt >/dev/null 2>&1; then
  err "This installer expects an apt-based system (Ubuntu, Debian, Kali). Exiting."
fi

# update + base packages
info "Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

info "Installing system packages (python, node, build deps, SDL2 for Pygame, curl)..."
sudo apt install -y \
  python3 python3-venv python3-pip git curl build-essential \
  nodejs npm libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  xdg-utils

# Create workspace (use existing clone if present)
if [ -d "$WORKDIR" ] && [ -f "$WORKDIR/install.sh" ]; then
  info "Found existing repo at $WORKDIR — using it."
else
  info "Cloning repo into $WORKDIR..."
  rm -rf "$WORKDIR"
  git clone "$REPO_REMOTE" "$WORKDIR"
fi

cd "$WORKDIR"

# Guard: ensure pure-lang folder exists
if [ ! -d "pure-lang" ]; then
  warn "pure-lang folder not found; creating placeholder."
  mkdir -p pure-lang
fi

# Fix possible filename typo: server,py -> server.py
if [ -f "pure-lang/server,py" ]; then
  info "Fixing filename typo: pure-lang/server,py -> pure-lang/server.py"
  mv -f pure-lang/server,py pure-lang/server.py
fi

# Python venv
if [ ! -d "$VENV_DIR" ]; then
  info "Creating Python virtual environment..."
  python3 -m venv "$VENV_DIR"
fi
# Activate venv for pip installs
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

info "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python requirements (search & protocol)
if [ -f "search/requirements.txt" ]; then
  info "Installing search requirements..."
  pip install -r search/requirements.txt
fi

if [ -f "protocol/requirements.txt" ]; then
  info "Installing protocol requirements..."
  pip install -r protocol/requirements.txt || true
fi

# Always install these runtime deps
info "Installing runtime packages: flask-cors, pygame, flask"
pip install flask-cors pygame flask

# Make ritual script executable (if present) and symlink
if [ -f "pure-lang/ritual_esolang.py" ]; then
  info "Making ritual executable and installing symlink /usr/local/bin/ritual"
  chmod +x pure-lang/ritual_esolang.py
  sudo ln -sf "$(pwd)/pure-lang/ritual_esolang.py" /usr/local/bin/ritual
else
  warn "pure-lang/ritual_esolang.py not found — please add it to the repo."
fi

# Ensure ritual bridge server file is executable (if present)
if [ -f "pure-lang/server.py" ]; then
  chmod +x pure-lang/server.py
fi

# Seed demo ritual if missing
DEMORIT="$WORKDIR/pure-lang/ritual.txt"
if [ ! -f "$DEMORIT" ]; then
  info "Seeding demo ritual to $DEMORIT"
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

# Electron / browser setup
if [ -d "browser" ]; then
  info "Installing browser npm deps (electron + socks-proxy-agent)..."
  cd browser
  # Ensure package.json exists
  if [ ! -f package.json ]; then
    npm init -y >/dev/null 2>&1 || true
  fi
  npm install --no-audit --no-fund electron --save-dev
  npm install socks-proxy-agent --save
  cd "$WORKDIR"
else
  warn "browser/ missing — skip npm install"
fi

# Optional: install and enable tor if not present
if ! command -v tor >/dev/null 2>&1; then
  info "Installing Tor..."
  sudo apt install -y tor torsocks || warn "Tor install failed (you can install it manually)."
else
  info "Tor already installed."
fi

# Make simple helper scripts in repo root for starting components
info "Writing helper start scripts to $WORKDIR/bin/"
mkdir -p "$WORKDIR/bin"

cat > "$WORKDIR/bin/start-protocol.sh" <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
nohup python3 protocol/server.py >> logs/protocol.log 2>&1 &
echo "protocol started (logs/protocol.log)"
SH

cat > "$WORKDIR/bin/start-search.sh" <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
nohup python3 search/server.py >> logs/search.log 2>&1 &
echo "search started (logs/search.log)"
SH

cat > "$WORKDIR/bin/start-ritual-server.sh" <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")/.."
source .venv/bin/activate
nohup python3 pure-lang/server.py >> logs/ritual_server.log 2>&1 &
echo "ritual bridge started (logs/ritual_server.log)"
SH

cat > "$WORKDIR/bin/start-browser-http.sh" <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")/../browser"
nohup python3 -m http.server 8000 >> ../logs/browser_http.log 2>&1 &
echo "browser static HTTP started on port 8000 (logs/browser_http.log)"
SH

cat > "$WORKDIR/bin/start-electron.sh" <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")/../browser"
# run electron from local node_modules
npm run start --silent || npx electron .
SH

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

# Make scripts executable
chmod +x "$WORKDIR/bin/"*.sh

# Create logs folder if missing
mkdir -p "$WORKDIR/logs"

# Create .gitignore if missing
if [ ! -f .gitignore ]; then
  cat > .gitignore <<'GIT'
# virtualenvs, node modules, logs
.venv/
node_modules/
logs/
npm-debug.log
dist/
GIT
fi

# Deactivate venv
deactivate 2>/dev/null || true

info "Installation complete."

cat <<'EOF'

Quick usage:

cd ~/pure
# activate venv for manual runs:
source .venv/bin/activate

# recommended: start everything via helper script (backgrounded)
./bin/start-all.sh

# or start individual pieces:
./bin/start-protocol.sh
./bin/start-search.sh
./bin/start-ritual-server.sh
./bin/start-browser-http.sh
./bin/start-electron.sh   # launches electron UI

Notes:
- Browser UI is served at http://127.0.0.1:8000/index.html
- Search API is at http://127.0.0.1:8888/search?q=...
- Protocol server listens on TCP 9000
- To route Electron fetches through Tor, use the socks-proxy-agent in your renderer/preload code.
EOF
