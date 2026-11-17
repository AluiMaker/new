/* MapaLeads PRO SaaS - Frontend Controller */
const STATE = {
  leads: [],
  templates: [],
  segments: [],
  stats: null,
  crmView: 'kanban',
  selectedLead: null,
  selectedLocation: null,
  map: null,
  mapCluster: null,
  pinMarker: null,
  pinReverse: null,
  charts: { opps: null, funnel: null },
  sse: null,
  baileysPoll: null,
  chatFilter: 'all',
  activeChatLead: null,
  chatThreads: [],
};

const TAB_META = {
  'tab-dashboard': ['Visão Geral', 'Acompanhe suas oportunidades de venda e resultados no Google'],
  'tab-search': ['Buscar Empresas', 'Encontre negócios locais com telefone válido para ofertar seus serviços'],
  'tab-map': ['Mapa de Oportunidades', 'Visualize seus leads e clique em qualquer rua para prospectar'],
  'tab-crm': ['CRM & Pipeline', 'Gerencie negociações no Kanban ou em lista e envie abordagens'],
  'tab-chat': ['Chat / Conversas', 'Atenda e acompanhe suas conversas ativas estilo Kommo'],
  'tab-templates': ['Modelos de Copy', 'Mensagens prontas para Plaquinhas NFC, WhatsApp, Cardápio e Biossites'],
  'tab-settings': ['WhatsApp & Conta', 'Configure o WhatsApp por QR Code, API Oficial da Meta e seus dados'],
  'tab-admin': ['Painel Admin', 'Gerencie contas de clientes e planos do sistema'],
};

const OPP_LABELS = {
  nfc_google: { label: 'Plaquinha NFC + QR', cls: 'opp-nfc', icon: 'fa-wifi' },
  whatsapp_biz: { label: 'WhatsApp Business', cls: 'opp-wa', icon: 'fa-brands fa-whatsapp' },
  cardapio_digital: { label: 'Cardápio Digital', cls: 'opp-cardapio', icon: 'fa-utensils' },
  biossite: { label: 'Biossite / LP', cls: 'opp-bio', icon: 'fa-globe' },
};

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSearchControls();
  initCrmControls();
  initChatControls();
  initDrawerControls();
  initTemplateControls();
  initSettingsControls();
  initAdminControls();
  initSSE();

  loadAllData();
});

async function loadAllData() {
  await Promise.all([loadStats(), loadLeads(), loadTemplates(), loadSegments(), loadSearchHistory(), loadChatThreads()]);
  if (window.CURRENT_USER && window.CURRENT_USER.role === 'admin') {
    loadAdminUsers();
  }
}

async function apiFetch(url, opts = {}) {
  const res = await fetch(url, opts);
  if (res.status === 401) {
    window.location.href = '/login';
    throw new Error('Sessão expirada');
  }
  return res;
}

function toast(msg, type = 'info') {
  const box = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check' : type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info'}"></i><span>${escapeHtml(msg)}</span>`;
  box.appendChild(el);
  setTimeout(() => el.remove(), 4200);
}

function escapeHtml(s) {
  return String(s || '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}

function formatBRL(v) {
  return Number(v || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// ==================== NAVIGATION, THEME & SIDEBAR ====================
function initNavigation() {
  document.querySelectorAll('.nav-item[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  const openSidebarMobile = () => {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebar-backdrop')?.classList.remove('hidden');
  };
  const closeSidebarMobile = () => {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-backdrop')?.classList.add('hidden');
  };

  document.getElementById('btn-open-sidebar')?.addEventListener('click', openSidebarMobile);
  document.getElementById('btn-close-sidebar')?.addEventListener('click', closeSidebarMobile);
  document.getElementById('sidebar-backdrop')?.addEventListener('click', closeSidebarMobile);

  // Menu retrátil desktop
  const syncCollapseIcon = () => {
    const collapsed = document.body.classList.contains('sidebar-collapsed');
    const icon = document.querySelector('#btn-toggle-sidebar i');
    if (icon) icon.className = collapsed ? 'fa-solid fa-angles-right' : 'fa-solid fa-angles-left';
  };
  syncCollapseIcon();
  document.getElementById('btn-toggle-sidebar')?.addEventListener('click', () => {
    document.body.classList.toggle('sidebar-collapsed');
    const collapsed = document.body.classList.contains('sidebar-collapsed');
    localStorage.setItem('ml_sidebar_collapsed', collapsed ? '1' : '0');
    syncCollapseIcon();
    setTimeout(() => STATE.map?.invalidateSize(), 220);
  });

  // Modo Dark / Claro
  const syncThemeIcon = () => {
    const isDark = document.body.classList.contains('dark-theme');
    const icon = document.querySelector('#btn-toggle-theme i');
    if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  };
  syncThemeIcon();
  document.getElementById('btn-toggle-theme')?.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('ml_theme', isDark ? 'dark' : 'light');
    syncThemeIcon();
    if (STATE.stats) renderCharts(STATE.stats);
  });

  document.getElementById('btn-export-csv')?.addEventListener('click', () => {
    const opp = document.getElementById('crm-filter-opportunity')?.value || 'all';
    const wt = document.getElementById('crm-filter-website')?.value || 'all';
    window.location.href = `/api/export/csv?opportunity=${encodeURIComponent(opp)}&website_type=${encodeURIComponent(wt)}`;
  });
}

function switchTab(tabId) {
  document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
  document.querySelectorAll('.tab-view').forEach(v => v.classList.toggle('active', v.id === tabId));
  const meta = TAB_META[tabId] || ['MapaLeads PRO', ''];
  document.getElementById('topbar-title').textContent = meta[0];
  document.getElementById('topbar-subtitle').textContent = meta[1];
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-backdrop')?.classList.add('hidden');

  if (tabId === 'tab-map') {
    setTimeout(() => {
      initMap();
      STATE.map?.invalidateSize();
      renderMapMarkers();
    }, 120);
  }
  if (tabId === 'tab-dashboard') {
    loadStats();
  }
  if (tabId === 'tab-chat') {
    loadChatThreads();
  }
  if (tabId !== 'tab-settings') {
    stopBaileysPolling();
  }
}

function openCrmWithOpportunity(opp) {
  document.getElementById('crm-filter-opportunity').value = opp;
  switchTab('tab-crm');
  loadLeads();
}

// ==================== STATS & CHARTS ====================
async function loadStats() {
  try {
    const res = await apiFetch('/api/stats');
    const st = await res.json();
    STATE.stats = st;
    document.getElementById('kpi-total').textContent = st.total || 0;
    document.getElementById('kpi-no-site').textContent = st.no_website || 0;
    document.getElementById('kpi-low-reviews').textContent = st.low_reviews || 0;
    document.getElementById('kpi-contacted').textContent = st.contacted || 0;
    document.getElementById('kpi-replied').textContent = st.replied || 0;
    document.getElementById('kpi-sales').textContent = formatBRL(st.sales_revenue || 0);
    document.getElementById('badge-crm-novo').textContent = (st.crm_status?.novo || 0);
    renderCharts(st);
  } catch (e) {}
}

function renderCharts(st) {
  if (typeof Chart === 'undefined') return;
  const isDark = document.body.classList.contains('dark-theme');
  const tickColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.06)';

  const opps = st.opportunities || {};
  const ctx1 = document.getElementById('chart-opportunities');
  if (ctx1) {
    if (STATE.charts.opps) STATE.charts.opps.destroy();
    STATE.charts.opps = new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: ['Plaquinha NFC + QR', 'WhatsApp Business', 'Biossite / LP', 'Cardápio Digital'],
        datasets: [{
          label: 'Empresas com Oportunidade',
          data: [opps.nfc_google || 0, opps.whatsapp_biz || 0, opps.biossite || 0, opps.cardapio_digital || 0],
          backgroundColor: ['#7c3aed', '#10b981', '#2563eb', '#f59e0b'],
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: tickColor }, grid: { color: gridColor } },
          y: { ticks: { color: tickColor }, grid: { color: gridColor } }
        }
      }
    });
  }

  const cs = st.crm_status || {};
  const ctx2 = document.getElementById('chart-funnel');
  if (ctx2) {
    if (STATE.charts.funnel) STATE.charts.funnel.destroy();
    STATE.charts.funnel = new Chart(ctx2, {
      type: 'doughnut',
      data: {
        labels: ['Novos', 'Contatados', 'Responderam', 'Proposta', 'Fechados'],
        datasets: [{
          data: [cs.novo || 0, cs.contatado || 0, cs.respondeu || 0, cs.negociacao || 0, cs.fechado || 0],
          backgroundColor: ['#94a3b8', '#2563eb', '#f59e0b', '#7c3aed', '#10b981'],
          borderColor: isDark ? '#111827' : '#ffffff',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: tickColor } } }
      }
    });
  }
}

