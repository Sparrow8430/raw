#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$HOME/pure"
VENV="$WORKDIR/.venv"
LOGDIR="$WORKDIR/logs"
BIN="$WORKDIR/bin"

info(){ printf "\e[36m[*]\e[0m %s\n" "$1"; }
warn(){ printf "\e[33m[!]\e[0m %s\n" "$1"; }
err(){ printf "\e[31m[-]\e[0m %s\n" "$1"; exit 1; }

# --- Dependencies ---
if ! command -v apt >/dev/null 2>&1; then
  err "This installer requires an apt-based system."
fi

info "Updating packages..."
sudo apt update -y && sudo apt upgrade -y

info "Installing system dependencies..."
sudo apt install -y python3 python3-venv python3-pip git curl build-essential \
nodejs npm libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev xdg-utils

# --- Clone repo ---
REPO="https://github.com/Sparrow8430/pure.git"
if [ ! -d "$WORKDIR" ]; then
  info "Cloning repo into $WORKDIR..."
  git clone "$REPO" "$WORKDIR"
else
  info "Repo exists, pulling latest..."
  cd "$WORKDIR" && git pull
fi

# --- Virtual environment ---
if [ ! -d "$VENV" ]; then
  info "Creating Python virtual environment..."
  python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"
pip install --upgrade pip setuptools wheel

# --- Python dependencies ---
pip install flask flask-cors pygame

# --- Make ritual executable ---
if [ -f "$WORKDIR/pure-lang/ritual_esolang.py" ]; then
  info "Making ritual executable..."
  chmod +x "$WORKDIR/pure-lang/ritual_esolang.py"
  sudo ln -sf "$WORKDIR/pure-lang/ritual_esolang.py" /usr/local/bin/ritual
else
  warn "ritual_esolang.py not found!"
fi

# --- Bin and log directories ---
mkdir -p "$BIN" "$LOGDIR"

# --- .gitignore ---
if [ ! -f "$WORKDIR/.gitignore" ]; then
  cat > "$WORKDIR/.gitignore" <<'GIT'
.venv/
node_modules/
logs/
npm-debug.log
dist/
GIT
fi

deactivate 2>/dev/null || true
info "Installation complete. Run '$BIN/start-all.sh' to launch all services."

