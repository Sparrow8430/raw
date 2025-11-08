// Preload: expose a safe search API to renderer via contextBridge
const { contextBridge } = require('electron');
const http = require('http');
const https = require('https');
const { URL } = require('url');

function doFetch(url) {
  return new Promise((resolve, reject) => {
    try {
      const u = new URL(url);
      const lib = u.protocol === 'http:' ? http : https;
      const req = lib.request(u, { method: 'GET', timeout: 15000 }, (res) => {
        let data = '';
        res.on('data', (d) => data += d);
        res.on('end', () => {
          try { resolve(JSON.parse(data)); } catch (e) { resolve(data); }
        });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
      req.end();
    } catch (e) { reject(e); }
  });
}

contextBridge.exposeInMainWorld('pure', {
  // q -> performs a search against local searx (default port 8080)
  search: async (q) => {
    if (!q || typeof q !== 'string') return { error: 'invalid query' };
    const url = `http://127.0.0.1:8080/search?q=${encodeURIComponent(q)}&format=json`;
    return doFetch(url).catch(e => ({ error: String(e) }));
  }
});
