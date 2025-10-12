(() => {
  const tbody = document.getElementById('rows');
  const onlyActive = document.getElementById('only-active');

  const esc = s => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

  function activeParam() { return onlyActive.checked ? 'true' : 'false'; }

  async function load() {
    try {
      const r = await fetch(`/api/incidents?active=${activeParam()}`, { credentials: 'same-origin' });
      if (!r.ok) return;
      const data = await r.json();
      const items = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : []);
      render(items);
    } catch { /* молчим */ }
  }

  function render(items) {
    tbody.innerHTML = items.map(it => `
      <tr data-id="${it.id}">
        <td>${it.id}</td>
        <td>${esc(it.machine_name ?? it.machine ?? '')}</td>
        <td>${esc(it.type_label ?? it.type ?? '')}</td>
        <td>${it.active ? 'yes' : 'no'}</td>
        <td>${esc(it.started_at ?? '')}</td>
        <td>${esc(it.resolved_at ?? '')}</td>
        <td>${esc(it.last_timeslot ?? '')}</td>
        <td>${esc(it.details ?? '')}</td>
      </tr>
    `).join('');
  }

  onlyActive.addEventListener('change', load);

  onlyActive.checked = (window.DEFAULT_ACTIVE ?? 'true') === 'true';


  load();


  setInterval(load, 5000);


  try {
    const es = new EventSource('/api/incidents/stream');
    es.onmessage = () => load();
    es.onerror   = () => { try { es.close(); } catch {} }; // не спамим ошибками
    window.addEventListener('beforeunload', () => { try { es.close(); } catch {} });
  } catch {}
})();
