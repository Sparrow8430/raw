#!/usr/bin/env python3
"""
Pure protocol server (v0.1)
- Simple TCP server
- Node identity via public key
- Accepts connections, performs a minimal handshake:
    CLIENT -> "HELLO <client_pub>"
    SERVER verifies format and replies "WELCOME <server_pub>"
- Supports "PING" -> "PONG" and echo fallback
"""

import socket
import threading
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

HOST = "0.0.0.0"
PORT = 9000
KEY_DIR = os.path.expanduser("~/.pure/keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")

def ensure_keys():
    os.makedirs(KEY_DIR, exist_ok=True)
    if not os.path.exists(PRIVATE_KEY_PATH):
        # generate key
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
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(pem)
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(pub)
        print("[*] Generated new node keypair in", KEY_DIR)
    else:
        print("[*] Using existing keys in", KEY_DIR)

def load_public():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()

def handle_conn(conn, addr, server_pub):
    print(f"[+] Connection from {addr}")
    try:
        data = conn.recv(4096).decode().strip()
        if not data:
            return
        parts = data.split(maxsplit=1)
        if parts[0].upper() == "HELLO" and len(parts) == 2:
            client_pub = parts[1]
            print(f"[>] HELLO from client pub (len {len(client_pub)})")
            conn.sendall(f"WELCOME {server_pub}\n".encode())
            # Now simple message loop
            while True:
                msg = conn.recv(4096)
                if not msg: break
                text = msg.decode().strip()
                if text.upper() == "PING":
                    conn.sendall(b"PONG\n")
                else:
                    conn.sendall(f"ECHO: {text}\n".encode())
        else:
            conn.sendall(b"ERR malformed handshake\n")
    except Exception as e:
        print("[-] connection handler error:", e)
    finally:
        conn.close()

def main():
    ensure_keys()
    server_pub = load_public()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[PURE] protocol server listening on {HOST}:{PORT}")
        print("[*] Server public key (PEM, first line):", server_pub.splitlines()[0])
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_conn, args=(conn, addr, server_pub))
            t.daemon = True
            t.start()

if __name__ == "__main__":
    main()
