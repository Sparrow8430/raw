#!/usr/bin/env python3
"""
PURE Protocol Server v0.2
- TCP server with peer registry
- Node identity via RSA keypair
- Minimal handshake:
    CLIENT -> "HELLO <client_pub>"
    SERVER -> "WELCOME <server_pub>"
- Supports PING -> PONG and echo fallback
- Tracks peers with roles and last_seen
"""

import socket
import threading
import os
import json
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

HOST = "0.0.0.0"
PORT = 9000
KEY_DIR = os.path.expanduser("~/.pure/keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")
PEERS_PATH = os.path.expanduser("~/.pure/peers.json")

peers = {}  # pubkey -> {ip, port, role, last_seen}

# -------------------------
# Key management
# -------------------------
def ensure_keys():
    os.makedirs(KEY_DIR, exist_ok=True)
    if not os.path.exists(PRIVATE_KEY_PATH):
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem_priv = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        pem_pub = priv.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(pem_priv)
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(pem_pub)
        print("[*] Generated new node keypair in", KEY_DIR)
    else:
        print("[*] Using existing keys in", KEY_DIR)

def load_public():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()

# -------------------------
# Peer registry
# -------------------------
def load_peers():
    global peers
    if os.path.exists(PEERS_PATH):
        with open(PEERS_PATH, "r") as f:
            peers = json.load(f)
    else:
        peers = {}

def save_peers():
    with open(PEERS_PATH, "w") as f:
        json.dump(peers, f, indent=2)

def register_peer(pubkey, addr, role="INITIATE"):
    peers[pubkey] = {
        "ip": addr[0],
        "port": addr[1],
        "role": role,
        "last_seen": time.time()
    }
    save_peers()
    print(f"[+] Registered peer: {pubkey[:20]}..., role={role}, addr={addr}")

# -------------------------
# Connection handler
# -------------------------
def handle_conn(conn, addr, server_pub):
    print(f"[+] Connection from {addr}")
    try:
        data = conn.recv(4096).decode().strip()
        if not data:
            return
        parts = data.split(maxsplit=1)
        if parts[0].upper() == "HELLO" and len(parts) == 2:
            client_pub = parts[1]
            # Invite system placeholder
            client_role = "INITIATE"  # Later: validate invite
            register_peer(client_pub, addr, client_role)
            conn.sendall(f"WELCOME {server_pub}\n".encode())

            # Message loop
            while True:
                msg = conn.recv(4096)
                if not msg:
                    break
                text = msg.decode().strip()
                if text.upper() == "PING":
                    conn.sendall(b"PONG\n")
                else:
                    conn.sendall(f"ECHO: {text}\n".encode())
        else:
            conn.sendall(b"ERR malformed handshake\n")
    except Exception as e:
        print("[-] Connection handler error:", e)
    finally:
        conn.close()

# -------------------------
# Main server
# -------------------------
def main():
    ensure_keys()
    load_peers()
    server_pub = load_public()
    print(f"[*] Server public key (first line): {server_pub.splitlines()[0]}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[PURE] protocol server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_conn, args=(conn, addr, server_pub))
            t.daemon = True
            t.start()

if __name__ == "__main__":
    main()