// ==================== SEARCH ====================
function initSearchControls() {
  const locInput = document.getElementById('search-location-input');
  const sugBox = document.getElementById('location-suggestions');
  let acTimer = null;

  locInput?.addEventListener('input', () => {
    clearTimeout(acTimer);
    const q = locInput.value.trim();
    if (q.length < 3) { sugBox.classList.add('hidden'); return; }
    acTimer = setTimeout(async () => {
      try {
        const res = await apiFetch(`/api/address/suggest?q=${encodeURIComponent(q)}`);
        const items = await res.json();
        if (!items.length) { sugBox.classList.add('hidden'); return; }
        sugBox.innerHTML = items.map((it, idx) => `
          <div class="ac-item" data-idx="${idx}">
            <i class="fa-solid ${escapeHtml(it.type_icon || 'fa-location-dot')}"></i>
            <div>
              <strong>${escapeHtml(it.display_title)}</strong>
              <small>${escapeHtml(it.display_subtitle)}</small>
            </div>
          </div>
        `).join('');
        sugBox.classList.remove('hidden');
        sugBox.querySelectorAll('.ac-item').forEach(el => {
          el.addEventListener('click', () => {
            const picked = items[Number(el.dataset.idx)];
            STATE.selectedLocation = picked;
            locInput.value = picked.full_label;
            sugBox.classList.add('hidden');
            const badge = document.getElementById('selected-location-badge');
            badge.innerHTML = `<i class="fa-solid fa-check-circle"></i> ${escapeHtml(picked.type_label)}: ${escapeHtml(picked.full_label)}`;
            badge.classList.remove('hidden');
          });
        });
      } catch (e) {}
    }, 320);
  });

  document.addEventListener('click', (e) => {
    if (!sugBox?.contains(e.target) && e.target !== locInput) sugBox?.classList.add('hidden');
  });

  const modeSel = document.getElementById('search-mode');
  modeSel?.addEventListener('change', () => {
    const m = modeSel.value;
    document.getElementById('multi-segments-box').classList.toggle('hidden', m !== 'multi');
    document.getElementById('wrap-niche').classList.toggle('hidden', m !== 'single');
  });
  document.getElementById('wrap-niche')?.classList.add('hidden');

  document.getElementById('btn-start-search')?.addEventListener('click', startSearch);
  document.getElementById('btn-stop-search')?.addEventListener('click', async () => {
    await apiFetch('/api/search/stop', { method: 'POST' });
    setSearchRunning(false);
    toast('Parada solicitada.', 'info');
  });
}

async function loadSegments() {
  try {
    const res = await apiFetch('/api/segments/presets');
    STATE.segments = await res.json();
    const box = document.getElementById('segments-chips');
    if (box) {
      box.innerHTML = STATE.segments.map(s => `<button type="button" class="seg-chip" data-id="${escapeHtml(s.id)}">${escapeHtml(s.name)}</button>`).join('');
      box.querySelectorAll('.seg-chip').forEach(ch => ch.addEventListener('click', () => ch.classList.toggle('selected')));
    }
  } catch (e) {}
}

async function loadSearchHistory() {
  try {
    const res = await apiFetch('/api/search/history');
    const rows = await res.json();
    const tb = document.getElementById('search-history-tbody');
    if (!tb) return;
    if (!rows.length) {
      tb.innerHTML = '<tr><td colspan="5" class="text-muted">Nenhuma busca realizada ainda.</td></tr>';
      return;
    }
    tb.innerHTML = rows.map(r => `
      <tr>
        <td><strong>${escapeHtml(r.niche || r.query)}</strong></td>
        <td>${escapeHtml(r.location || '-')}</td>
        <td>${r.total_found || 0}</td>
        <td>${r.no_website_count || 0}</td>
        <td>${escapeHtml((r.created_at || '').slice(0, 16).replace('T', ' '))}</td>
      </tr>
    `).join('');
  } catch (e) {}
}

async function startSearch() {
  const locText = document.getElementById('search-location-input').value.trim();
  const mode = document.getElementById('search-mode').value;
  const niche = document.getElementById('search-niche').value.trim();
  const limit = Number(document.getElementById('search-limit').value || 50);
  const visible = document.getElementById('chk-visible-browser').checked;
  const selLoc = STATE.selectedLocation;

  if (!locText && !niche) {
    toast('Informe uma cidade, bairro ou rua para buscar.', 'error');
    return;
  }

  const segments = Array.from(document.querySelectorAll('.seg-chip.selected')).map(el => el.dataset.id);
  const payload = {
    mode,
    niche,
    segments,
    target_limit: limit,
    visible_browser: visible,
    street: selLoc?.street || '',
    neighborhood: selLoc?.neighborhood || '',
    city: selLoc?.city || locText,
    lat: selLoc?.lat || null,
    lon: selLoc?.lon || null,
    place_type: selLoc?.place_type || 'city',
    zoom: selLoc?.recommended_zoom || null,
  };

  document.getElementById('live-log-box').innerHTML = '';
  document.getElementById('live-leads-list').innerHTML = '';
  document.getElementById('search-progress-bar').style.width = '5%';

  try {
    const res = await apiFetch('/api/search/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!data.success) {
      toast(data.error || 'Erro ao iniciar busca.', 'error');
      return;
    }
    setSearchRunning(true);
    toast('Busca iniciada no Google!', 'success');
  } catch (e) {
    toast('Erro ao iniciar busca.', 'error');
  }
}

function setSearchRunning(running) {
  document.getElementById('btn-start-search')?.classList.toggle('hidden', running);
  document.getElementById('btn-stop-search')?.classList.toggle('hidden', !running);
  document.getElementById('topbar-live-pill')?.classList.toggle('hidden', !running);
  document.getElementById('nav-search-dot')?.classList.toggle('hidden', !running);
}

