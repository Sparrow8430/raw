#!/usr/bin/env python3
"""
Flask server for PURE Ritual language UI
Handles search queries and optional Ritual script execution
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(**name**)
CORS(app)  # Allow cross-origin requests from local Electron/browser UI

# -------------------------------

# Simple search API (demo)

# -------------------------------

@app.route("/search")
def search():
q = request.args.get("q", "").strip()
# Demo: return a simple "hit" if query exists
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
try:
# Run the ritual script as a subprocess
import subprocess
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

if **name** == "**main**":
app.run(host="0.0.0.0", port=8888)
