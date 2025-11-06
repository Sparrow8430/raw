from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from typing import List, Optional

app = FastAPI(title="PURE Protocol", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PURE_DIR = Path.home() / ".pure"
DATA_DIR = PURE_DIR / "data"
KEYS_DIR = PURE_DIR / "keys"

DATA_DIR.mkdir(parents=True, exist_ok=True)
KEYS_DIR.mkdir(parents=True, exist_ok=True)

# Models
class Identity(BaseModel):
    username: str
    public_key: str

class Message(BaseModel):
    to_user: str
    content: str
    encrypted: bool = True

class PeerInfo(BaseModel):
    peer_id: str
    address: str
    port: int
    last_seen: float

# Storage
IDENTITY_FILE = DATA_DIR / "identity.json"
MESSAGES_FILE = DATA_DIR / "messages.json"
PEERS_FILE = DATA_DIR / "peers.json"

def load_json(filepath, default):
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# Initialize identity
def get_or_create_identity():
    if IDENTITY_FILE.exists():
        return load_json(IDENTITY_FILE, {})
    
    # Generate new identity
    key = Fernet.generate_key()
    key_file = KEYS_DIR / "encryption.key"
    with open(key_file, 'wb') as f:
        f.write(key)
    
    username = f"pure_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    identity = {
        "username": username,
        "public_key": key.decode(),
        "created_at": datetime.now().isoformat()
    }
    save_json(IDENTITY_FILE, identity)
    return identity

identity = get_or_create_identity()

@app.get("/")
def root():
    return {
        "service": "PURE Protocol",
        "version": "0.1.0",
        "status": "running",
        "identity": identity["username"]
    }

@app.get("/identity")
def get_identity():
    return identity

@app.post("/identity/update")
def update_identity(new_identity: Identity):
    identity["username"] = new_identity.username
    save_json(IDENTITY_FILE, identity)
    return {"status": "updated", "identity": identity}

@app.get("/messages")
def get_messages():
    messages = load_json(MESSAGES_FILE, [])
    return {"messages": messages, "count": len(messages)}

@app.post("/messages/send")
def send_message(message: Message):
    messages = load_json(MESSAGES_FILE, [])
    
    new_message = {
        "id": hashlib.sha256(f"{time.time()}{message.content}".encode()).hexdigest()[:16],
        "from_user": identity["username"],
        "to_user": message.to_user,
        "content": message.content,
        "encrypted": message.encrypted,
        "timestamp": time.time(),
        "sent_at": datetime.now().isoformat()
    }
    
    messages.append(new_message)
    save_json(MESSAGES_FILE, messages)
    
    return {"status": "sent", "message": new_message}

@app.get("/peers")
def get_peers():
    peers = load_json(PEERS_FILE, [])
    return {"peers": peers, "count": len(peers)}

@app.post("/peers/add")
def add_peer(peer: PeerInfo):
    peers = load_json(PEERS_FILE, [])
    
    # Check if peer already exists
    for p in peers:
        if p["peer_id"] == peer.peer_id:
            p["last_seen"] = peer.last_seen
            save_json(PEERS_FILE, peers)
            return {"status": "updated", "peer": p}
    
    new_peer = peer.dict()
    peers.append(new_peer)
    save_json(PEERS_FILE, peers)
    
    return {"status": "added", "peer": new_peer}

@app.delete("/peers/{peer_id}")
def remove_peer(peer_id: str):
    peers = load_json(PEERS_FILE, [])
    peers = [p for p in peers if p["peer_id"] != peer_id]
    save_json(PEERS_FILE, peers)
    return {"status": "removed", "peer_id": peer_id}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "identity": identity["username"],
        "data_dir": str(DATA_DIR)
    }

if __name__ == "__main__":
    print(f"Starting PURE Protocol Server...")
    print(f"Identity: {identity['username']}")
    print(f"Data directory: {DATA_DIR}")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