function initSSE() {
  if (STATE.sse) STATE.sse.close();
  const es = new EventSource('/api/search/stream');
  STATE.sse = es;

  es.addEventListener('init', (e) => {
    const d = JSON.parse(e.data || '{}');
    setSearchRunning(Boolean(d.is_running));
  });

  es.addEventListener('search_started', (e) => {
    const d = JSON.parse(e.data || '{}');
    setSearchRunning(true);
    document.getElementById('search-status-text').textContent = `Buscando: ${d.query || ''}`;
    document.getElementById('topbar-live-text').textContent = `Buscando (${d.location || ''})...`;
  });

  es.addEventListener('log', (e) => {
    const d = JSON.parse(e.data || '{}');
    const box = document.getElementById('live-log-box');
    if (box) {
      const line = document.createElement('div');
      line.textContent = `[${d.time || ''}] ${d.message || ''}`;
      box.appendChild(line);
      box.scrollTop = box.scrollHeight;
    }
  });

  es.addEventListener('progress', (e) => {
    const d = JSON.parse(e.data || '{}');
    document.getElementById('live-found-count').textContent = `${d.total_extracted || 0} encontrados`;
    if (d.target_limit) {
      const pct = Math.min(100, Math.round(((d.total_extracted || 0) / d.target_limit) * 100));
      document.getElementById('search-progress-bar').style.width = `${pct}%`;
    }
  });

  es.addEventListener('lead_found', (e) => {
    const lead = JSON.parse(e.data || '{}');
    const list = document.getElementById('live-leads-list');
    if (list) {
      const row = document.createElement('div');
      row.className = 'live-lead-row';
      row.innerHTML = `
        <div>
          <strong>${escapeHtml(lead.name)}</strong>
          <div class="text-muted" style="font-size:0.75rem">${escapeHtml(lead.category || '')} · ${escapeHtml(lead.phone || '')}</div>
        </div>
        <span class="opp-badge opp-bio">${lead.website_type === 'none' ? 'Sem Site' : lead.website_type === 'social' ? 'Rede Social' : 'Com Site'}</span>
      `;
      row.addEventListener('click', () => openLeadDrawerById(lead.id));
      list.prepend(row);
    }
  });

  es.addEventListener('search_completed', (e) => {
    const d = JSON.parse(e.data || '{}');
    document.getElementById('search-progress-bar').style.width = '100%';
    document.getElementById('search-status-text').textContent = d.message || 'Busca concluída!';
    toast(d.message || 'Busca concluída!', 'success');
    loadAllData();
  });

  es.addEventListener('search_finished', () => setSearchRunning(false));
  es.addEventListener('lead_updated', () => { loadStats(); loadLeads(); loadChatThreads(); });
  es.addEventListener('lead_reply', (e) => {
    const d = JSON.parse(e.data || '{}');
    toast(`Nova resposta de ${d.name || 'um cliente'}!`, 'success');
    loadStats();
    loadLeads();
    loadChatThreads();
  });
  es.addEventListener('chat_message', (e) => {
    const d = JSON.parse(e.data || '{}');
    loadChatThreads();
    if (STATE.activeChatLead?.id === d.lead_id) {
      renderActiveChatMessages(d.lead_id);
    }
  });
}

// ==================== MAPA ====================
function initMap() {
  if (STATE.map) return;
  const map = L.map('leaflet-map').setView([-19.9167, -43.9345], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map);
  STATE.map = map;
  STATE.mapCluster = L.markerClusterGroup();
  map.addLayer(STATE.mapCluster);

  map.on('click', async (ev) => {
    const { lat, lng } = ev.latlng;
    if (STATE.pinMarker) STATE.map.removeLayer(STATE.pinMarker);
    STATE.pinMarker = L.marker([lat, lng]).addTo(STATE.map);
    try {
      const res = await apiFetch(`/api/address/reverse?lat=${lat}&lon=${lng}`);
      const d = await res.json();
      if (d.success) {
        STATE.pinReverse = d;
        STATE.pinMarker.bindPopup(`<strong>${escapeHtml(d.display_title)}</strong><br>${escapeHtml(d.display_subtitle)}`).openPopup();
        document.getElementById('btn-map-search-pin').classList.remove('hidden');
      }
    } catch (e) {}
  });

  document.getElementById('btn-map-search-pin')?.addEventListener('click', () => {
    if (!STATE.pinReverse) return;
    STATE.selectedLocation = STATE.pinReverse;
    document.getElementById('search-location-input').value = STATE.pinReverse.full_label;
    switchTab('tab-search');
    startSearch();
  });

  document.getElementById('btn-map-center')?.addEventListener('click', () => {
    if (STATE.mapCluster && STATE.mapCluster.getLayers().length) {
      STATE.map.fitBounds(STATE.mapCluster.getBounds(), { padding: [30, 30] });
    }
  });
}

function renderMapMarkers() {
  if (!STATE.mapCluster) return;
  STATE.mapCluster.clearLayers();
  STATE.leads.forEach(l => {
    if (l.lat && l.lon) {
      const m = L.marker([Number(l.lat), Number(l.lon)]);
      m.bindPopup(`<strong>${escapeHtml(l.name)}</strong><br>${escapeHtml(l.category || '')}<br>${escapeHtml(l.phone || '')}`);
      m.on('dblclick', () => openLeadDrawer(l));
      STATE.mapCluster.addLayer(m);
    }
  });
}

