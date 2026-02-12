#!/usr/bin/env bash
# Improved SearxNG Setup Script
# Uses Docker for easy, reliable installation

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   SearxNG Setup Script (Docker)        ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is installed
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    echo ""
    echo "Docker is required for easy SearxNG installation."
    echo ""
    echo "Install Docker:"
    echo "  Ubuntu/Debian: sudo apt install docker.io"
    echo "  macOS: brew install docker"
    echo "  Or visit: https://docs.docker.com/get-docker/"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo ""
    echo "Start Docker:"
    echo "  Ubuntu/Debian: sudo systemctl start docker"
    echo "  macOS: Start Docker Desktop"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon running${NC}"

# Create configuration directory
SEARX_DIR="$HOME/.pure/searxng"
mkdir -p "$SEARX_DIR"

# Create settings.yml if it doesn't exist
if [ ! -f "$SEARX_DIR/settings.yml" ]; then
    echo -e "\n${BLUE}Creating SearxNG configuration...${NC}"
    cat > "$SEARX_DIR/settings.yml" << 'EOF'
use_default_settings: true
server:
  secret_key: "changeme-this-is-not-secure"
  limiter: false
  image_proxy: true
  port: 8080
  bind_address: "0.0.0.0"
ui:
  default_locale: "en"
  theme_args:
    simple_style: dark
search:
  safe_search: 0
  autocomplete: "google"
engines:
  - name: google
    disabled: false
  - name: duckduckgo
    disabled: false
  - name: wikipedia
    disabled: false
  - name: reddit
    disabled: false
EOF
    echo -e "${GREEN}✅ Configuration created at $SEARX_DIR/settings.yml${NC}"
else
    echo -e "${GREEN}✅ Configuration already exists${NC}"
fi

# Pull SearxNG Docker image
echo -e "\n${BLUE}Pulling SearxNG Docker image...${NC}"
docker pull searxng/searxng:latest
echo -e "${GREEN}✅ Image downloaded${NC}"

# Create run script
RUN_SCRIPT="$HOME/.pure/run-searxng.sh"
cat > "$RUN_SCRIPT" << EOF
#!/usr/bin/env bash
# SearxNG Docker Runner

# Stop any existing container
docker stop searxng 2>/dev/null || true
docker rm searxng 2>/dev/null || true

# Start SearxNG
echo "Starting SearxNG on http://localhost:8888..."
docker run -d \\
  --name searxng \\
  -p 8888:8080 \\
  -v "$SEARX_DIR/settings.yml:/etc/searxng/settings.yml:ro" \\
  --restart unless-stopped \\
  searxng/searxng:latest

echo "SearxNG is running!"
echo "Access it at: http://localhost:8888"
echo ""
echo "To stop: docker stop searxng"
echo "To view logs: docker logs searxng"
EOF

chmod +x "$RUN_SCRIPT"

# Create stop script
STOP_SCRIPT="$HOME/.pure/stop-searxng.sh"
cat > "$STOP_SCRIPT" << EOF
#!/usr/bin/env bash
echo "Stopping SearxNG..."
docker stop searxng
docker rm searxng
echo "SearxNG stopped"
EOF

chmod +x "$STOP_SCRIPT"

echo -e "\n${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║     SearxNG Setup Complete! 🎉         ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${BLUE}Quick Start:${NC}"
echo -e "  Start SearxNG: ${GREEN}$RUN_SCRIPT${NC}"
echo -e "  Stop SearxNG:  ${GREEN}$STOP_SCRIPT${NC}"
echo ""
echo -e "${BLUE}Or use Docker directly:${NC}"
echo "  docker start searxng    # Start"
echo "  docker stop searxng     # Stop"
echo "  docker logs searxng     # View logs"
echo ""
echo -e "${BLUE}Access SearxNG:${NC}"
echo -e "  ${GREEN}http://localhost:8888${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} The browser expects SearxNG on port 8888"
echo ""
