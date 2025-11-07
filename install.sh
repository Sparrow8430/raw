#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------

# PURE bootstrap installer v0.3

# - Installs system dependencies (apt)

# - Creates Python venv and installs Python dependencies

# - Fixes filenames, symlinks ritual binary

# - Installs Electron dependencies

# - Creates convenient start scripts

# ---------------------------------------------------------

REPO_REMOTE="[https://github.com/Sparrow8430/pure.git](https://github.com/Sparrow8430/pure.git)"
WORKDIR="$HOME/pure"
VENV_DIR="$WORKDIR/.venv"

info(){ printf "\e[36m[*]\e[0m %s\n" "$1"; }
warn(){ printf "\e[33m[!]\e[0m %s\n" "$1"; }
err(){ printf "\e[31m[-]\e[0m %s\n" "$1"; exit 1; }

# Ensure apt-based system

if ! command -v apt >/dev/null 2>&1; then
err "This installer expects an apt-based system. Exiting."
fi

# Update & install system packages

info "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y
info "Installing dependencies..."
sudo apt install -y python3 python3-venv python3-pip git curl build-essential 
nodejs npm libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev xdg-utils

# Clone repo if missing

if [ ! -d "$WORKDIR" ]; then
info "Cloning repo into $WORKDIR..."
git clone "$REPO_REMOTE" "$WORKDIR"
else
info "Using existing repo at $WORKDIR"
fi
cd "$WORKDIR"

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
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

# Install Python requirements

[ -f "search/requirements.txt" ] && pip install -r search/requirements.txt
[ -f "protocol/requirements.txt" ] && pip install -r protocol/requirements.txt || true

# Runtime packages

pip install flask flask-cors pygame

# Make ritual executable & symlink

if [ -f "pure-lang/ritual_esolang.py" ]; then
info "Making ritual executable and linking to /usr/local/bin/ritual"
chmod +x pure-lang/ritual_esolang.py
sudo ln -sf "$WORKDIR/pure-lang/ritual_esolang.py" /usr/local/bin/ritual
else
warn "pure-lang/ritual_esolang.py not found."
fi

# Make ritual bridge server executable

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
npm install --no-audit --no-fund electron --save-dev
npm install socks-proxy-agent --save
cd "$WORKDIR"
else
warn "browser/ missing — skipping npm install"
fi

# Optional: install Tor

if ! command -v tor >/dev/null 2>&1; then
info "Installing Tor..."
sudo apt install -y tor torsocks || warn "Tor install failed."
fi

# Create helper scripts

mkdir -p "$WORKDIR/bin"
for script in start-protocol.sh start-search.sh start-ritual-server.sh start-browser-http.sh start-electron.sh start-all.sh; do

> "$WORKDIR/bin/$script"
> done

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

chmod +x "$WORKDIR/bin/"*.sh
mkdir -p "$WORKDIR/logs"

# Create .gitignore if missing

if [ ! -f .gitignore ]; then
cat > .gitignore <<'GIT'
.venv/
node_modules/
logs/
npm-debug.log
dist/
GIT
fi

deactivate 2>/dev/null || true
info "Installation complete."