// ==================== CRM & KANBAN ====================
function initCrmControls() {
  document.getElementById('crm-search-input')?.addEventListener('input', debounce(loadLeads, 280));
  document.getElementById('crm-filter-opportunity')?.addEventListener('change', loadLeads);
  document.getElementById('crm-filter-website')?.addEventListener('change', loadLeads);

  document.getElementById('btn-dedup-leads')?.addEventListener('click', async () => {
    const res = await apiFetch('/api/leads/deduplicate', { method: 'POST' });
    const d = await res.json();
    toast(`${d.duplicates_removed || 0} leads duplicados removidos.`, 'success');
    loadAllData();
  });

  // Drag and drop nas colunas Kanban
  document.querySelectorAll('.kanban-list').forEach(col => {
    if (typeof Sortable === 'undefined') return;
    Sortable.create(col, {
      group: 'crm-kanban',
      animation: 150,
      onEnd: async (evt) => {
        const leadId = Number(evt.item.dataset.id);
        const newStatus = evt.to.closest('.kanban-col').dataset.status;
        if (!leadId || !newStatus) return;
        await apiFetch(`/api/leads/${leadId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ crm_status: newStatus })
        });
        loadStats();
        updateColumnCounts();
      }
    });
  });
}

function setCrmView(view) {
  STATE.crmView = view;
  document.getElementById('btn-view-kanban').classList.toggle('active', view === 'kanban');
  document.getElementById('btn-view-table').classList.toggle('active', view === 'table');
  document.getElementById('crm-kanban-view').classList.toggle('hidden', view !== 'kanban');
  document.getElementById('crm-table-view').classList.toggle('hidden', view !== 'table');
}

async function loadLeads() {
  const search = document.getElementById('crm-search-input')?.value || '';
  const opp = document.getElementById('crm-filter-opportunity')?.value || 'all';
  const wt = document.getElementById('crm-filter-website')?.value || 'all';
  const qs = new URLSearchParams({ search, opportunity: opp, website_type: wt, limit: 1000 });
  try {
    const res = await apiFetch(`/api/leads?${qs.toString()}`);
    STATE.leads = await res.json();
    renderKanban();
    renderTable();
  } catch (e) {}
}

function renderOpportunityBadges(opps = []) {
  return (opps || []).slice(0, 3).map(k => {
    const info = OPP_LABELS[k];
    if (!info) return '';
    return `<span class="opp-badge ${info.cls}"><i class="fa-solid ${info.icon}"></i> ${info.label}</span>`;
  }).join('');
}

function renderKanban() {
  const cols = { novo: [], contatado: [], respondeu: [], negociacao: [], fechado: [] };
  STATE.leads.forEach(l => {
    const st = cols[l.crm_status] ? l.crm_status : 'novo';
    cols[st].push(l);
  });

  Object.entries(cols).forEach(([status, items]) => {
    const container = document.getElementById(`col-${status}`);
    if (!container) return;
    container.innerHTML = items.map(l => `
      <div class="lead-card" data-id="${l.id}">
        <div class="lead-card-title">${escapeHtml(l.name)}</div>
        <div class="lead-card-sub">${escapeHtml(l.category || 'Negócio local')} · ${escapeHtml(l.neighborhood || l.city || '')}</div>
        <div class="lead-card-badges">${renderOpportunityBadges(l.opportunities)}</div>
        <div class="lead-card-foot">
          <span><i class="fa-solid fa-star" style="color:#f59e0b"></i> ${l.rating || '-'} (${l.reviews_count || 0})</span>
          <span>${l.sale_value ? formatBRL(l.sale_value) : escapeHtml(l.phone || '')}</span>
        </div>
      </div>
    `).join('');
    container.querySelectorAll('.lead-card').forEach(card => {
      card.addEventListener('click', () => openLeadDrawerById(Number(card.dataset.id)));
    });
  });
  updateColumnCounts();
}

function updateColumnCounts() {
  ['novo', 'contatado', 'respondeu', 'negociacao', 'fechado'].forEach(st => {
    const c = document.getElementById(`col-${st}`);
    const cnt = document.getElementById(`cnt-${st}`);
    if (c && cnt) cnt.textContent = c.children.length;
  });
}

function renderTable() {
  const tb = document.getElementById('crm-table-tbody');
  if (!tb) return;
  if (!STATE.leads.length) {
    tb.innerHTML = '<tr><td colspan="6" class="text-muted">Nenhum lead encontrado com os filtros atuais.</td></tr>';
    return;
  }
  tb.innerHTML = STATE.leads.map(l => `
    <tr>
      <td><strong>${escapeHtml(l.name)}</strong><div class="text-muted" style="font-size:0.75rem">${escapeHtml(l.category || '')} · ${escapeHtml(l.neighborhood || l.city || '')}</div></td>
      <td>${escapeHtml(l.phone || '-')}</td>
      <td><div style="display:flex;gap:4px;flex-wrap:wrap">${renderOpportunityBadges(l.opportunities)}</div></td>
      <td>${l.rating || '-'} ⭐ (${l.reviews_count || 0})</td>
      <td><span class="status-pill">${escapeHtml(l.crm_status)}</span></td>
      <td><button class="btn btn-outline btn-xs" onclick="openLeadDrawerById(${l.id})">Abrir</button></td>
    </tr>
  `).join('');
}

// ==================== LEAD DRAWER ====================
function initDrawerControls() {
  document.getElementById('drawer-template-select')?.addEventListener('change', fillDrawerTemplate);
  document.getElementById('btn-drawer-copy')?.addEventListener('click', () => {
    const txt = document.getElementById('drawer-message-text').value;
    navigator.clipboard.writeText(txt);
    toast('Mensagem copiada!', 'success');
  });

  document.getElementById('btn-drawer-wa-web')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l || !l.clean_phone) { toast('Lead sem telefone válido.', 'error'); return; }
    const text = document.getElementById('drawer-message-text').value.trim();
    const url = `https://wa.me/${l.clean_phone}?text=${encodeURIComponent(text)}`;
    window.open(url, '_blank');
    await apiFetch(`/api/leads/${l.id}/toggle-contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ crm_status: 'contatado', text, phone: l.clean_phone })
    });
    toast('WhatsApp Web aberto e lead marcado como Contatado!', 'success');
    loadAllData();
    loadLeadConversation(l.id);
  });

  document.getElementById('btn-drawer-wa-baileys')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l) return;
    const text = document.getElementById('drawer-message-text').value.trim();
    const res = await apiFetch('/api/wa/send-one', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_id: l.id, text, force: true })
    });
    const d = await res.json();
    if (d.success) {
      toast('Mensagem enviada pelo WhatsApp QR!', 'success');
      loadAllData();
      loadLeadConversation(l.id);
    } else {
      toast(d.error || 'WhatsApp QR não conectado. Conecte em WhatsApp & Conta.', 'error');
    }
  });

  document.getElementById('btn-drawer-wa-official')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l) return;
    const text = document.getElementById('drawer-message-text').value.trim();
    const res = await apiFetch('/api/wa/official/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_id: l.id, send_type: 'text', text })
    });
    const d = await res.json();
    if (d.success) {
      toast('Mensagem enviada pela API Oficial da Meta!', 'success');
      loadAllData();
      loadLeadConversation(l.id);
    } else {
      toast(d.error || 'Erro ao enviar pela API Oficial. Verifique Configurações.', 'error');
    }
  });

  document.getElementById('btn-drawer-save-sale')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l) return;
    const val = Number(document.getElementById('drawer-sale-value').value || 0);
    const prod = document.getElementById('drawer-product-interest').value;
    await apiFetch(`/api/leads/${l.id}/record-sale`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sale_value: val, product_interest: prod })
    });
    toast('Venda registrada no faturamento!', 'success');
    loadAllData();
    closeLeadDrawer();
  });

  document.getElementById('btn-drawer-save-notes')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l) return;
    await apiFetch(`/api/leads/${l.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crm_status: document.getElementById('drawer-crm-status').value,
        product_interest: document.getElementById('drawer-product-interest').value,
        notes: document.getElementById('drawer-notes').value,
      })
    });
    toast('Alterações salvas!', 'success');
    loadAllData();
  });

  document.getElementById('btn-drawer-delete')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l || !confirm(`Excluir "${l.name}"?`)) return;
    await apiFetch(`/api/leads/${l.id}`, { method: 'DELETE' });
    toast('Lead excluído.', 'info');
    closeLeadDrawer();
    loadAllData();
  });
}

function openLeadDrawerById(id) {
  const l = STATE.leads.find(x => x.id === id);
  if (l) openLeadDrawer(l);
}

function openLeadDrawer(l) {
  STATE.selectedLead = l;
  document.getElementById('drawer-lead-name').textContent = l.name;
  document.getElementById('drawer-lead-cat').textContent = `${l.category || 'Empresa'} · ${l.neighborhood || l.city || ''}`;
  document.getElementById('drawer-opps').innerHTML = renderOpportunityBadges(l.opportunities);
  document.getElementById('drawer-phone').textContent = l.phone || '-';
  document.getElementById('drawer-rating').textContent = `${l.rating || '-'} ⭐ (${l.reviews_count || 0} avaliações)`;
  document.getElementById('drawer-address').textContent = l.address || '-';
  document.getElementById('drawer-website').innerHTML = l.website
    ? `<a href="${escapeHtml(l.website)}" target="_blank">${escapeHtml(l.website)}</a>`
    : '<span class="text-muted">Sem site oficial</span>';

  document.getElementById('drawer-crm-status').value = l.crm_status || 'novo';
  document.getElementById('drawer-product-interest').value = l.product_interest || '';
  document.getElementById('drawer-sale-value').value = l.sale_value || '';
  document.getElementById('drawer-notes').value = l.notes || '';

  const sel = document.getElementById('drawer-template-select');
  sel.innerHTML = STATE.templates.map(t => `<option value="${escapeHtml(t.id)}">${escapeHtml(t.title)}</option>`).join('');
  fillDrawerTemplate();
  loadLeadConversation(l.id);

  document.getElementById('drawer-backdrop').classList.remove('hidden');
  document.getElementById('lead-drawer').classList.remove('hidden');
}

function closeLeadDrawer() {
  document.getElementById('drawer-backdrop').classList.add('hidden');
  document.getElementById('lead-drawer').classList.add('hidden');
}

