#!/usr/bin/env bash
set -e

# ----------------------------
# PURE v0.1 Installer
# ----------------------------

# Colors for echo
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
YELLOW="\033[1;33m"
RESET="\033[0m"

echo -e "${CYAN}[*] PURE v0.1 bootstrap starting...${RESET}"

# ----------------------------
# Check OS
# ----------------------------
if ! command -v apt >/dev/null 2>&1; then
  echo -e "${YELLOW}[!] This installer expects an apt-based Linux (Ubuntu/Debian/Linux Lite). Exiting.${RESET}"
  exit 1
fi

# ----------------------------
# Update & Install Dependencies
# ----------------------------
echo -e "${CYAN}[*] Updating packages...${RESET}"
sudo apt update -y

echo -e "${CYAN}[*] Installing core dependencies...${RESET}"
sudo apt install -y python3 python3-venv python3-pip git curl \
libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
build-essential xdg-utils

# ----------------------------
# Create Workspace
# ----------------------------
WORKDIR="$HOME/pure"
mkdir -p "$WORKDIR"
echo -e "${CYAN}[*] Workspace: $WORKDIR${RESET}"

# ----------------------------
# Clone or Copy Repo
# ----------------------------
REPO_PATH="$(pwd)"
if [ -f "$REPO_PATH/install.sh" ]; then
  echo -e "${CYAN}[*] Using repo at $REPO_PATH${RESET}"
  rsync -a --exclude='.git' "$REPO_PATH/" "$WORKDIR/"
else
  echo -e "${CYAN}[*] Repo not found locally; cloning from GitHub...${RESET}"
  git clone https://github.com/Slave88/pure.git "$WORKDIR"
fi

cd "$WORKDIR"

# ----------------------------
# Python Virtual Env
# ----------------------------
echo -e "${CYAN}[*] Creating Python virtual environment...${RESET}"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# ----------------------------
# Install Search & Protocol Dependencies
# ----------------------------
echo -e "${CYAN}[*] Installing Python packages for search & protocol...${RESET}"
if [ -f "search/requirements.txt" ]; then
  pip install -r search/requirements.txt
fi
if [ -f "protocol/requirements.txt" ]; then
  pip install -r protocol/requirements.txt || true
fi

# ----------------------------
# Setup Ritual Language
# ----------------------------
echo -e "${CYAN}[*] Installing Ritual language & Pygame visuals...${RESET}"
pip install pygame flask

# Make Ritual executable & link globally
chmod +x "$WORKDIR/pure-lang/ritual_esolang.py"
sudo ln -sf "$WORKDIR/pure-lang/ritual_esolang.py" /usr/local/bin/ritual

# Make Flask bridge server executable
chmod +x "$WORKDIR/pure-lang/server.py"

# Add demo Ritual script
DEMO_SCRIPT="$WORKDIR/pure-lang/ritual_demo.txt"
cat > "$DEMO_SCRIPT" <<'EOF'
# Demo Ritual script
CHIME
PAUSE 0.5
LIGHT 128 0 128
REPEAT 3 {
    FLASH 255 0 0 1
    ORB 200 200 50 0 0 255
    SIGIL 50 50 100 100 0 255 0
}
INSCRIBE Demo complete!
EOF

# ----------------------------
# Aesthetic Enhancements
# ----------------------------
echo -e "${CYAN}[*] Applying aesthetic setup...${RESET}"

# Example: create wallpapers folder
mkdir -p "$WORKDIR/wallpapers"
# Download example wallpaper
curl -s -L -o "$WORKDIR/wallpapers/pure_bg.png" https://i.imgur.com/3O8Xr5t.png || true

# Optional: add fonts or UI themes (extend here)
mkdir -p "$WORKDIR/fonts"

deactivate

# ----------------------------
# Completion Message
# ----------------------------
echo -e "${CYAN}[*] PURE installation complete!${RESET}"
echo -e "Run ${MAGENTA}ritual${RESET} to try your creative scripting environment."
echo
cat <<'EOF'
QUICK START:

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

4) Run the Ritual demo:
   ritual /pure-lang/ritual_demo.txt
EOF
