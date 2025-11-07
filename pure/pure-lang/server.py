#!/usr/bin/env python3
# pure/pure-lang/server.py
from flask import Flask, request, jsonify
import subprocess, os, shlex, threading

app = Flask("pure-ritual")

RITUAL_DIR = os.path.expanduser("~/pure/rituals")
os.makedirs(RITUAL_DIR, exist_ok=True)

def run_ritual_async(path):
    # run ritual_esolang.py with the script path
    cmd = f"python3 {os.path.expanduser('~/pure/pure-lang/ritual_esolang.py')} {shlex.quote(path)}"
    proc = subprocess.Popen(cmd, shell=True)
    return proc

@app.route("/ritual/run", methods=["POST"])
def ritual_run():
    data = request.json or {}
    script = data.get("script")  # script text
    name = data.get("name", "untitled.txt")
    if not script:
        return jsonify({"ok": False, "error": "no script provided"}), 400
    safe_name = "".join(c for c in name if c.isalnum() or c in "._-")[:64]
    path = os.path.join(RITUAL_DIR, safe_name)
    with open(path, "w") as f:
        f.write(script)
    proc = run_ritual_async(path)
    return jsonify({"ok": True, "pid": proc.pid, "path": path})

@app.route("/ritual/list", methods=["GET"])
def ritual_list():
    files = [f for f in os.listdir(RITUAL_DIR) if os.path.isfile(os.path.join(RITUAL_DIR,f))]
    return jsonify({"ok": True, "files": files})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8899)