function fillTemplateText(raw, l) {
  return (raw || '')
    .replace(/\{nome\}/g, l?.name || 'sua empresa')
    .replace(/\{categoria\}/g, l?.category || 'seu segmento')
    .replace(/\{bairro\}/g, l?.neighborhood || l?.city || 'sua região')
    .replace(/\{rua\}/g, l?.street || '')
    .replace(/\{avaliacao\}/g, l?.rating || '5.0')
    .replace(/\{avaliacoes\}/g, l?.reviews_count || '0');
}

function fillDrawerTemplate(useFollowUp = false) {
  const l = STATE.selectedLead;
  const tid = document.getElementById('drawer-template-select').value;
  const tpl = STATE.templates.find(t => t.id === tid);
  if (!tpl || !l) return;
  const raw = (useFollowUp === true) ? (tpl.follow_up || tpl.content || '') : (tpl.content || '');
  document.getElementById('drawer-message-text').value = fillTemplateText(raw, l);
}

async function loadLeadConversation(leadId) {
  try {
    const res = await apiFetch(`/api/leads/${leadId}/conversation`);
    const msgs = await res.json();
    const box = document.getElementById('drawer-conversation');
    if (!msgs.length) {
      box.innerHTML = '<div class="text-muted" style="font-size:0.8rem">Nenhuma mensagem registrada ainda.</div>';
      return;
    }
    box.innerHTML = msgs.map(m => `
      <div class="conv-msg ${m.direction === 'out' ? 'out' : 'in'}">
        <div>${escapeHtml(m.text)}</div>
        <small class="text-muted">${escapeHtml((m.created_at || '').slice(0, 16).replace('T', ' '))} · ${escapeHtml(m.status || '')}</small>
      </div>
    `).join('');
  } catch (e) {}
}

// ==================== TEMPLATES ====================
function initTemplateControls() {
  document.getElementById('btn-drawer-icebreaker')?.addEventListener('click', () => {
    const sel = document.getElementById('drawer-template-select');
    const ice = STATE.templates.find(t => t.id === 'quebra_gelo_antibloqueio') || STATE.templates[0];
    if (ice) {
      sel.value = ice.id;
      fillDrawerTemplate(false);
    }
  });

  document.getElementById('btn-drawer-followup')?.addEventListener('click', () => {
    fillDrawerTemplate(true);
  });

  document.getElementById('btn-reset-templates')?.addEventListener('click', async () => {
    if (!confirm('Restaurar os modelos curtos padrão (incluindo o Quebra-Gelo Anti-Bloqueio)?')) return;
    const res = await apiFetch('/api/pitch-templates/reset', { method: 'POST' });
    const d = await res.json();
    if (d.success) {
      toast('Modelos curtos restaurados!', 'success');
      loadTemplates();
    }
  });

  document.getElementById('btn-new-template')?.addEventListener('click', () => {
    document.getElementById('tpl-id').value = '';
    document.getElementById('tpl-title').value = '';
    document.getElementById('tpl-product').value = 'nfc';
    document.getElementById('tpl-meta-name').value = '';
    document.getElementById('tpl-content').value = '';
    document.getElementById('tpl-follow-up').value = '';
    document.getElementById('tpl-editor-heading').textContent = 'Criar Novo Modelo';
    document.getElementById('btn-delete-template').classList.add('hidden');
  });

  document.getElementById('form-template-editor')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      id: document.getElementById('tpl-id').value || undefined,
      title: document.getElementById('tpl-title').value,
      product: document.getElementById('tpl-product').value,
      meta_template_name: document.getElementById('tpl-meta-name').value,
      content: document.getElementById('tpl-content').value,
      follow_up: document.getElementById('tpl-follow-up').value,
    };
    const res = await apiFetch('/api/pitch-templates', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await res.json();
    if (d.success) {
      toast('Modelo salvo!', 'success');
      loadTemplates();
    }
  });

  document.getElementById('btn-delete-template')?.addEventListener('click', async () => {
    const id = document.getElementById('tpl-id').value;
    if (!id || !confirm('Excluir este modelo?')) return;
    await apiFetch(`/api/pitch-templates/${encodeURIComponent(id)}`, { method: 'DELETE' });
    toast('Modelo excluído.', 'info');
    loadTemplates();
  });
}

async function loadTemplates() {
  try {
    const res = await apiFetch('/api/pitch-templates');
    STATE.templates = await res.json();
    const list = document.getElementById('templates-list');
    if (!list) return;
    list.innerHTML = STATE.templates.map(t => `
      <div class="tpl-item" data-id="${escapeHtml(t.id)}">
        <strong>${escapeHtml(t.title)}</strong>
        <small>Oferta: ${escapeHtml(t.product || 'geral')}</small>
      </div>
    `).join('');
    list.querySelectorAll('.tpl-item').forEach(el => {
      el.addEventListener('click', () => {
        const t = STATE.templates.find(x => x.id === el.dataset.id);
        if (!t) return;
        list.querySelectorAll('.tpl-item').forEach(x => x.classList.remove('active'));
        el.classList.add('active');
        document.getElementById('tpl-id').value = t.id;
        document.getElementById('tpl-title').value = t.title;
        document.getElementById('tpl-product').value = t.product || 'geral';
        document.getElementById('tpl-meta-name').value = t.meta_template_name || '';
        document.getElementById('tpl-content').value = t.content || '';
        document.getElementById('tpl-follow-up').value = t.follow_up || '';
        document.getElementById('tpl-editor-heading').textContent = 'Editar Modelo';
        document.getElementById('btn-delete-template').classList.remove('hidden');
      });
    });
    if (STATE.templates.length) list.querySelector('.tpl-item')?.click();
  } catch (e) {}
}

// ==================== SETTINGS & OFFICIAL WHATSAPP ====================
function setSettingsSubtab(name) {
  document.querySelectorAll('.settings-tabs .seg-btn').forEach((b, idx) => {
    const map = ['official', 'baileys', 'account'];
    b.classList.toggle('active', map[idx] === name);
  });
  document.getElementById('pane-official').classList.toggle('hidden', name !== 'official');
  document.getElementById('pane-baileys').classList.toggle('hidden', name !== 'baileys');
  document.getElementById('pane-account').classList.toggle('hidden', name !== 'account');
  if (name === 'baileys') {
    startBaileysPolling();
  } else {
    stopBaileysPolling();
  }
}

function copyWebhookUrl() {
  const url = document.getElementById('meta-webhook-url').textContent;
  navigator.clipboard.writeText(url);
  toast('Webhook URL copiada!', 'success');
}

