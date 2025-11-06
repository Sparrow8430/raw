# PURE Quick Reference Card

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pure-installer/main/install.sh | bash
```

## Daily Commands

```bash
# Start PURE
~/.pure/start.sh

# Stop PURE
~/.pure/stop.sh

# Check status
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## File Locations

```
~/.pure/data/           # Your data
~/.pure/logs/           # Application logs
~/.pure/keys/           # Encryption keys
~/.pure/system/         # Application code
```

## API Quick Reference

### Protocol API (Port 8001)

```bash
# Get identity
curl http://localhost:8001/identity

# Send message
curl -X POST http://localhost:8001/messages/send \
  -H "Content-Type: application/json" \
  -d '{"to_user":"user","content":"Hi!","encrypted":true}'

# List messages
curl http://localhost:8001/messages

# Add peer
curl -X POST http://localhost:8001/peers/add \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"peer1","address":"192.168.1.100","port":8001,"last_seen":0}'

# List peers
curl http://localhost:8001/peers
```

### Search API (Port 8002)

```bash
# Add document
curl -X POST http://localhost:8002/documents/add \
  -H "Content-Type: application/json" \
  -d '{"title":"Doc","content":"Text","tags":["tag"],"metadata":{}}'

# Search
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query":"search term","tags":[],"limit":10}'

# List all documents
curl http://localhost:8002/documents

# Get stats
curl http://localhost:8002/stats
```

## Troubleshooting

```bash
# Check if running
ps aux | grep -E "pure-protocol|pure-search|electron"

# Check ports
netstat -tuln | grep -E "8001|8002"

# View logs
tail -f ~/.pure/logs/protocol.log
tail -f ~/.pure/logs/search.log
tail -f ~/.pure/logs/browser.log

# Kill stuck processes
pkill -f "pure-protocol"
pkill -f "pure-search"
pkill -f "electron"

# Fresh start
rm -rf ~/.pure/data/*
~/.pure/start.sh
```

## Browser Interface

- **Dashboard**: System overview
- **Messages**: Send/receive messages
- **Network**: Manage peers
- **Search**: Index and search documents
- **Identity**: View your identity

## Common Tasks

### Backup Your Data

```bash
tar -czf pure-backup-$(date +%Y%m%d).tar.gz ~/.pure/data/
```

### Restore Data

```bash
~/.pure/stop.sh
tar -xzf pure-backup-YYYYMMDD.tar.gz -C ~/
~/.pure/start.sh
```

### Update PURE

```bash
~/.pure/stop.sh
cd ~/.pure/system/pure-protocol && git pull
cd ~/.pure/system/pure-search && git pull
cd ~/.pure/system/pure-browser && git pull && npm install
~/.pure/start.sh
```

### Reset Everything

```bash
~/.pure/stop.sh
rm -rf ~/.pure/data/*
rm -rf ~/.pure/keys/*
~/.pure/start.sh
```

## Ports

- **8001**: Protocol API (identity, messages, peers)
- **8002**: Search API (documents, search)

## Key Files

- `identity.json`: Your identity
- `messages.json`: Message history
- `peers.json`: Connected peers
- `documents.json`: Indexed documents
- `encryption.key`: Your encryption key

## Development

```bash
# Test protocol server
cd ~/.pure/system/pure-protocol
python3 main.py

# Test search server
cd ~/.pure/system/pure-search
python3 main.py

# Test browser
cd ~/.pure/system/pure-browser
npm start
```

## Environment

```bash
# Python dependencies
pip3 list | grep -E 'fastapi|uvicorn|pydantic|cryptography'

# Node packages
npm list -g --depth=0 | grep electron
```

## Useful Aliases

Add to `~/.bashrc`:

```bash
alias pure-start="~/.pure/start.sh"
alias pure-stop="~/.pure/stop.sh"
alias pure-logs="tail -f ~/.pure/logs/*.log"
alias pure-status="curl -s http://localhost:8001/health && curl -s http://localhost:8002/health"
```

Then run: `source ~/.bashrc`

## Repository URLs

Replace `YOUR_USERNAME` with your GitHub username:

- Main: `https://github.com/YOUR_USERNAME/pure-installer`
- Protocol: `https://github.com/YOUR_USERNAME/pure-protocol`
- Search: `https://github.com/YOUR_USERNAME/pure-search`
- Browser: `https://github.com/YOUR_USERNAME/pure-browser`

## Support

- Documentation: Check README files in each repo
- Testing: See TESTING.md
- Setup: See SETUP-GUIDE.md
- Issues: File on GitHub

---

**Quick Start**: `curl -sSL URL | bash` → `~/.pure/start.sh` → Browser opens → Start using PURE!
