#!/bin/bash
set -e

echo "🜏  PURE: initializing environment..."
sleep 1

# Update system

echo "[*] Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

# Dependencies

echo "[*] Installing core dependencies..."
sudo apt install -y python3 python3-pip git nodejs npm build-essential 
libnss3 libatk1.0-0 libxss1 libasound2 libgtk-3-0 curl

# Create PURE workspace

echo "[*] Setting up PURE directories..."
mkdir -p ~/pure && cd ~/pure

# Clone components

echo "[*] Cloning PURE components..."
if [ ! -d "browser" ]; then
git clone [https://github.com/Slave88/pure-browser.git](https://github.com/Slave88/pure-browser.git) browser
else
echo "[+] Browser already exists, skipping..."
fi

if [ ! -d "protocol" ]; then
git clone [https://github.com/Slave88/pure-protocol.git](https://github.com/Slave88/pure-protocol.git) protocol
else
echo "[+] Protocol already exists, skipping..."
fi

if [ ! -d "search" ]; then
git clone [https://github.com/Slave88/pure-search.git](https://github.com/Slave88/pure-search.git) search
else
echo "[+] Search already exists, skipping..."
fi

# Install browser dependencies

echo "[*] Installing browser dependencies..."
cd ~/pure/browser
npm install

# Run browser

echo "[*] Launching PURE browser..."
npm start
