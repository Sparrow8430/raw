# PURE - Decentralized Operating System

PURE is a minimal decentralized operating system and communication network inspired by Urbit. It provides a local-first, privacy-focused platform for messaging, peer networking, and content management.

## Architecture

PURE consists of three core components:

1. **pure-protocol** - Python FastAPI server handling P2P networking, encryption, and identity management
2. **pure-search** - Python FastAPI server providing local document indexing and search
3. **pure-browser** - Electron-based GUI client for user interaction

All components run locally and communicate via localhost ports:
- Protocol: `http://localhost:8001`
- Search: `http://localhost:8002`
- Browser: Electron app

## Prerequisites

- Linux operating system
- Python 3.8+
- Node.js 16+
- npm
- git

Install dependencies on Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm git
```

## Installation

Run the installer:
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pure-installer/main/install.sh | bash
```

Or clone and run manually:
```bash
git clone https://github.com/YOUR_USERNAME/pure-installer.git
cd pure-installer
chmod +x install.sh
./install.sh
```

## Usage

### Starting PURE

```bash
~/.pure/start.sh
```

Or if the symlink was created:
```bash
pure
```

The browser window will open automatically. You can access:
- **Dashboard** - System status and overview
- **Messages** - Send and receive encrypted messages
- **Network** - Manage peer connections
- **Search** - Index and search local documents
- **Identity** - View your identity and public key

### Stopping PURE

```bash
~/.pure/stop.sh
```

### Logs

Logs are stored in `~/.pure/logs/`:
- `protocol.log` - Protocol server logs
- `search.log` - Search server logs
- `browser.log` - Browser application logs

### Data Storage

All data is stored locally in `~/.pure/data/`:
- `identity.json` - Your identity information
- `messages.json` - Message history
- `peers.json` - Connected peers
- `index/documents.json` - Indexed documents

## API Endpoints

### Protocol API (Port 8001)

- `GET /` - Service info
- `GET /identity` - Get your identity
- `POST /identity/update` - Update identity
- `GET /messages` - List all messages
- `POST /messages/send` - Send a message
- `GET /peers` - List connected peers
- `POST /peers/add` - Add a peer
- `DELETE /peers/{peer_id}` - Remove a peer
- `GET /health` - Health check

### Search API (Port 8002)

- `GET /` - Service info
- `GET /documents` - List all documents
- `POST /documents/add` - Add a document
- `GET /documents/{doc_id}` - Get specific document
- `DELETE /documents/{doc_id}` - Delete a document
- `POST /search` - Search documents
- `GET /stats` - Index statistics
- `GET /health` - Health check

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing instructions.

Quick test:
```bash
# Check if services are running
curl http://localhost:8001/health
curl http://localhost:8002/health

# Get your identity
curl http://localhost:8001/identity
```

## Development

### Repository Structure

```
pure-installer/
├── install.sh           # Main installer script
└── README.md

pure-protocol/
├── main.py             # Protocol server
├── requirements.txt
└── README.md

pure-search/
├── main.py             # Search server
├── requirements.txt
└── README.md

pure-browser/
├── main.js             # Electron main process
├── index.html          # UI
├── package.json
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Roadmap

- [ ] P2P networking implementation
- [ ] End-to-end encryption for messages
- [ ] Peer discovery protocol
- [ ] Content synchronization
- [ ] File sharing
- [ ] Plugin system
- [ ] Mobile clients

## Security Notes

- All data is stored locally by default
- Identity keys are generated on first run
- Messages can be encrypted (encryption foundation in place)
- No telemetry or external connections by default

## Philosophy

PURE follows these principles:

1. **Local-first** - Your data lives on your machine
2. **Privacy by default** - No central servers or tracking
3. **User ownership** - You control your identity and data
4. **Simplicity** - Minimal, understandable codebase
5. **Extensibility** - Build on top of the foundation

## License

MIT License - See LICENSE file for details

## Credits

Inspired by Urbit's vision of personal servers and digital sovereignty.

## Support

- Issues: GitHub Issues
- Documentation: See individual component READMEs
- Community: Coming soon

---

Built with ❤️ for a decentralized future
