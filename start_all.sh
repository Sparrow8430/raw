#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$HOME/pure"
VENV="$WORKDIR/.venv"
LOGDIR="$WORKDIR/logs"

mkdir -p "$LOGDIR"

# 1. Fix ritual symlink and permissions

chmod +x "$WORKDIR/pure-lang/ritual_esolang.py"
sudo ln -sf "$WORKDIR/pure-lang/ritual_esolang.py" /usr/local/bin/ritual

# 2. Activate Python virtual environment

# shellcheck source=/dev/null

source "$VENV/bin/activate"

# 3. Kill any existing servers on their ports

kill_port() {
local PORT=$1
if sudo lsof -i :"$PORT" -t >/dev/null; then
echo "[*] Killing process on port $PORT..."
sudo kill -9 $(sudo lsof -i :"$PORT" -t)
fi
}

kill_port 9000   # protocol / ritual server
kill_port 8888   # search server
kill_port 8000   # browser HTTP

# 4. Start protocol server

nohup python3 "$WORKDIR/protocol/server.py" >> "$LOGDIR/protocol.log" 2>&1 &
echo "[*] Protocol server started (logs/protocol.log)"

# 5. Start search server

nohup python3 "$WORKDIR/search/server.py" >> "$LOGDIR/search.log" 2>&1 &
echo "[*] Search server started (logs/search.log)"

# 6. Start ritual bridge server

nohup python3 "$WORKDIR/pure-lang/server.py" >> "$LOGDIR/ritual_server.log" 2>&1 &
echo "[*] Ritual bridge server started (logs/ritual_server.log)"

# 7. Start browser HTTP server

nohup python3 -m http.server 8000 --directory "$WORKDIR/browser" >> "$LOGDIR/browser_http.log" 2>&1 &
echo "[*] Browser HTTP server started on port 8000 (logs/browser_http.log)"

# 8. Optional: start Electron UI

if [ -f "$WORKDIR/browser/package.json" ]; then
(cd "$WORKDIR/browser" && nohup npm run start --silent >> "$LOGDIR/electron.log" 2>&1 || nohup npx electron . >> "$LOGDIR/electron.log" 2>&1) &
echo "[*] Electron UI launched (logs/electron.log)"
fi

echo "[*] All services started. Use 'tail -f $LOGDIR/*.log' to watch logs."