function initSettingsControls() {
  const whEl = document.getElementById('meta-webhook-url');
  if (whEl) whEl.textContent = `${window.location.origin}/api/wa/official/webhook`;

  loadOfficialConfig();
  initMetaEmbeddedSignup();

  document.getElementById('form-meta-config')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      mode: document.getElementById('meta-mode').value,
      meta_api_version: document.getElementById('meta-api-version').value,
      meta_phone_number_id: document.getElementById('meta-phone-number-id').value,
      meta_waba_id: document.getElementById('meta-waba-id').value,
      meta_access_token: document.getElementById('meta-access-token').value,
      meta_verify_token: document.getElementById('meta-verify-token').value,
      default_template_name: document.getElementById('meta-default-template').value,
    };
    const res = await apiFetch('/api/wa/official/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await res.json();
    if (d.success) toast('Configurações da API Oficial salvas!', 'success');
  });

  document.getElementById('btn-test-meta')?.addEventListener('click', async () => {
    const badge = document.getElementById('meta-conn-badge');
    badge.textContent = 'Testando...';
    const res = await apiFetch('/api/wa/official/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        meta_phone_number_id: document.getElementById('meta-phone-number-id').value,
        meta_access_token: document.getElementById('meta-access-token').value,
        meta_api_version: document.getElementById('meta-api-version').value,
      })
    });
    const d = await res.json();
    if (d.success) {
      badge.className = 'status-pill ok';
      badge.textContent = `Conectado: ${d.verified_name || d.display_phone_number}`;
      toast(`Conectado com sucesso: ${d.display_phone_number}`, 'success');
    } else {
      badge.className = 'status-pill err';
      badge.textContent = 'Erro na conexão';
      toast(d.error || 'Falha ao conectar com a Meta.', 'error');
    }
  });

  document.getElementById('btn-sync-meta-templates')?.addEventListener('click', async () => {
    const box = document.getElementById('meta-templates-result');
    const res = await apiFetch('/api/wa/official/templates');
    const d = await res.json();
    if (d.success) {
      box.classList.remove('hidden');
      box.innerHTML = `<div class="info-banner"><div><strong>Templates encontrados (${d.templates.length}):</strong><br>${d.templates.map(t => `<code>${escapeHtml(t.name)}</code> (${escapeHtml(t.status)})`).join(' · ') || 'Nenhum template encontrado.'}</div></div>`;
    } else {
      toast(d.error || 'Erro ao buscar templates.', 'error');
    }
  });

  document.getElementById('btn-baileys-connect')?.addEventListener('click', async () => {
    const badge = document.getElementById('baileys-status-badge');
    badge.textContent = 'Gerando QR...';
    const res = await apiFetch('/api/wa/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ force: true })
    });
    const d = await res.json();
    if (d.offline || d.error) {
      toast(d.error || 'Serviço WhatsApp QR iniciando, aguarde...', 'info');
    }
    startBaileysPolling();
  });

  document.getElementById('btn-baileys-logout')?.addEventListener('click', async () => {
    stopBaileysPolling();
    await apiFetch('/api/wa/logout', { method: 'POST' });
    pollBaileysStatus();
  });

  document.getElementById('form-my-account')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const res = await apiFetch('/api/me', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: document.getElementById('acc-name').value,
        company_name: document.getElementById('acc-company').value,
        password: document.getElementById('acc-password').value || undefined,
      })
    });
    const d = await res.json();
    if (d.success) {
      document.getElementById('sidebar-user-name').textContent = d.user.name;
      document.getElementById('acc-password').value = '';
      toast('Dados atualizados!', 'success');
    } else {
      toast(d.error || 'Erro ao atualizar.', 'error');
    }
  });
}

async function loadOfficialConfig() {
  try {
    const res = await apiFetch('/api/wa/official/config');
    const c = await res.json();
    document.getElementById('meta-mode').value = c.mode || 'web_1click';
    document.getElementById('meta-api-version').value = c.meta_api_version || 'v21.0';
    document.getElementById('meta-phone-number-id').value = c.meta_phone_number_id || '';
    document.getElementById('meta-waba-id').value = c.meta_waba_id || '';
    document.getElementById('meta-access-token').value = c.meta_access_token || '';
    document.getElementById('meta-verify-token').value = c.meta_verify_token || 'mapaleads_webhook_2026';
    document.getElementById('meta-default-template').value = c.default_template_name || '';
  } catch (e) {}
}

let _embeddedCfg = null;
let _embeddedSignupSession = { phone_number_id: '', waba_id: '' };

async function initMetaEmbeddedSignup() {
  const btn = document.getElementById('btn-meta-embedded-signup');
  const txt = document.getElementById('meta-embedded-status-text');
  if (!btn) return;

  try {
    const res = await apiFetch('/api/wa/official/embedded-config');
    _embeddedCfg = await res.json();
  } catch (e) {
    _embeddedCfg = { enabled: false };
  }

  if (!_embeddedCfg?.enabled) {
    if (txt) {
      txt.textContent = 'Ativo automaticamente após publicar em HTTPS e configurar o App da Meta (META_APP_ID e META_EMBEDDED_CONFIG_ID). Enquanto isso, use a Configuração Manual abaixo ou o WhatsApp Web 1-Clique.';
    }
    btn.addEventListener('click', () => {
      toast('Para usar o botão automático 1-clique da Meta (igual ao Kommo), publique em HTTPS e configure META_APP_ID + META_EMBEDDED_CONFIG_ID no servidor.', 'info');
    });
    return;
  }

  window.addEventListener('message', (event) => {
    if (event.origin !== 'https://www.facebook.com' && event.origin !== 'https://web.facebook.com') return;
    try {
      const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
      if (data?.type === 'WA_EMBEDDED_SIGNUP' && data?.event === 'FINISH') {
        _embeddedSignupSession.phone_number_id = data.data?.phone_number_id || '';
        _embeddedSignupSession.waba_id = data.data?.waba_id || '';
      }
    } catch (e) {}
  });

  if (!window.FB) {
    window.fbAsyncInit = function () {
      window.FB.init({
        appId: _embeddedCfg.app_id,
        autoLogAppEvents: true,
        xfbml: true,
        version: _embeddedCfg.api_version || 'v21.0',
      });
    };
    const js = document.createElement('script');
    js.src = 'https://connect.facebook.net/pt_BR/sdk.js';
    js.async = true;
    js.defer = true;
    document.head.appendChild(js);
  }

  btn.addEventListener('click', () => {
    if (!window.FB) {
      toast('SDK da Meta ainda carregando, tente novamente em 2 segundos.', 'info');
      return;
    }
    _embeddedSignupSession = { phone_number_id: '', waba_id: '' };
    window.FB.login((response) => {
      const code = response?.authResponse?.code;
      if (!code) {
        toast('Conexão com a Meta cancelada.', 'info');
        return;
      }
      apiFetch('/api/wa/official/embedded-callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          phone_number_id: _embeddedSignupSession.phone_number_id,
          waba_id: _embeddedSignupSession.waba_id,
        }),
      })
        .then((r) => r.json())
        .then((d) => {
          if (d.success) {
            toast('WhatsApp Oficial conectado automaticamente!', 'success');
            loadOfficialConfig();
          } else {
            toast(d.error || 'Erro ao finalizar conexão com a Meta.', 'error');
          }
        })
        .catch(() => toast('Erro ao comunicar com o servidor.', 'error'));
    }, {
      config_id: _embeddedCfg.config_id,
      response_type: 'code',
      override_default_response_type: true,
      extras: { setup: {}, featureType: '' },
    });
  });
}

function startBaileysPolling() {
  stopBaileysPolling();
  pollBaileysStatus();
  STATE.baileysPoll = setInterval(pollBaileysStatus, 2000);
}

function stopBaileysPolling() {
  if (STATE.baileysPoll) {
    clearInterval(STATE.baileysPoll);
    STATE.baileysPoll = null;
  }
}

async function pollBaileysStatus() {
  try {
    const res = await apiFetch('/api/wa/status');
    const st = await res.json();
    const badge = document.getElementById('baileys-status-badge');
    const qrWrap = document.getElementById('baileys-qr-wrap');
    const qrImg = document.getElementById('baileys-qr-img');
    const userInfo = document.getElementById('baileys-user-info');
    if (!badge) return;

    const labels = {
      connected: 'Conectado',
      qrcode: 'Escaneie o QR Code',
      connecting: 'Gerando QR Code...',
      disconnected: 'Desconectado',
      offline: 'Offline'
    };
    badge.textContent = labels[st.state] || st.state || 'offline';
    badge.className = `status-pill ${st.state === 'connected' ? 'ok' : st.state === 'offline' ? 'err' : ''}`;

    if (st.state === 'connected' && st.user) {
      userInfo.innerHTML = `<i class="fa-brands fa-whatsapp"></i> <strong>Conectado como:</strong> ${escapeHtml(st.user.name || 'WhatsApp')} (${escapeHtml(st.user.phone || '')})`;
      userInfo.classList.remove('hidden');
      qrWrap.classList.add('hidden');
      stopBaileysPolling();
    } else {
      userInfo.classList.add('hidden');
      if (st.qr) {
        qrImg.src = st.qr;
        qrWrap.classList.remove('hidden');
      } else {
        qrWrap.classList.add('hidden');
      }
      if (st.state === 'disconnected' || st.state === 'offline') {
        stopBaileysPolling();
      }
    }
  } catch (e) {}
}

