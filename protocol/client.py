#!/usr/bin/env python3
"""
Simple protocol client for PURE
Usage:
  python3 protocol/client.py <host> <port>
"""

import socket
import sys
import os

KEY_DIR = os.path.expanduser("~/.pure/keys")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")

def load_public():
    if not os.path.isfile(PUBLIC_KEY_PATH):
        print(f"Public key not found at {PUBLIC_KEY_PATH}")
        sys.exit(1)
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()

def main():
    if len(sys.argv) < 3:
        print("Usage: client.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    pub = load_public()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(f"HELLO {pub}\n".encode())
        resp = s.recv(4096).decode()
        print("Server replied:", resp.strip())

        # Test ping
        s.sendall(b"PING\n")
        print("Reply to PING:", s.recv(4096).decode().strip())

        # Test echo
        s.sendall(b"hi from client\n")
        print("Echo:", s.recv(4096).decode().strip())

if __name__ == "__main__":
    main()
