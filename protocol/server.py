#!/usr/bin/env python3
"""
PURE Protocol Server v0.3
- Secure peer-to-peer communication
- RSA key authentication with challenge-response
- Chat message broadcasting
- Peer discovery and registry
"""

import socket
import threading
import os
import json
import time
import hashlib
import secrets
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# Configuration
HOST = "0.0.0.0"
PORT = 9000
KEY_DIR = os.path.expanduser("~/.pure/keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")
PEERS_PATH = os.path.expanduser("~/.pure/peers.json")
CONFIG_PATH = os.path.expanduser("~/.pure/config.json")

# Global state
peers = {}  # pubkey -> {ip, port, role, last_seen, conn, challenge_passed}
active_connections = {}  # conn -> pubkey
chat_history = []  # List of chat messages
private_key = None
public_key = None

MAX_PEERS = 50
MAX_CHAT_HISTORY = 1000

# -------------------------
# Cryptographic Functions
# -------------------------

def ensure_keys():
    """Generate or load RSA keypair"""
    global private_key, public_key
    
    os.makedirs(KEY_DIR, exist_ok=True)
    
    if not os.path.exists(PRIVATE_KEY_PATH):
        print("[*] Generating new RSA keypair...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        pem_priv = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        pem_pub = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(pem_priv)
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(pem_pub)
        
        print(f"[*] Keypair saved to {KEY_DIR}")
    else:
        print("[*] Loading existing keypair...")
        with open(PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        public_key = private_key.public_key()
    
    print("[✓] Keys loaded successfully")


def load_public_pem():
    """Load public key as PEM string"""
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()


def verify_signature(pubkey_pem, message, signature):
    """Verify a signature using peer's public key"""
    try:
        pubkey = serialization.load_pem_public_key(
            pubkey_pem.encode(),
            backend=default_backend()
        )
        pubkey.verify(
            bytes.fromhex(signature),
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"[-] Signature verification failed: {e}")
        return False


def sign_message(message):
    """Sign a message with our private key"""
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature.hex()


# -------------------------
# Peer Management
# -------------------------

def load_peers():
    """Load peer registry from disk"""
    global peers
    if os.path.exists(PEERS_PATH):
        try:
            with open(PEERS_PATH, "r") as f:
                peers = json.load(f)
            print(f"[*] Loaded {len(peers)} known peers")
        except Exception as e:
            print(f"[-] Error loading peers: {e}")
            peers = {}
    else:
        peers = {}


def save_peers():
    """Save peer registry to disk"""
    try:
        # Remove connection objects before saving
        peers_to_save = {}
        for pubkey, data in peers.items():
            peers_to_save[pubkey] = {
                "ip": data["ip"],
                "port": data["port"],
                "role": data["role"],
                "last_seen": data["last_seen"],
                "challenge_passed": data.get("challenge_passed", False)
            }
        
        with open(PEERS_PATH, "w") as f:
            json.dump(peers_to_save, f, indent=2)
    except Exception as e:
        print(f"[-] Error saving peers: {e}")


def register_peer(pubkey, addr, role="INITIATE", conn=None):
    """Register or update a peer"""
    if len(peers) >= MAX_PEERS and pubkey not in peers:
        print(f"[-] Peer limit reached ({MAX_PEERS}), rejecting new peer")
        return False
    
    peers[pubkey] = {
        "ip": addr[0],
        "port": addr[1],
        "role": role,
        "last_seen": time.time(),
        "conn": conn,
        "challenge_passed": False
    }
    
    if conn:
        active_connections[conn] = pubkey
    
    save_peers()
    print(f"[+] Registered peer: {pubkey[:32]}..., role={role}, addr={addr}")
    return True


def remove_peer(conn):
    """Remove a peer when they disconnect"""
    if conn in active_connections:
        pubkey = active_connections[conn]
        if pubkey in peers:
            print(f"[-] Peer disconnected: {pubkey[:32]}...")
            del peers[pubkey]
        del active_connections[conn]
        save_peers()


# -------------------------
# Chat System
# -------------------------

def broadcast_message(message, sender_pubkey=None):
    """Broadcast a chat message to all connected peers"""
    msg_data = {
        "type": "CHAT",
        "sender": sender_pubkey[:32] if sender_pubkey else "SERVER",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to history
    chat_history.append(msg_data)
    if len(chat_history) > MAX_CHAT_HISTORY:
        chat_history.pop(0)
    
    # Broadcast to all connected peers
    msg_json = json.dumps(msg_data) + "\n"
    disconnected = []
    
    for conn, pubkey in active_connections.items():
        try:
            conn.sendall(msg_json.encode())
        except Exception as e:
            print(f"[-] Failed to send to {pubkey[:32]}...: {e}")
            disconnected.append(conn)
    
    # Clean up disconnected peers
    for conn in disconnected:
        remove_peer(conn)


# -------------------------
# Connection Handler
# -------------------------

def handle_connection(conn, addr):
    """Handle individual peer connection"""
    print(f"[+] Connection from {addr}")
    pubkey = None
    
    try:
        # Phase 1: HELLO handshake
        data = conn.recv(4096).decode().strip()
        if not data:
            conn.close()
            return
        
        parts = data.split()
        if parts[0].upper() != "HELLO" or len(parts) < 2:
            conn.sendall(b"ERR malformed handshake\n")
            conn.close()
            return
        
        # Extract public key
        pubkey_start = data.find("-----BEGIN PUBLIC KEY-----")
        pubkey_end = data.find("-----END PUBLIC KEY-----")
        if pubkey_start == -1 or pubkey_end == -1:
            conn.sendall(b"ERR invalid public key\n")
            conn.close()
            return
        
        client_pubkey = data[pubkey_start:pubkey_end + len("-----END PUBLIC KEY-----")]
        
        # Check for invite code (future feature)
        client_role = "INITIATE"
        if "INVITE" in data:
            # TODO: Validate invite code
            pass
        
        # Register peer
        if not register_peer(client_pubkey, addr, client_role, conn):
            conn.sendall(b"ERR peer limit reached\n")
            conn.close()
            return
        
        pubkey = client_pubkey
        
        # Phase 2: Challenge-response authentication
        challenge = secrets.token_hex(32)
        conn.sendall(f"CHALLENGE {challenge}\n".encode())
        
        response = conn.recv(4096).decode().strip()
        if not response.startswith("RESPONSE "):
            conn.sendall(b"ERR invalid challenge response\n")
            conn.close()
            return
        
        signature = response.split(" ", 1)[1]
        if not verify_signature(client_pubkey, challenge, signature):
            conn.sendall(b"ERR authentication failed\n")
            conn.close()
            return
        
        peers[pubkey]["challenge_passed"] = True
        
        # Send welcome with our public key
        server_pub = load_public_pem()
        conn.sendall(f"WELCOME {server_pub}\n".encode())
        
        print(f"[✓] Peer authenticated: {pubkey[:32]}...")
        
        # Send recent chat history
        if chat_history:
            history_msg = json.dumps({
                "type": "HISTORY",
                "messages": chat_history[-10:]
            }) + "\n"
            conn.sendall(history_msg.encode())
        
        # Announce new peer
        broadcast_message(f"Peer {pubkey[:8]}... joined", None)
        
        # Phase 3: Message loop
        buffer = ""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                
                if not line:
                    continue
                
                # Update last seen
                peers[pubkey]["last_seen"] = time.time()
                
                # Handle commands
                if line.upper() == "PING":
                    conn.sendall(b"PONG\n")
                
                elif line.upper() == "PEERS":
                    peer_list = [
                        {
                            "pubkey": pk[:32],
                            "role": p["role"],
                            "last_seen": p["last_seen"]
                        }
                        for pk, p in peers.items()
                        if p.get("challenge_passed")
                    ]
                    response = json.dumps({"type": "PEERS", "peers": peer_list}) + "\n"
                    conn.sendall(response.encode())
                
                elif line.startswith("CHAT "):
                    message = line[5:]
                    broadcast_message(message, pubkey)
                
                else:
                    # Echo unknown commands
                    conn.sendall(f"ECHO: {line}\n".encode())
    
    except Exception as e:
        print(f"[-] Connection error with {addr}: {e}")
    
    finally:
        if pubkey:
            remove_peer(conn)
        else:
            try:
                conn.close()
            except:
                pass


# -------------------------
# Main Server
# -------------------------

def main():
    """Start the PURE protocol server"""
    ensure_keys()
    load_peers()
    
    server_pub = load_public_pem()
    print("\n" + "="*50)
    print("PURE Protocol Server v0.3")
    print("="*50)
    print(f"Node ID: {server_pub.split('\n')[1][:32]}...")
    print(f"Listening on {HOST}:{PORT}")
    print("="*50 + "\n")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        
        print("[✓] Server started successfully")
        print("[*] Waiting for connections...\n")
        
        try:
            while True:
                conn, addr = server_socket.accept()
                thread = threading.Thread(
                    target=handle_connection,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
        
        except KeyboardInterrupt:
            print("\n[*] Shutting down server...")
            save_peers()
            print("[✓] Server stopped")


if __name__ == "__main__":
    main()