// ==================== CHAT / CONVERSAS (KOMMO) ====================
function initChatControls() {
  document.getElementById('chat-search-input')?.addEventListener('input', debounce(loadChatThreads, 250));
  document.querySelectorAll('[data-chat-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-chat-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      STATE.chatFilter = btn.dataset.chatFilter;
      loadChatThreads();
    });
  });

  document.getElementById('chat-template-select')?.addEventListener('change', (e) => {
    const tid = e.target.value;
    const l = STATE.activeChatLead;
    const tpl = STATE.templates.find(t => t.id === tid);
    if (!tpl || !l) return;
    let txt = (tpl.content || '')
      .replace(/\{nome\}/g, l.name || 'sua empresa')
      .replace(/\{categoria\}/g, l.category || 'seu segmento')
      .replace(/\{bairro\}/g, l.neighborhood || l.city || 'sua região')
      .replace(/\{rua\}/g, l.street || '')
      .replace(/\{avaliacao\}/g, l.rating || '5.0')
      .replace(/\{avaliacoes\}/g, l.reviews_count || '0');
    document.getElementById('chat-input-text').value = txt;
  });

  document.getElementById('btn-chat-send')?.addEventListener('click', sendChatMessage);
  document.getElementById('chat-input-text')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });

  document.getElementById('chat-peer-status')?.addEventListener('change', async (e) => {
    const l = STATE.activeChatLead;
    if (!l) return;
    await apiFetch(`/api/leads/${l.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ crm_status: e.target.value })
    });
    toast('Etapa atualizada!', 'success');
    loadStats();
    loadLeads();
  });

  document.getElementById('btn-chat-open-drawer')?.addEventListener('click', () => {
    if (STATE.activeChatLead) openLeadDrawer(STATE.activeChatLead);
  });
}

async function loadChatThreads() {
  const list = document.getElementById('chat-thread-list');
  if (!list) return;
  const search = document.getElementById('chat-search-input')?.value || '';
  const qs = new URLSearchParams({ filter: STATE.chatFilter, search });
  try {
    const res = await apiFetch(`/api/chat/threads?${qs.toString()}`);
    const threads = await res.json();
    STATE.chatThreads = threads;

    const repliesCount = threads.filter(t => t.had_reply || t.crm_status === 'respondeu').length;
    const badge = document.getElementById('badge-chat-replies');
    if (badge) {
      badge.textContent = repliesCount;
      badge.classList.toggle('hidden', repliesCount === 0);
    }

    if (!threads.length) {
      list.innerHTML = '<div class="chat-empty">Nenhuma conversa ativa ainda.<br><small>Envie uma abordagem pelo CRM para aparecer aqui.</small></div>';
      return;
    }

    list.innerHTML = threads.map(t => {
      const activeCls = STATE.activeChatLead?.id === t.id ? 'active' : '';
      const replyTag = (t.had_reply || t.crm_status === 'respondeu')
        ? '<span class="opp-badge opp-wa">Respondeu</span>'
        : `<span class="status-pill" style="font-size:0.68rem">${escapeHtml(t.crm_status)}</span>`;
      return `
        <div class="chat-thread-item ${activeCls}" data-id="${t.id}">
          <div class="chat-thread-top">
            <strong>${escapeHtml(t.name)}</strong>
            ${replyTag}
          </div>
          <div class="chat-thread-preview">${escapeHtml(t.last_message || t.phone || 'Contato registrado')}</div>
        </div>
      `;
    }).join('');

    list.querySelectorAll('.chat-thread-item').forEach(el => {
      el.addEventListener('click', () => {
        const t = threads.find(x => x.id === Number(el.dataset.id));
        if (t) openChatThread(t);
      });
    });
  } catch (e) {}
}

async function openChatThread(lead) {
  STATE.activeChatLead = lead;
  document.querySelectorAll('.chat-thread-item').forEach(el => {
    el.classList.toggle('active', Number(el.dataset.id) === lead.id);
  });
  document.getElementById('chat-main-empty').classList.add('hidden');
  document.getElementById('chat-active-pane').classList.remove('hidden');
  document.getElementById('chat-peer-name').textContent = lead.name;
  document.getElementById('chat-peer-meta').textContent = `${lead.phone || ''} · ${lead.category || ''} · ${lead.neighborhood || lead.city || ''}`;
  document.getElementById('chat-peer-status').value = lead.crm_status || 'contatado';

  const sel = document.getElementById('chat-template-select');
  sel.innerHTML = '<option value="">Inserir modelo rápido...</option>' +
    STATE.templates.map(t => `<option value="${escapeHtml(t.id)}">${escapeHtml(t.title)}</option>`).join('');

  await renderActiveChatMessages(lead.id);
}

async function renderActiveChatMessages(leadId) {
  const box = document.getElementById('chat-messages-box');
  if (!box) return;
  try {
    const res = await apiFetch(`/api/leads/${leadId}/conversation`);
    const msgs = await res.json();
    if (!msgs.length) {
      box.innerHTML = '<div class="chat-empty">Nenhuma mensagem trocada ainda. Envie a primeira abaixo!</div>';
      return;
    }
    box.innerHTML = msgs.map(m => `
      <div class="chat-bubble ${m.direction === 'out' ? 'out' : 'in'}">
        <div>${escapeHtml(m.text)}</div>
        <span class="chat-bubble-meta">${escapeHtml((m.created_at || '').slice(0, 16).replace('T', ' '))} · ${escapeHtml(m.status || '')}</span>
      </div>
    `).join('');
    box.scrollTop = box.scrollHeight;
  } catch (e) {}
}

async function sendChatMessage() {
  const l = STATE.activeChatLead;
  const input = document.getElementById('chat-input-text');
  const text = (input.value || '').trim();
  if (!l || !text) return;

  input.disabled = true;
  try {
    const res = await apiFetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_id: l.id, text })
    });
    const d = await res.json();
    if (d.success) {
      input.value = '';
      if (d.channel === 'web_1click' && d.wa_url) {
        window.open(d.wa_url, '_blank');
        toast('Aberto no WhatsApp Web e registrado no histórico!', 'info');
      } else {
        toast('Mensagem enviada!', 'success');
      }
      await renderActiveChatMessages(l.id);
      loadChatThreads();
    } else {
      toast(d.error || 'Erro ao enviar mensagem.', 'error');
    }
  } finally {
    input.disabled = false;
    input.focus();
  }
}

// ==================== ADMIN ====================
function copyBillingWebhookUrl() {
  const url = document.getElementById('billing-webhook-url')?.textContent || '';
  if (url) {
    navigator.clipboard.writeText(url);
    toast('Webhook de cobrança copiado!', 'success');
  }
}

let _adminUsersCache = [];
let _adminFilter = 'all';

function initAdminControls() {
  const bWh = document.getElementById('billing-webhook-url');
  if (bWh) bWh.textContent = `${window.location.origin}/api/billing/webhook`;

  document.getElementById('admin-search-input')?.addEventListener('input', renderAdminUsersTable);
  document.querySelectorAll('[data-adm-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-adm-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      _adminFilter = btn.dataset.admFilter;
      renderAdminUsersTable();
    });
  });

  document.getElementById('btn-cleanup-trials')?.addEventListener('click', async () => {
    const res = await apiFetch('/api/admin/cleanup-trials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grace_days: 15 })
    });
    const d = await res.json();
    if (d.success) {
      toast(`${d.removed || 0} conta(s) de teste abandonada(s) removida(s).`, 'success');
      loadAdminUsers();
    }
  });

  document.getElementById('form-admin-site-settings')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const res = await apiFetch('/api/admin/site-settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        checkout_url: document.getElementById('site-checkout-url').value,
        plan_starter_price: document.getElementById('site-starter-price').value,
        checkout_pro_url: document.getElementById('site-checkout-pro-url').value,
        plan_pro_price: document.getElementById('site-pro-price').value,
        support_whatsapp: document.getElementById('site-support-wa').value,
      })
    });
    const d = await res.json();
    if (d.success) toast('Página de vendas, planos Kiwify e WhatsApp comercial atualizados!', 'success');
  });

  document.getElementById('form-admin-create-user')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target).entries());
    const res = await apiFetch('/api/admin/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await res.json();
    if (d.success) {
      toast('Conta criada com sucesso!', 'success');
      e.target.reset();
      loadAdminUsers();
    } else {
      toast(d.error || 'Erro ao criar usuário.', 'error');
    }
  });
}

async function loadAdminUsers() {
  const tb = document.getElementById('admin-users-tbody');
  if (!tb) return;
  try {
    const res = await apiFetch('/api/admin/users');
    const d = await res.json();
    if (!d.success) return;
    _adminUsersCache = d.users || [];

    try {
      const sr = await apiFetch('/api/admin/site-settings');
      const sd = await sr.json();
      if (sd.success && sd.settings) {
        const cu = document.getElementById('site-checkout-url');
        const sp = document.getElementById('site-starter-price');
        const cpu = document.getElementById('site-checkout-pro-url');
        const pp = document.getElementById('site-pro-price');
        const sw = document.getElementById('site-support-wa');
        if (cu) cu.value = sd.settings.checkout_url || '';
        if (sp) sp.value = sd.settings.plan_starter_price || 'R$ 37';
        if (cpu) cpu.value = sd.settings.checkout_pro_url || '';
        if (pp) pp.value = sd.settings.plan_pro_price || 'R$ 79';
        if (sw) sw.value = sd.settings.support_whatsapp || '';
      }
    } catch (e) {}

    const st = d.stats || {};
    document.getElementById('adm-kpi-paid').textContent = st.paid_active || 0;
    document.getElementById('adm-kpi-trial').textContent = st.trial_active || 0;
    document.getElementById('adm-kpi-expired').textContent = st.expired_count || 0;
    document.getElementById('adm-kpi-clients').textContent = st.total_clients || 0;
    document.getElementById('adm-kpi-leads').textContent = st.total_leads || 0;

    renderAdminUsersTable();

    const evTb = document.getElementById('admin-events-tbody');
    if (evTb) {
      const evs = st.recent_events || [];
      evTb.innerHTML = evs.length ? evs.map(ev => `
        <tr>
          <td>${escapeHtml((ev.created_at || '').slice(0, 16).replace('T', ' '))}</td>
          <td><span class="status-pill">${escapeHtml(ev.gateway)}</span></td>
          <td>${escapeHtml(ev.event_type)}</td>
          <td>${escapeHtml(ev.email)}</td>
          <td><strong>${escapeHtml(ev.status)}</strong> <small class="text-muted">${escapeHtml(ev.details || '')}</small></td>
        </tr>
      `).join('') : '<tr><td colspan="5" class="text-muted">Nenhum evento de pagamento recebido ainda.</td></tr>';
    }
  } catch (e) {}
}

function renderAdminUsersTable() {
  const tb = document.getElementById('admin-users-tbody');
  if (!tb) return;
  const q = (document.getElementById('admin-search-input')?.value || '').trim().toLowerCase();
  const nowIso = new Date().toISOString();

  const filtered = _adminUsersCache.filter(u => {
    const subSt = u.subscription_status || 'active';
    const isExp = (!u.is_active) || subSt === 'expired' || subSt === 'suspended' || (u.plan_expires_at && u.plan_expires_at < nowIso);
    const isTrial = !isExp && (u.plan === 'trial' || subSt === 'trial');
    const isPaid = !isExp && !isTrial && u.role !== 'admin';

    if (_adminFilter === 'paid' && !isPaid) return false;
    if (_adminFilter === 'trial' && !isTrial) return false;
    if (_adminFilter === 'expired' && !isExp) return false;
    if (q) {
      const hay = `${u.name || ''} ${u.email || ''} ${u.company_name || ''}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  tb.innerHTML = filtered.length ? filtered.map(u => {
    const exp = u.plan_expires_at ? u.plan_expires_at.slice(0, 10) : (u.role === 'admin' ? 'Vitalício' : '-');
    const isTrialPlan = (u.plan || 'trial') === 'trial';
    const usedQuota = isTrialPlan ? (u.leads_count || 0) : (u.leads_30d_count ?? u.leads_count ?? 0);
    const limitStr = u.max_leads > 0 ? ` / ${u.max_leads}` : ' / ilimitado';
    const subSt = u.subscription_status || 'active';
    const isOk = u.is_active && subSt !== 'expired' && subSt !== 'suspended';
    const targetPlan = isTrialPlan ? 'starter' : (u.plan || 'starter');
    return `
    <tr>
      <td>#${u.id}</td>
      <td><strong>${escapeHtml(u.name)}</strong><div class="text-muted" style="font-size:0.75rem">${escapeHtml(u.company_name || '')}</div></td>
      <td>${escapeHtml(u.email)}</td>
      <td><span class="status-pill">${escapeHtml(u.plan === 'agency' ? 'enterprise' : u.plan)}</span></td>
      <td>${escapeHtml(exp)}</td>
      <td>${usedQuota}${limitStr}</td>
      <td><span class="status-pill ${isOk ? 'ok' : 'err'}">${u.is_active ? escapeHtml(subSt) : 'bloqueada'}</span></td>
      <td style="display:flex; gap:6px; flex-wrap:wrap;">
        <button class="btn btn-emerald btn-xs" onclick="renewUser(${u.id}, 30, '${escapeHtml(targetPlan)}')">+30d (${escapeHtml(targetPlan)})</button>
        <button class="btn btn-outline btn-xs" onclick="renewUser(${u.id}, 30, 'pro')">PRO</button>
        <button class="btn btn-outline btn-xs" onclick="toggleUserActive(${u.id}, ${u.is_active ? 0 : 1})">
          ${u.is_active ? 'Bloquear' : 'Liberar'}
        </button>
      </td>
    </tr>`;
  }).join('') : '<tr><td colspan="8" class="text-muted">Nenhuma conta encontrada nesse filtro.</td></tr>';
}

async function renewUser(uid, days = 30, plan = 'starter') {
  const res = await apiFetch(`/api/admin/users/${uid}/renew`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ days, plan })
  });
  const d = await res.json();
  if (d.success) {
    toast(`Assinatura renovada por +${days} dias (Plano ${String(plan).toUpperCase()})!`, 'success');
    loadAdminUsers();
  }
}

async function toggleUserActive(uid, active) {
  await apiFetch(`/api/admin/users/${uid}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: active })
  });
  toast('Status do usuário atualizado.', 'success');
  loadAdminUsers();
}

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}
