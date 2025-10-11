(function () {
  const rows = document.getElementById("rows");
  const onlyActiveCb = document.getElementById("only-active");
  let es = null;
  let lastSince = new Date().toISOString();

  function fmt(v) { return v == null ? "" : v; }

  function upsertRow(item) {
    let tr = document.querySelector(`tr[data-id="${item.id}"]`);
    const html = `
      <td>${item.id}</td>
      <td>${item.machine}</td>
      <td>${item.type}</td>
      <td>${item.active ? "yes" : "no"}</td>
      <td>${fmt(item.started_at)}</td>
      <td>${fmt(item.resolved_at)}</td>
      <td>${fmt(item.last_timeslot)}</td>
      <td>${fmt(item.details)}</td>
    `;
    if (!tr) {
      tr = document.createElement("tr");
      tr.dataset.id = String(item.id);
      rows.prepend(tr);
    }
    tr.className = item.active ? "" : "inactive";
    tr.innerHTML = html;
  }

  function loadOnce(active) {
    const q = active ? "true" : "all";
    return fetch(`/api/incidents?active=${q}&limit=200`)
      .then(r => r.json())
      .then(data => {
        rows.innerHTML = "";
        data.items.forEach(upsertRow);
        lastSince = new Date().toISOString();
      })
      .catch(console.error);
  }

  function connect(active) {
    if (es) { try { es.close(); } catch {} es = null; }
    const q = active ? "true" : "all";
    es = new EventSource(`/api/incidents/stream?active=${q}&since=${encodeURIComponent(lastSince)}`);
    es.addEventListener("incidents", (ev) => {
      try {
        const payload = JSON.parse(ev.data);
        payload.items.forEach(upsertRow);
        if (payload.ts) lastSince = payload.ts;
      } catch (e) { console.error(e); }
    });
    es.onerror = () => {
      try { es.close(); } catch {}
      setTimeout(() => connect(active), 1500);
    };
  }

  function start() {
    const initialActive = (window.DEFAULT_ACTIVE || "true") === "true";
    onlyActiveCb.checked = initialActive;
    loadOnce(initialActive).then(() => connect(initialActive));
    onlyActiveCb.addEventListener("change", () => {
      loadOnce(onlyActiveCb.checked).then(() => connect(onlyActiveCb.checked));
    });
  }

  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", start) : start();
})();
