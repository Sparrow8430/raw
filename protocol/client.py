#!/usr/bin/env python3
"""
PURE protocol client v0.2 — invite-aware
Usage: python3 client.py <host> <port>
"""
import socket
import sys
import os
import json

KEY_DIR = os.path.expanduser("~/.pure/keys")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")
IDENTITY_PATH = os.path.expanduser("~/.pure/identity.json")

def load_public():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()

def load_identity():
    if os.path.exists(IDENTITY_PATH):
        with open(IDENTITY_PATH, "r") as f:
            return json.load(f)
    return {"role": "INITIATE", "invites": []}

def main():
    if len(sys.argv) < 3:
        print("Usage: client.py <host> <port>")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])

    pub = load_public()
    identity = load_identity()
    invite_code = identity.get("invites", [None])[0]

    hello_msg = f"HELLO {pub}"
    if invite_code:
        hello_msg += f" INVITE {invite_code}"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(f"{hello_msg}\n".encode())
        resp = s.recv(4096).decode()
        print("Server replied:\n", resp.strip())

        s.sendall(b"PING\n")
        print("Reply to PING:", s.recv(4096).decode().strip())

        s.sendall(b"hi from client\n")
        print("Echo:", s.recv(4096).decode().strip())

if __name__ == "__main__":
    main()