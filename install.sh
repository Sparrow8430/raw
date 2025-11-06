#!/bin/bash
set -e

echo "[*] Updating system..."
sudo apt update -y && sudo apt upgrade -y

echo "[*] Installing dependencies..."
sudo apt install -y python3 python3-pip git nodejs npm build-essential libnss3 libatk1.0-0 libxss1 libasound2 libgtk-3-0

echo "[*] Cloning LunaOS components..."
mkdir -p ~/lunaos && cd ~/lunaos

# Browser
git clone https://github.com/yourusername/lunaos-browser.git browser || echo "Browser repo already exists."

# Protocol server
git clone https://github.com/yourusername/lunaos-protocol.git protocol || echo "Protocol repo already exists."

# Search
git clone https://github.com/yourusername/lunaos-search.git search || echo "Search repo already exists."

echo "[*] Installing Node dependencies for browser..."
cd browser && npm install && cd ..

echo "[*] Launching LunaOS browser..."
cd browser && npm start
