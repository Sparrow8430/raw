# PURE - Complete Setup Guide

This guide will walk you through setting up PURE on GitHub and deploying it on a Linux system.

## Repository Structure

You'll need to create **4 repositories** on GitHub:

1. `pure-installer` - Main installer script
2. `pure-protocol` - Protocol/messaging server
3. `pure-search` - Search/indexing server
4. `pure-browser` - Electron GUI client

## Step 1: Create GitHub Repositories

### 1.1 Create Repositories

Go to GitHub and create these four repositories:

```
https://github.com/YOUR_USERNAME/pure-installer
https://github.com/YOUR_USERNAME/pure-protocol
https://github.com/YOUR_USERNAME/pure-search
https://github.com/YOUR_USERNAME/pure-browser
```

Make them all **public** (or private if you prefer).

### 1.2 Update install.sh

Before uploading, edit `install.sh` and replace `YOUR_USERNAME` with your actual GitHub username:

```bash
# Find these lines and update:
git clone https://github.com/YOUR_USERNAME/pure-protocol.git
git clone https://github.com/YOUR_USERNAME/pure-search.git
git clone https://github.com/YOUR_USERNAME/pure-browser.git
```

## Step 2: Upload Files to GitHub

### 2.1 pure-installer Repository

```bash
cd /tmp
mkdir pure-installer
cd pure-installer

# Create files
cat > install.sh << 'EOF'
[paste install.sh content here]
EOF

cat > README.md << 'EOF'
[paste main README.md content here]
EOF

cat > TESTING.md << 'EOF'
[paste TESTING.md content here]
EOF

# Initialize and push
git init
git add .
git commit -m "Initial commit: PURE installer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pure-installer.git
git push -u origin main
```

### 2.2 pure-protocol Repository

```bash
cd /tmp
mkdir pure-protocol
cd pure-protocol

# Create main.py
cat > main.py << 'EOF'
[paste pure-protocol/main.py content here]
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
cryptography==41.0.7
python-multipart==0.0.6
EOF

# Create README
cat > README.md << 'EOF'
[paste pure-protocol/README.md content here]
EOF

# Initialize and push
git init
git add .
git commit -m "Initial commit: PURE protocol server"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pure-protocol.git
git push -u origin main
```

### 2.3 pure-search Repository

```bash
cd /tmp
mkdir pure-search
cd pure-search

# Create main.py
cat > main.py << 'EOF'
[paste pure-search/main.py content here]
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
EOF

# Create README
cat > README.md << 'EOF'
[paste pure-search/README.md content here]
EOF

# Initialize and push
git init
git add .
git commit -m "Initial commit: PURE search server"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pure-search.git
git push -u origin main
```

### 2.4 pure-browser Repository

```bash
cd /tmp
mkdir pure-browser
cd pure-browser

# Create package.json
cat > package.json << 'EOF'
{
  "name": "pure-browser",
  "version": "0.1.0",
  "description": "PURE Decentralized Browser Client",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "dev": "electron . --dev"
  },
  "keywords": ["pure", "decentralized", "p2p"],
  "author": "PURE",
  "license": "MIT",
  "dependencies": {
    "electron": "^27.0.0",
    "axios": "^1.6.0"
  }
}
EOF

# Create main.js
cat > main.js << 'EOF'
[paste pure-browser/main.js content here]
EOF

# Create index.html
cat > index.html << 'EOF'
[paste pure-browser/index.html content here]
EOF

# Create README
cat > README.md << 'EOF'
[paste pure-browser/README.md content here]
EOF

# Initialize and push
git init
git add .
git commit -m "Initial commit: PURE browser client"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pure-browser.git
git push -u origin main
```

## Step 3: Installation on Linux

### 3.1 Prerequisites

Install required packages:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip nodejs npm git curl

# Verify installations
python3 --version  # Should be 3.8+
node --version     # Should be 16+
npm --version
git --version
```

### 3.2 Run Installer

**Option 1: Direct curl installation**
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pure-installer/main/install.sh | bash
```

**Option 2: Download and run manually**
```bash
wget https://raw.githubusercontent.com/YOUR_USERNAME/pure-installer/main/install.sh
chmod +x install.sh
./install.sh
```

### 3.3 Wait for Installation

The installer will:
1. ✓ Check dependencies
2. ✓ Create directory structure
3. ✓ Clone repositories
4. ✓ Install Python packages
5. ✓ Install Node packages
6. ✓ Create startup scripts

This takes 3-5 minutes depending on your connection.

## Step 4: First Run

### 4.1 Start PURE

```bash
~/.pure/start.sh
```

You should see:
```
Starting PURE system...
✓ pure-protocol started (PID: 12345)
✓ pure-search started (PID: 12346)
✓ pure-browser started (PID: 12347)

PURE is running!
Protocol API: http://localhost:8001
Search API: http://localhost:8002
Browser: Opening in new window...
```

### 4.2 Verify Installation

The browser window should open automatically showing the PURE dashboard.

