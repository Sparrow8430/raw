# 1. Make sure repo is in ~/pure
cd ~/pure

# 2. Ensure Tor is installed & running (host listens on 127.0.0.1:9050)
sudo apt update
sudo apt install -y tor
sudo systemctl enable --now tor

# check Tor
ss -ltnp | grep 9050

# 3. Start Searx (docker-compose)
cd ~/pure/searx
# create searx-data dir
mkdir -p searx-data
docker compose up -d

# 4. Start electron UI (from repo root)
cd ~/pure/browser
npm install --no-audit --no-fund
npm run start
