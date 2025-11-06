# pure-protocol

Protocol server for PURE decentralized operating system. Handles identity management, peer-to-peer networking, and encrypted messaging.

## Features

- Identity generation and management
- Message sending and storage
- Peer connection management
- Encryption key generation
- RESTful API for all operations

## Installation

### Via PURE Installer (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pure-installer/main/install.sh | bash
```

### Manual Installation

```bash
git clone https://github.com/YOUR_USERNAME/pure-protocol.git
cd pure-protocol
pip3 install -r requirements.txt
python3 main.py
```

## Configuration

The protocol server uses the following defaults:

- **Host**: `127.0.0.1` (localhost only)
- **Port**: `8001`
- **Data Directory**: `~/.pure/data`
- **Keys Directory**: `~/.pure/keys`

## API Endpoints

### Identity

#### GET `/identity`
Get current identity information.

**Response:**
```json
{
  "username": "pure_abc12345",
  "public_key": "...",
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST `/identity/update`
Update identity information.

**Request:**
```json
{
  "username": "new_username",
  "public_key": "..."
}
```

**Response:**
```json
{
  "status": "updated",
  "identity": {...}
}
```

### Messages

#### GET `/messages`
List all messages.

**Response:**
```json
{
  "messages": [
    {
      "id": "abc123...",
      "from_user": "pure_abc12345",
      "to_user": "peer_xyz67890",
      "content": "Hello!",
      "encrypted": true,
      "timestamp": 1234567890.123,
      "sent_at": "2024-01-01T00:00:00"
    }
  ],
  "count": 1
}
```

#### POST `/messages/send`
Send a new message.

**Request:**
```json
{
  "to_user": "peer_username",
  "content": "Message text",
  "encrypted": true
}
```

**Response:**
```json
{
  "status": "sent",
  "message": {...}
}
```

### Peers

#### GET `/peers`
List all connected peers.

**Response:**
```json
{
  "peers": [
    {
      "peer_id": "peer_xyz67890",
      "address": "192.168.1.100",
      "port": 8001,
      "last_seen": 1234567890.0
    }
  ],
  "count": 1
}
```

#### POST `/peers/add`
Add a new peer.

**Request:**
```json
{
  "peer_id": "peer_xyz67890",
  "address": "192.168.1.100",
  "port": 8001,
  "last_seen": 1234567890.0
}
```

**Response:**
```json
{
  "status": "added",
  "peer": {...}
}
```

#### DELETE `/peers/{peer_id}`
Remove a peer.

**Response:**
```json
{
  "status": "removed",
  "peer_id": "peer_xyz67890"
}
```

### Health

#### GET `/health`
Check server health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "identity": "pure_abc12345",
  "data_dir": "/home/user/.pure/data"
}
```

## Data Storage

### Files

- **identity.json** - User identity and keys
- **messages.json** - Message history
- **peers.json** - Connected peers
- **keys/encryption.key** - Encryption key

### Format

All data is stored in JSON format for easy inspection and portability.

## Security

- Identity keys are generated on first run using cryptography library
- Keys are stored locally in `~/.pure/keys/`
- Server only accepts connections from localhost by default
- Encryption foundation is in place for future P2P implementation

## Development

### Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic
- Cryptography

### Running in Development

```bash
python3 main.py
```

### Testing

```bash
# Health check
curl http://localhost:8001/health

# Get identity
curl http://localhost:8001/identity

# Send test message
curl -X POST http://localhost:8001/messages/send \
  -H "Content-Type: application/json" \
  -d '{"to_user": "test", "content": "Hello!", "encrypted": true}'
```

## Roadmap

- [ ] Implement actual P2P networking
- [ ] Add end-to-end encryption for messages
- [ ] Implement peer discovery protocol
- [ ] Add message acknowledgment system
- [ ] Implement DHT for peer lookup
- [ ] Add support for file transfers
- [ ] Implement NAT traversal

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Part of PURE

This is a component of the PURE decentralized operating system. See the main PURE repository for more information.
