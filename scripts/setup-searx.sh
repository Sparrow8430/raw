#!/usr/bin/env bash
set -e

echo "Creating Python virtual environment..."
python3 -m venv searx-venv

source searx-venv/bin/activate
echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing SearxNG..."
pip install git+https://github.com/searxng/searxng.git

echo "✅ Done!"
echo "To run SearxNG:"
echo "  source searx-venv/bin/activate"
echo "  python -m searx.webapp"
