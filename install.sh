#!/bin/bash

set -e

PURE_DIR="$HOME/.pure"
INSTALL_DIR="$PURE_DIR/system"

echo "========================================="
echo "  PURE - Decentralized OS Installation  "
echo "========================================="
echo ""

# Check for dependencies
echo "[1/6] Checking dependencies..."
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Error: node is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "Error: npm is required but not installed."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "Error: git is required but not installed."; exit 1; }

echo "✓ All dependencies found"

# Create directory structure
echo ""
echo "[2/6] Creating PURE directory structure..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$PURE_DIR/data"
mkdir -p "$PURE_DIR/logs"
mkdir -p "$PURE_DIR/keys"

# Clone repositories
echo ""
echo "[3/6] Cloning PURE components..."
cd "$INSTALL_DIR"

if [ -d "pure-protocol" ]; then
    echo "  Updating pure-protocol..."
    cd pure-protocol && git pull && cd ..
else
    echo "  Cloning pure-protocol..."
    git clone https://github.com/YOUR_USERNAME/pure-protocol.git
fi

if [ -d "pure-search" ]; then
    echo "  Updating pure-search..."
    cd pure-search && git pull && cd ..
else
    echo "  Cloning pure-search..."
    git clone https://github.com/YOUR_USERNAME/pure-search.git
fi

if [ -d "pure-browser" ]; then
    echo "  Updating pure-browser..."
    cd pure-browser && git pull && cd ..
else
    echo "  Cloning pure-browser..."
    git clone https://github.com/YOUR_USERNAME/pure-browser.git
fi

# Install Python dependencies
echo ""
echo "[4/6] Installing Python dependencies..."
cd "$INSTALL_DIR/pure-protocol"
python3 -m pip install --user -r requirements.txt

cd "$INSTALL_DIR/pure-search"
python3 -m pip install --user -r requirements.txt

# Install Node dependencies
echo ""
echo "[5/6] Installing Node dependencies..."
cd "$INSTALL_DIR/pure-browser"
npm install

# Create startup scripts
echo ""
echo "[6/6] Creating startup scripts..."

# Main launcher script
cat > "$PURE_DIR/start.sh" << 'EOF'
#!/bin/bash

PURE_DIR="$HOME/.pure"
LOG_DIR="$PURE_DIR/logs"

echo "Starting PURE system..."

# Start pure-protocol
cd "$PURE_DIR/system/pure-protocol"
python3 main.py > "$LOG_DIR/protocol.log" 2>&1 &
PROTOCOL_PID=$!
echo "✓ pure-protocol started (PID: $PROTOCOL_PID)"

sleep 2

# Start pure-search
cd "$PURE_DIR/system/pure-search"
python3 main.py > "$LOG_DIR/search.log" 2>&1 &
SEARCH_PID=$!
echo "✓ pure-search started (PID: $SEARCH_PID)"

sleep 2

# Start pure-browser
cd "$PURE_DIR/system/pure-browser"
npm start > "$LOG_DIR/browser.log" 2>&1 &
BROWSER_PID=$!
echo "✓ pure-browser started (PID: $BROWSER_PID)"

# Save PIDs
echo "$PROTOCOL_PID" > "$PURE_DIR/protocol.pid"
echo "$SEARCH_PID" > "$PURE_DIR/search.pid"
echo "$BROWSER_PID" > "$PURE_DIR/browser.pid"

echo ""
echo "PURE is running!"
echo "Protocol API: http://localhost:8001"
echo "Search API: http://localhost:8002"
echo "Browser: Opening in new window..."
echo ""
echo "To stop PURE, run: ~/.pure/stop.sh"
EOF

chmod +x "$PURE_DIR/start.sh"

# Stop script
cat > "$PURE_DIR/stop.sh" << 'EOF'
#!/bin/bash

PURE_DIR="$HOME/.pure"

echo "Stopping PURE system..."

if [ -f "$PURE_DIR/protocol.pid" ]; then
    kill $(cat "$PURE_DIR/protocol.pid") 2>/dev/null && echo "✓ pure-protocol stopped"
    rm "$PURE_DIR/protocol.pid"
fi

if [ -f "$PURE_DIR/search.pid" ]; then
    kill $(cat "$PURE_DIR/search.pid") 2>/dev/null && echo "✓ pure-search stopped"
    rm "$PURE_DIR/search.pid"
fi

if [ -f "$PURE_DIR/browser.pid" ]; then
    kill $(cat "$PURE_DIR/browser.pid") 2>/dev/null && echo "✓ pure-browser stopped"
    rm "$PURE_DIR/browser.pid"
fi

echo "PURE stopped."
EOF

chmod +x "$PURE_DIR/stop.sh"

# Create symlink for easy access
sudo ln -sf "$PURE_DIR/start.sh" /usr/local/bin/pure 2>/dev/null || \
    echo "Note: Could not create /usr/local/bin/pure symlink (needs sudo)"

echo ""
echo "========================================="
echo "  Installation Complete!                "
echo "========================================="
echo ""
echo "To start PURE, run:"
echo "  ~/.pure/start.sh"
echo ""
echo "Or if symlink was created:"
echo "  pure"
echo ""
echo "To stop PURE, run:"
echo "  ~/.pure/stop.sh"
echo ""
echo "Logs are stored in: $PURE_DIR/logs"
echo ""
