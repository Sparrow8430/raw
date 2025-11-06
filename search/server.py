#!/usr/bin/env python3
"""
Simple local search stub for PURE v0.1
Serves a JSON list of fake local results. Later this will index local pages.
"""
from flask import Flask, request, jsonify
import os

app = Flask("pure-search")

@app.route("/search")
def search():
    q = request.args.get("q", "")
    results = []
    if q.strip():
        results.append({"title": f"Local result for {q}", "snippet": f"This is a demo hit for '{q}'", "url": f"pure://local/{q}"})
    else:
        results.append({"title": "PURE Search", "snippet": "Type a query to search local content", "url": "pure://local/"})
    return jsonify({"query": q, "results": results})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888)