**Quick API test:**
```bash
# Check protocol server
curl http://localhost:8001/health

# Check search server
curl http://localhost:8002/health

# Get your identity
curl http://localhost:8001/identity
```

Expected: All three commands return JSON responses without errors.

## Step 5: Test the System

### 5.1 Send a Test Message

In the browser:
1. Click "Messages" in the sidebar
2. Enter `test_user` as recipient
3. Type "Hello PURE!"
4. Click "Send Message"
5. Verify it appears in history below

### 5.2 Add a Test Document

In the browser:
1. Click "Search" in the sidebar
2. Enter title: "Test Document"
3. Enter content: "This is my first PURE document"
4. Enter tags: "test, demo"
5. Click "Add Document"
6. Try searching for "first"

### 5.3 Add a Test Peer

In the browser:
1. Click "Network" in the sidebar
2. Enter peer ID: "test_peer_001"
3. Enter address: "192.168.1.100"
4. Enter port: 8001
5. Click "Add Peer"
6. Verify it appears in the list

## Step 6: Stop PURE

When you're done:

```bash
~/.pure/stop.sh
```

You should see:
```
Stopping PURE system...
✓ pure-protocol stopped
✓ pure-search stopped
✓ pure-browser stopped
PURE stopped.
```

## Directory Structure

After installation, you'll have:

```
~/.pure/
├── data/                    # All user data
│   ├── identity.json       # Your identity
│   ├── messages.json       # Message history
│   ├── peers.json          # Connected peers
│   └── index/
│       └── documents.json  # Indexed documents
├── keys/                   # Encryption keys
│   └── encryption.key
├── logs/                   # Application logs
│   ├── protocol.log
│   ├── search.log
│   └── browser.log
├── system/                 # Application code
│   ├── pure-protocol/
│   ├── pure-search/
│   └── pure-browser/
├── start.sh               # Start script
└── stop.sh                # Stop script
```

## Common Issues

### Issue: Port Already in Use

**Symptom:** Installer fails with "port already in use"

**Solution:**
```bash
# Find and kill processes on ports 8001 and 8002
lsof -ti:8001 | xargs kill -9
lsof -ti:8002 | xargs kill -9
```

### Issue: Python Module Not Found

**Symptom:** "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
cd ~/.pure/system/pure-protocol
pip3 install --user -r requirements.txt

cd ~/.pure/system/pure-search
pip3 install --user -r requirements.txt
```

### Issue: Electron Won't Start

**Symptom:** Browser window doesn't open

**Solution:**
```bash
cd ~/.pure/system/pure-browser
npm install
npm start
```

### Issue: Permission Denied

**Symptom:** "Permission denied" when running start.sh

**Solution:**
```bash
chmod +x ~/.pure/start.sh
chmod +x ~/.pure/stop.sh
```

## Updating PURE

To update to the latest version:

```bash
# Stop PURE
~/.pure/stop.sh

# Pull latest changes
cd ~/.pure/system/pure-protocol && git pull
cd ~/.pure/system/pure-search && git pull
cd ~/.pure/system/pure-browser && git pull && npm install

# Restart
~/.pure/start.sh
```

## Uninstallation

To completely remove PURE:

```bash
# Stop PURE
~/.pure/stop.sh

# Remove all files
rm -rf ~/.pure

# Remove symlink (if created)
sudo rm /usr/local/bin/pure
```

## Next Steps

Now that PURE is installed:

1. **Explore the Interface** - Try all sections in the browser
2. **Read the Documentation** - Check individual component READMEs
3. **Test the APIs** - Use curl to interact with the servers
4. **Customize** - Modify the code to add features
5. **Connect Peers** - Set up PURE on another machine and connect them

## Getting Help

- Check logs: `~/.pure/logs/`
- Read TESTING.md for detailed testing procedures
- Check individual component READMEs
- File issues on GitHub

## Contributing

To contribute to PURE:

1. Fork the relevant repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Architecture Overview

```
┌─────────────────┐
│  pure-browser   │ (Electron GUI)
│  Port: N/A      │
└────────┬────────┘
         │ HTTP/IPC
         │
    ┌────┴──────────────┐
    │                   │
┌───▼──────────┐  ┌────▼──────────┐
│ pure-protocol│  │  pure-search  │
│ Port: 8001   │  │  Port: 8002   │
└──────┬───────┘  └───────┬───────┘
       │                  │
       │                  │
   ┌───▼──────────────────▼───┐
   │   ~/.pure/data/          │
   │   (Local Storage)        │
   └──────────────────────────┘
```

## Philosophy

PURE follows these principles:

- **Local-First**: All data on your machine
- **Privacy**: No external servers
- **Ownership**: You control everything
- **Simplicity**: Easy to understand and modify
- **Extensible**: Build on the foundation

---

**Welcome to PURE - Your Personal Decentralized Internet**

You now have a working decentralized OS running locally. This is just the beginning. The peer networking, encryption, and distributed features will come in future updates.

For now, enjoy your private, local-first communication and knowledge management system!
