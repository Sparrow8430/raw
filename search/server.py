#!/usr/bin/env python3
"""
Simple local search server for PURE
Serves a JSON list of demo local results
"""

from flask import Flask, request, jsonify

app = Flask("pure-search")

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []

    if q:
        results.append({
            "title": f"Local result for {q}",
            "snippet": f"This is a demo hit for '{q}'",
            "url": f"pure://local/{q}"
        })
    else:
        results.append({
            "title": "PURE Search",
            "snippet": "Type a query to search local content",
            "url": "pure://local/"
        })

    return jsonify({"query": q, "results": results})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888)
