#!/usr/bin/env python3
"""
Flask server for PURE Ritual language UI
Handles search queries and optional Ritual script execution
"""

import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from local Electron/browser UI

# -------------------------------
# Simple search API (demo)
# -------------------------------

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"query": q, "results": []})
    return jsonify({
        "query": q,
        "results": [
            {
                "title": f"Local result for {q}",
                "url": f"pure://local/{q}",
                "snippet": f"This is a demo hit for '{q}'"
            }
        ]
    })

# -------------------------------
# Optional Ritual execution endpoint
# -------------------------------

@app.route("/run", methods=["POST"])
def run_ritual():
    data = request.get_json()
    script_path = data.get("script")
    if not script_path:
        return jsonify({"error": "No script path provided"}), 400

    # Resolve absolute path
    repo_root = os.path.dirname(os.path.abspath(__file__))
    ritual_script = os.path.join(repo_root, "ritual_esolang.py")
    if not os.path.isfile(ritual_script):
        return jsonify({"error": f"Ritual interpreter not found at {ritual_script}"}), 500

    try:
        result = subprocess.run(
            ["python3", ritual_script, script_path],
            capture_output=True, text=True, check=True
        )
        return jsonify({"output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500

# -------------------------------
# Health check
# -------------------------------

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

# -------------------------------
# Run server
# -------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)

