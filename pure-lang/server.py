#!/usr/bin/env python3
"""
Flask server for PURE Ritual language UI
- Handles search queries
- Runs Ritual scripts via POST /run
- CORS enabled for local Electron/browser UI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)  # allow cross-origin requests from Electron/browser UI

# -------------------------------
# Search API (demo)
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
# Ritual execution endpoint
# -------------------------------

@app.route("/run", methods=["POST"])
def run_ritual():
    data = request.get_json()
    script_path = data.get("script")
    if not script_path:
        return jsonify({"error": "No script path provided"}), 400

    script_path = os.path.expanduser(script_path)
    if not os.path.isfile(script_path):
        return jsonify({"error": f"Script not found: {script_path}"}), 404

    try:
        result = subprocess.run(
            ["python3", "ritual_esolang.py", script_path],
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
