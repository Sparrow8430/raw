#!/usr/bin/env python3
"""
PURE protocol client v0.3 - FIXED VERSION
Now includes proper RSA authentication
Usage: python3 client.py <host> <port>
"""
import socket
import sys
import os
import json
import threading
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

KEY_DIR = os.path.expanduser("~/.pure/keys")
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private.pem")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "node_public.pem")
IDENTITY_PATH = os.path.expanduser("~/.pure/identity.json")

def load_public():
    """Load public key as PEM string"""
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return f.read().decode().strip()

def load_private_key():
    """Load private key for signing"""
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

def sign_challenge(challenge):
    """Sign a challenge string with our private key"""
    private_key = load_private_key()
    signature = private_key.sign(
        challenge.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature.hex()

def load_identity():
    """Load identity configuration"""
    if os.path.exists(IDENTITY_PATH):
        with open(IDENTITY_PATH, "r") as f:
            return json.load(f)
    return {"role": "INITIATE", "invites": []}

def receive_messages(sock):
    """Background thread to receive and display messages"""
    buffer = ""
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print("\n[!] Connection closed by server")
                break
            
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                
                if not line:
                    continue
                
                # Try to parse as JSON
                try:
                    msg = json.loads(line)
                    if msg.get("type") == "CHAT":
                        sender = msg.get("sender", "Unknown")
                        message = msg.get("message", "")
                        timestamp = msg.get("timestamp", "")
                        print(f"\n[{timestamp}] {sender}: {message}")
                    elif msg.get("type") == "HISTORY":
                        print("\n--- Chat History ---")
                        for m in msg.get("messages", []):
                            print(f"[{m['timestamp']}] {m['sender']}: {m['message']}")
                        print("--- End History ---")
                    elif msg.get("type") == "PEERS":
                        print("\n--- Connected Peers ---")
                        for p in msg.get("peers", []):
                            print(f"  {p['pubkey']}... ({p['role']})")
                        print("--- End Peers ---")
                    else:
                        print(f"\n[SERVER] {line}")
                except json.JSONDecodeError:
                    print(f"\n[SERVER] {line}")
    
    except Exception as e:
        print(f"\n[!] Error receiving messages: {e}")

def main():
    """Main client function"""
    if len(sys.argv) < 3:
        print("Usage: client.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    # Check if keys exist
    if not os.path.exists(PRIVATE_KEY_PATH):
        print("[!] Error: Keys not found. Run the server first to generate keys.")
        sys.exit(1)
    
    pub = load_public()
    identity = load_identity()
    invite_code = identity.get("invites", [None])[0]
    
    # Build HELLO message
    hello_msg = f"HELLO {pub}"
    if invite_code:
        hello_msg += f" INVITE {invite_code}"
    
    print(f"[*] Connecting to {host}:{port}...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            print("[✓] Connected!")
            
            # Phase 1: Send HELLO
            print("[*] Sending HELLO...")
            sock.sendall(f"{hello_msg}\n".encode())
            
            # Phase 2: Receive CHALLENGE
            response = sock.recv(4096).decode().strip()
            print(f"[<] {response}")
            
            if not response.startswith("CHALLENGE "):
                print("[!] Expected CHALLENGE, got:", response)
                return
            
            challenge = response.split(" ", 1)[1]
            print(f"[*] Received challenge: {challenge[:32]}...")
            
            # Phase 3: Sign and respond
            print("[*] Signing challenge...")
            signature = sign_challenge(challenge)
            sock.sendall(f"RESPONSE {signature}\n".encode())
            print("[✓] Sent signature")
            
            # Phase 4: Receive WELCOME
            welcome = sock.recv(4096).decode().strip()
            print(f"[<] {welcome[:50]}...")
            
            if not welcome.startswith("WELCOME "):
                print("[!] Authentication failed:", welcome)
                return
            
            print("[✓] Authenticated successfully!")
            print("\n" + "="*50)
            print("Connected to PURE Network")
            print("="*50)
            print("Commands:")
            print("  CHAT <message>  - Send a chat message")
            print("  PEERS           - List connected peers")
            print("  PING            - Ping the server")
            print("  quit            - Exit")
            print("="*50 + "\n")
            
            # Start message receiver thread
            receiver = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
            receiver.start()
            
            # Interactive loop
            try:
                while True:
                    user_input = input("> ")
                    
                    if user_input.lower() == "quit":
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    # Send command to server
                    sock.sendall(f"{user_input}\n".encode())
            
            except KeyboardInterrupt:
                print("\n[*] Disconnecting...")
        
        except ConnectionRefusedError:
            print(f"[!] Connection refused. Is the server running on {host}:{port}?")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
