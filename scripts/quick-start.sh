#!/usr/bin/env bash
# Pure Browser Project - Quick Start Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   Pure Browser Project - Quick Start   ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python 3 found"

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found"

# Setup SearxNG
echo -e "\n${BLUE}[1/4] Setting up SearxNG...${NC}"
if [ ! -d "searx-venv" ]; then
    ./scripts/setup-searx.sh
else
    echo "✅ SearxNG already setup"
fi

# Setup Protocol
echo -e "\n${BLUE}[2/4] Setting up Protocol Server...${NC}"
cd protocol
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    echo "✅ Protocol dependencies installed"
else
    echo "✅ Protocol already setup"
fi
cd ..

# Setup Browser
echo -e "\n${BLUE}[3/4] Setting up Browser...${NC}"
cd browser
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Browser dependencies installed"
else
    echo "✅ Browser already setup"
fi
cd ..

# Create launch script
echo -e "\n${BLUE}[4/4] Creating launch script...${NC}"
cat > start-pure.sh << 'LAUNCHER'
#!/usr/bin/env bash

# Start SearxNG in background
echo "Starting SearxNG..."
source searx-venv/bin/activate
export SEARXNG_SETTINGS_PATH="$HOME/.pure/searxng/settings.yml"
python -m searx.webapp > /dev/null 2>&1 &
SEARX_PID=$!

# Wait for SearxNG to start
sleep 3

# Start Protocol Server in background
echo "Starting Protocol Server..."
cd protocol
source venv/bin/activate
python server.py > /dev/null 2>&1 &
PROTOCOL_PID=$!
cd ..

# Wait for Protocol Server to start
sleep 2

# Start Browser (foreground)
echo "Starting Pure Browser..."
cd browser
npm start

# Cleanup on exit
kill $SEARX_PID $PROTOCOL_PID 2>/dev/null
LAUNCHER

chmod +x start-pure.sh

echo -e "\n${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║          Setup Complete! 🎉            ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${BLUE}Quick Start:${NC}"
echo "  ./start-pure.sh"

echo -e "\n${BLUE}Manual Start:${NC}"
echo "  Terminal 1: source searx-venv/bin/activate && python -m searx.webapp"
echo "  Terminal 2: cd protocol && python server.py"
echo "  Terminal 3: cd browser && npm start"

echo -e "\n${BLUE}Connect to peer:${NC}"
echo "  cd protocol && python client.py <peer-ip> 9000"

echo -e "\n${GREEN}Ready to explore Pure! 🌐${NC}\n"
