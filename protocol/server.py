#!/usr/bin/env python3
"""
PURE protocol server v0.2 — invite-only / role system
- TCP server, simple handshake with client public key
- Optional invite code for access control
- Maintains node identity with role in ~/.pure/identity.json
"""

import socket
import threading
import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

HOST = "0.0.0.0"
PORT = 9000
KEY_DIR = os.path.expanduser("~/.pure/keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")
IDENTITY_PATH = os.path.expanduser("~/.pure/identity.json")
INVITES_PATH = os.path.expanduser("~/.pure/invites.txt")

# ------------------- Setup -------------------
def ensure_keys():
    os.makedirs(KEY_DIR, exist_ok=True)
    if not os.path.exists(PRIVATE_KEY_PATH):
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub = priv.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(PRIVATE_KEY_PATH, "wb") as f: f.write(pem)
        with open(PUBLIC_KEY_PATH, "wb") as f: f.write(pub)
        print("[*] Generated new node keypair")
    else:
        print("[*] Using existing keys")

def load_public():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()

def load_identity():
    if not os.path.exists(IDENTITY_PATH):
        os.makedirs(os.path.dirname(IDENTITY_PATH), exist_ok=True)
        identity = {"role": "INITIATE", "invites": []}
        with open(IDENTITY_PATH, "w") as f:
            json.dump(identity, f)
    else:
        with open(IDENTITY_PATH, "r") as f:
            identity = json.load(f)
    return identity

def load_invites():
    if os.path.exists(INVITES_PATH):
        with open(INVITES_PATH, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# ------------------- Connection -------------------
def handle_conn(conn, addr, server_pub, invites):
    print(f"[+] Connection from {addr}")
    try:
        data = conn.recv(4096).decode().strip()
        if not data:
            return

        parts = data.split()
        if parts[0].upper() != "HELLO":
            conn.sendall(b"ERR malformed handshake\n")
            return

        client_pub = parts[1]
        client_invite = None
        if len(parts) >= 4 and parts[2].upper() == "INVITE":
            client_invite = parts[3]

        if client_invite and client_invite not in invites:
            conn.sendall(b"ERR invalid invite\n")
            print(f"[-] Invalid invite from {addr}")
            return

        print(f"[>] HELLO from client pub (len {len(client_pub)})")
        response = f"WELCOME {server_pub}\nROLE ARCHON\nSTATUS OK\n"
        conn.sendall(response.encode())

        while True:
            msg = conn.recv(4096)
            if not msg: break
            text = msg.decode().strip()
            if text.upper() == "PING":
                conn.sendall(b"PONG\n")
            else:
                conn.sendall(f"ECHO: {text}\n".encode())

    except Exception as e:
        print(f"[-] Connection error: {e}")
    finally:
        conn.close()

# ------------------- Main -------------------
def main():
    ensure_keys()
    server_pub = load_public()
    identity = load_identity()
    invites = load_invites()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[PURE] protocol server listening on {HOST}:{PORT}")
        print("[*] Server public key (first line):", server_pub.splitlines()[0])
        print("[*] Server role:", identity.get("role"))

        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_conn, args=(conn, addr, server_pub, invites))
            t.daemon = True
            t.start()

if __name__ == "__main__":
    main()