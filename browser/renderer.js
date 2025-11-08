// renderer
document.getElementById('go').onclick = async () => {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  document.getElementById('results').textContent = 'Searching...';
  const res = await window.pure.search(q);
  if (res && res.error) {
    document.getElementById('results').innerHTML = `<div style="color:red">${res.error}</div>`;
    return;
  }
  // searx JSON format: results array usually in res.results
  const hits = res.results || res.engine_results || [];
  if (!hits.length) {
    document.getElementById('results').innerHTML = `<div>No results</div><pre>${JSON.stringify(res, null, 2)}</pre>`;
    return;
  }
  document.getElementById('results').innerHTML = hits.map(h => `
    <div class="result">
      <div class="title"><a href="${h.url}" target="_blank">${h.title || h.url}</a></div>
      <div class="snippet">${h.snippet || ''}</div>
      <div style="font-size:12px;color:#666">${h.url}</div>
    </div>
  `).join('');
};
