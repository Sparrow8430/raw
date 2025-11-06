async function search(q) {
  try {
    const res = await fetch(`http://127.0.0.1:8888/search?q=${encodeURIComponent(q)}`);
    const json = await res.json();
    return JSON.stringify(json, null, 2);
  } catch (e) {
    return "Search error: " + e;
  }
}

async function pingPeer(hostport) {
  // Use a tiny proxy approach: browser cannot open raw TCP.
  // We'll hit a local helper endpoint if you run one later.
  // For MVP just attempt a TCP connection via protocol client script manually.
  return "For TCP peer test, run: python3 protocol/client.py " + hostport;
}

document.getElementById("searchBtn").onclick = async () => {
  const q = document.getElementById("query").value;
  document.getElementById("results").textContent = await search(q);
};

document.getElementById("connectBtn").onclick = async () => {
  const peer = document.getElementById("peer").value;
  document.getElementById("results").textContent = await pingPeer(peer);
};
