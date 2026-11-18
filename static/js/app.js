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
  academyLessons: [],
  activeLessonId: null,
  academyModuleFilter: 'all',
  salesAcademy: { unlocked: false, items: [], completed_count: 0, total_count: 5, percent: 0 },
  activeSalesCourseId: null,
  salesAcademyMode: 'course',
};

const TAB_META = {
  'tab-dashboard': ['Visão Geral', 'Acompanhe suas oportunidades de venda e resultados no Google'],
  'tab-search': ['Buscar Empresas', 'Encontre negócios locais com telefone válido para ofertar seus serviços'],
  'tab-map': ['Mapa de Oportunidades', 'Visualize seus leads e clique em qualquer rua para prospectar'],
  'tab-crm': ['CRM & Pipeline', 'Gerencie negociações no Kanban ou em lista e envie abordagens'],
  'tab-chat': ['Chat / Conversas', 'Atenda e acompanhe suas conversas ativas estilo Kommo'],
  'tab-templates': ['Modelos de Copy', 'Mensagens prontas para Google Meu Negócio, Plaquinhas NFC, WhatsApp, Cardápio e Biossites'],
  'tab-academy': ['Como Usar (Tutoriais)', 'Aprenda passo a passo a captar leads, limpar sua base e atender no WhatsApp'],
  'tab-sales-academy': ['Academia de Vendas PRO', 'Cursos de fechamento por estratégia + VSLs prontas para baixar e divulgar'],
  'tab-settings': ['WhatsApp & Conta', 'Configure o WhatsApp por QR Code, API Oficial da Meta e seus dados'],
  'tab-admin': ['Painel Admin', 'Gerencie contas de clientes e planos do sistema'],
};

const OPP_LABELS = {
  gmn: { label: 'Google Meu Negócio', cls: 'opp-gmn', icon: 'fa-map-pin' },
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
  initAcademyControls();
  initSalesAcademyControls();
  initSettingsControls();
  initAdminControls();
  initSSE();
  if (window.ACCESS_STATUS) updateTopbarQuotaDisplay(window.ACCESS_STATUS);

  loadAllData();
});

async function loadAllData() {
  await Promise.all([
    loadStats(),
    loadLeads(),
    loadTemplates(),
    loadSegments(),
    loadSearchHistory(),
    loadChatThreads(),
    loadAcademyLessons(),
    loadSalesAcademy(),
    loadOnboardingAndActivations(),
    loadMyResultsDashboard(),
    loadCrmFollowupSummary(),
  ]);
  if (window.CURRENT_USER && window.CURRENT_USER.role === 'admin') {
    loadAdminUsers();
    loadAdminSaasOverview();
    loadAdminAcademyLessons();
    loadAdminActivationRules();
    loadAdminSystemHealthAndBackups();
  }
}

function openUpgradeModal(customMsg) {
  const modal = document.getElementById('upgrade-plan-modal');
  if (!modal) return;
  if (customMsg) {
    const desc = document.getElementById('upgrade-modal-desc');
    if (desc) desc.textContent = customMsg;
  }
  modal.classList.remove('hidden');
}

function closeUpgradeModal() {
  const modal = document.getElementById('upgrade-plan-modal');
  if (!modal || modal.dataset.locked === '1') return;
  modal.classList.add('hidden');
}

async function apiFetch(url, opts = {}) {
  const res = await fetch(url, opts);
  if (res.status === 401) {
    window.location.href = '/login';
    throw new Error('Sessão expirada');
  }
  if (res.status === 402 || res.status === 403) {
    try {
      const clone = res.clone();
      const body = await clone.json();
      if (res.status === 402 || body.upgrade_required) {
        openUpgradeModal(body.error);
      }
    } catch (e) {
      if (res.status === 402) openUpgradeModal();
    }
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
        labels: ['Google Meu Negócio', 'Plaquinha NFC + QR', 'WhatsApp Business', 'Biossite / LP', 'Cardápio Digital'],
        datasets: [{
          label: 'Empresas com Oportunidade',
          data: [opps.gmn || 0, opps.nfc_google || 0, opps.whatsapp_biz || 0, opps.biossite || 0, opps.cardapio_digital || 0],
          backgroundColor: ['#1d4ed8', '#7c3aed', '#10b981', '#2563eb', '#f59e0b'],
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
  const visible = Boolean(document.getElementById('chk-visible-browser')?.checked);
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
      if (data.leads_limit_reached) refreshTopbarQuota();
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

  es.addEventListener('search_completed', async (e) => {
    const d = JSON.parse(e.data || '{}');
    document.getElementById('search-progress-bar').style.width = '100%';
    document.getElementById('search-status-text').textContent = d.message || 'Busca concluída!';
    toast(d.message || 'Busca concluída!', 'success');
    loadAllData();
    try {
      const mr = await apiFetch('/api/me');
      const md = await mr.json();
      const acc = md.access;
      if (acc) {
        updateTopbarQuotaDisplay(acc);
        if (!acc.active) {
          openUpgradeModal(`Seu período de acesso do plano (${String(acc.plan).toUpperCase()}) encerrou. Escolha um plano para continuar!`);
        } else if (acc.leads_limit_reached) {
          toast(`Limite de ${acc.max_leads} leads do seu plano atingido! Novas buscas foram pausadas, mas seus ${acc.leads_count} leads continuam 100% liberados para ver e atender no CRM e Chat.`, 'info');
        }
      }
    } catch (err) {}
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
  document.getElementById('crm-filter-score')?.addEventListener('change', loadLeads);
  document.getElementById('crm-sort-by')?.addEventListener('change', loadLeads);
  document.getElementById('crm-filter-followup')?.addEventListener('change', loadLeads);
  document.getElementById('crm-filter-wa')?.addEventListener('change', () => {
    renderKanban();
    renderTable();
  });

  document.getElementById('btn-verify-wa-crm')?.addEventListener('click', verifyWhatsAppBatchFromCrm);
  document.getElementById('btn-purge-no-wa')?.addEventListener('click', () => cleanupLeads('sem_whatsapp'));

  document.getElementById('btn-dedup-leads')?.addEventListener('click', async () => {
    const res = await apiFetch('/api/leads/deduplicate', { method: 'POST' });
    const d = await res.json();
    toast(`${d.duplicates_removed || 0} leads duplicados removidos.`, 'success');
    loadAllData();
    refreshTopbarQuota();
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
  const scoreLvl = document.getElementById('crm-filter-score')?.value || 'all';
  const sortBy = document.getElementById('crm-sort-by')?.value || 'recent';
  const fuFilter = document.getElementById('crm-filter-followup')?.value || 'all';
  const qs = new URLSearchParams({
    search,
    opportunity: opp,
    website_type: wt,
    opportunity_level: scoreLvl,
    sort_by: sortBy,
    followup_filter: fuFilter,
    limit: 1000,
  });
  try {
    const res = await apiFetch(`/api/leads?${qs.toString()}`);
    STATE.leads = await res.json();
    renderKanban();
    renderTable();
  } catch (e) {}
}

function renderLeadScoreBadge(l) {
  const sc = Number(l.lead_score || 0);
  if (!sc) return '';
  const lvl = l.opportunity_level || (sc >= 70 ? 'alta' : (sc >= 45 ? 'media' : 'baixa'));
  const bg = lvl === 'alta' ? '#dcfce7' : (lvl === 'media' ? '#fef3c7' : '#f1f5f9');
  const col = lvl === 'alta' ? '#166534' : (lvl === 'media' ? '#92400e' : '#475569');
  const icon = lvl === 'alta' ? '🔥' : (lvl === 'media' ? '⚡' : '•');
  const tip = (l.score_reasons || []).map(r => `+${r.points}: ${r.label}`).join(' | ');
  return `<span class="opp-badge" style="background:${bg};color:${col};font-weight:700;" title="${escapeHtml(tip)}">${icon} ${sc} pts</span>`;
}

function renderFollowupBadge(l) {
  const nfu = (l.next_followup_at || '').trim();
  if (!nfu) return '';
  const today = new Date().toISOString().slice(0, 10);
  const isDue = nfu.slice(0, 10) <= today;
  const bg = isDue ? '#fee2e2' : '#e0f2fe';
  const col = isDue ? '#991b1b' : '#075985';
  return `<span class="opp-badge" style="background:${bg};color:${col};" title="${escapeHtml(l.followup_note || 'Follow-up agendado')}"><i class="fa-regular fa-clock"></i> ${escapeHtml(nfu.slice(0, 10))}</span>`;
}

function renderOpportunityBadges(opps = [], maxCount = 2) {
  return (opps || []).slice(0, maxCount).map(k => {
    const info = OPP_LABELS[k];
    if (!info) return '';
    return `<span class="opp-badge ${info.cls}"><i class="fa-solid ${info.icon}"></i> ${info.label}</span>`;
  }).join('');
}

function getFilteredCrmLeads() {
  const waFilter = document.getElementById('crm-filter-wa')?.value || 'all';
  return (STATE.leads || []).filter(l => {
    if (waFilter === 'mobile') return l.phone_type !== 'fixed' && l.whatsapp_verified !== -1 && l.crm_status !== 'sem_whatsapp' && Boolean(l.clean_phone);
    if (waFilter === 'sem_whatsapp') return l.crm_status === 'sem_whatsapp' || l.whatsapp_verified === -1 || l.whatsapp_status === 'sem_whatsapp' || !l.clean_phone;
    if (waFilter === 'fixed') return l.phone_type === 'fixed';
    return true;
  });
}

function renderPhoneStatusBadge(l) {
  if (l.crm_status === 'sem_whatsapp' || l.whatsapp_verified === -1 || l.whatsapp_status === 'sem_whatsapp' || !l.clean_phone) {
    return '<span class="opp-badge opp-nowa"><i class="fa-solid fa-phone-slash"></i> Sem WhatsApp</span>';
  }
  if (l.phone_type === 'fixed') {
    return '<span class="opp-badge opp-fixed"><i class="fa-solid fa-phone"></i> Fixo</span>';
  }
  return '';
}

function renderKanban() {
  const cols = { novo: [], contatado: [], respondeu: [], negociacao: [], fechado: [], sem_whatsapp: [], perdido: [] };
  getFilteredCrmLeads().forEach(l => {
    const st = cols[l.crm_status] ? l.crm_status : 'novo';
    cols[st].push(l);
  });

  Object.entries(cols).forEach(([status, items]) => {
    const container = document.getElementById(`col-${status}`);
    if (!container) return;
    container.innerHTML = items.map(l => `
      <div class="lead-card" data-id="${l.id}">
        <div class="lead-card-top">
          <div class="lead-card-title">${escapeHtml(l.name)}</div>
          <button type="button" class="lead-card-del" onclick="event.stopPropagation(); deleteLeadQuick(${l.id}, '${escapeHtml(l.name).replace(/'/g, "\\'")}')" title="Excluir lead">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
        <div class="lead-card-sub">${escapeHtml(l.category || 'Negócio local')} · ${escapeHtml(l.neighborhood || l.city || '')}</div>
        <div class="lead-card-badges">${renderPhoneStatusBadge(l)}${renderFollowupBadge(l)}${renderOpportunityBadges(l.opportunities, 2)}</div>
        <div class="lead-card-foot">
          <span><i class="fa-solid fa-star" style="color:#f59e0b"></i> ${l.rating || '-'} (${l.reviews_count || 0})${l.lead_score ? ` · <strong style="color:${l.opportunity_level === 'alta' ? '#059669' : 'inherit'}">${l.lead_score}pts</strong>` : ''}</span>
          <span>${l.sale_value ? formatBRL(l.sale_value) : escapeHtml(l.phone || 'Sem tel.')}</span>
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
  ['novo', 'contatado', 'respondeu', 'negociacao', 'fechado', 'sem_whatsapp', 'perdido'].forEach(st => {
    const c = document.getElementById(`col-${st}`);
    const cnt = document.getElementById(`cnt-${st}`);
    if (c && cnt) cnt.textContent = c.children.length;
  });
  const noWaCount = (STATE.leads || []).filter(l => l.crm_status === 'sem_whatsapp' || l.whatsapp_verified === -1 || l.whatsapp_status === 'sem_whatsapp' || !l.clean_phone).length;
  const purgeEl = document.getElementById('cnt-purge-nowa');
  if (purgeEl) purgeEl.textContent = noWaCount;
}

function renderTable() {
  const tb = document.getElementById('crm-table-tbody');
  if (!tb) return;
  const rows = getFilteredCrmLeads();
  if (!rows.length) {
    tb.innerHTML = '<tr><td colspan="6" class="text-muted">Nenhum lead encontrado com os filtros atuais.</td></tr>';
    return;
  }
  const statusLabels = {
    novo: 'Novo', contatado: 'Contatado', respondeu: 'Respondeu',
    negociacao: 'Proposta', fechado: 'Fechado', sem_whatsapp: 'Sem WhatsApp', perdido: 'Perdido'
  };
  tb.innerHTML = rows.map(l => `
    <tr>
      <td><strong>${escapeHtml(l.name)}</strong><div class="text-muted" style="font-size:0.75rem">${escapeHtml(l.category || '')} · ${escapeHtml(l.neighborhood || l.city || '')}</div></td>
      <td>${escapeHtml(l.phone || '-')}<div>${renderPhoneStatusBadge(l)}</div></td>
      <td><div style="display:flex;gap:4px;flex-wrap:wrap">${renderLeadScoreBadge(l)}${renderFollowupBadge(l)}${renderOpportunityBadges(l.opportunities)}</div></td>
      <td>${l.rating || '-'} ⭐ (${l.reviews_count || 0})</td>
      <td><span class="status-pill">${escapeHtml(statusLabels[l.crm_status] || l.crm_status)}</span></td>
      <td style="white-space:nowrap;">
        <button class="btn btn-outline btn-xs" onclick="openLeadDrawerById(${l.id})">Abrir</button>
        ${l.crm_status !== 'sem_whatsapp' ? `<button class="btn btn-outline btn-xs" onclick="quickMarkStatus(${l.id}, 'sem_whatsapp')" title="Marcar sem WhatsApp"><i class="fa-solid fa-phone-slash"></i></button>` : ''}
        <button class="btn btn-outline btn-xs text-danger" onclick="deleteLeadQuick(${l.id}, '${escapeHtml(l.name).replace(/'/g, "\\'")}')" title="Excluir lead"><i class="fa-solid fa-trash-can"></i></button>
      </td>
    </tr>
  `).join('');
}

async function deleteLeadQuick(leadId, leadName = '') {
  if (!confirm(`Excluir "${leadName || 'este lead'}" da sua base e liberar vaga na cota?`)) return;
  const res = await apiFetch(`/api/leads/${leadId}`, { method: 'DELETE' });
  const d = await res.json();
  if (d.success) {
    toast('Lead excluído e vaga liberada.', 'info');
    if (d.access) updateTopbarQuotaDisplay(d.access);
    loadAllData();
  }
}

async function quickMarkStatus(leadId, newStatus) {
  await apiFetch(`/api/leads/${leadId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ crm_status: newStatus })
  });
  toast(newStatus === 'sem_whatsapp' ? 'Movido para Sem WhatsApp.' : 'Movido para Lead Perdido.', 'info');
  loadAllData();
}

async function deleteKanbanColumnLeads(status, colLabel) {
  const colEl = document.getElementById(`col-${status}`);
  const ids = colEl
    ? Array.from(colEl.querySelectorAll('.lead-card')).map(c => Number(c.dataset.id)).filter(Boolean)
    : [];
  if (!ids.length && status !== 'sem_whatsapp') {
    toast(`A coluna "${colLabel}" já está vazia.`, 'info');
    return;
  }
  const msg = ids.length
    ? `Excluir todos os ${ids.length} lead(s) visíveis na coluna "${colLabel}" e liberar espaço na sua conta?`
    : `Excluir todos os leads da coluna "${colLabel}" e liberar espaço na sua conta?`;
  if (!confirm(msg)) return;

  const payload = ids.length ? { mode: status, ids } : { mode: status };
  const res = await apiFetch('/api/leads/cleanup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const d = await res.json();
  if (d.success) {
    toast(`${d.removed || 0} lead(s) excluídos da coluna "${colLabel}"!`, 'success');
    if (d.access) updateTopbarQuotaDisplay(d.access);
    loadAllData();
  } else {
    toast(d.error || 'Erro ao excluir leads da coluna.', 'error');
  }
}

async function cleanupLeads(mode = 'sem_whatsapp') {
  const msg = mode === 'perdido'
    ? 'Excluir TODOS os leads marcados como "Lead Perdido" para limpar seu funil e liberar espaço?'
    : 'Excluir TODOS os leads sem WhatsApp confirmado (ou sem telefone) para liberar espaço na sua conta?';
  if (!confirm(msg)) return;
  const res = await apiFetch('/api/leads/cleanup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode })
  });
  const d = await res.json();
  if (d.success) {
    toast(`${d.removed || 0} lead(s) removidos! Espaço liberado na sua conta.`, 'success');
    if (d.access) updateTopbarQuotaDisplay(d.access);
    loadAllData();
  } else {
    toast(d.error || 'Erro ao limpar leads.', 'error');
  }
}

async function verifyWhatsAppBatchFromCrm() {
  const btn = document.getElementById('btn-verify-wa-crm');
  const orig = btn ? btn.innerHTML : '';
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verificando...'; }
  try {
    const res = await apiFetch('/api/leads/verify-whatsapp-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ only_unverified: true })
    });
    const d = await res.json();
    if (!d.success) {
      toast(d.error || 'Conecte seu WhatsApp QR em "WhatsApp & Conta" para verificar números automaticamente.', 'info');
      return;
    }
    toast(`Verificados: ${d.active || 0} têm WhatsApp e ${d.inactive || 0} foram movidos para "Sem WhatsApp".`, 'success');
    loadAllData();
  } catch (e) {
    toast('Erro ao verificar números.', 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = orig; }
  }
}

function updateSearchLimitBanner(acc) {
  const banner = document.getElementById('search-limit-banner');
  if (!banner || !acc) return;
  const isAdmin = window.CURRENT_USER && window.CURRENT_USER.role === 'admin';
  const showBanner = Boolean(!isAdmin && acc.active && acc.leads_limit_reached);
  banner.classList.toggle('hidden', !showBanner);
  const maxEl = document.getElementById('search-limit-max');
  const curEl = document.getElementById('search-limit-current');
  if (maxEl && acc.max_leads > 0) maxEl.textContent = acc.max_leads;
  if (curEl) curEl.textContent = acc.leads_count ?? 0;
}

function updateTopbarQuotaDisplay(acc) {
  if (!acc) return;
  window.ACCESS_STATUS = acc;
  updateSearchLimitBanner(acc);
  const pt = document.getElementById('topbar-plan-text');
  if (!pt) return;
  if (acc.plan === 'trial') {
    pt.innerHTML = `Teste (${acc.hours_left || 24}h) · ${acc.leads_count}/${acc.max_leads} leads · <u>Assinar</u>`;
  } else if (acc.max_leads > 0) {
    pt.textContent = `${String(acc.plan).toUpperCase()}: ${acc.leads_count}/${acc.max_leads} leads salvos · ${acc.days_left}d`;
  }
}

async function refreshTopbarQuota() {
  try {
    const r = await apiFetch('/api/me');
    const d = await r.json();
    if (d.access) updateTopbarQuotaDisplay(d.access);
  } catch (e) {}
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

  document.getElementById('btn-drawer-mark-no-wa')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l) return;
    await quickMarkStatus(l.id, 'sem_whatsapp');
    closeLeadDrawer();
  });

  document.getElementById('btn-drawer-mark-lost')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l) return;
    await quickMarkStatus(l.id, 'perdido');
    closeLeadDrawer();
  });

  document.getElementById('btn-drawer-delete')?.addEventListener('click', async () => {
    const l = STATE.selectedLead;
    if (!l || !confirm(`Excluir "${l.name}"?`)) return;
    const res = await apiFetch(`/api/leads/${l.id}`, { method: 'DELETE' });
    const d = await res.json();
    toast('Lead excluído e vaga liberada.', 'info');
    if (d.access) updateTopbarQuotaDisplay(d.access);
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

  // P1.1 — Lead Score & Justificativas
  const scorePill = document.getElementById('drawer-lead-score-pill');
  const nextActEl = document.getElementById('drawer-next-action-line');
  const reasonsEl = document.getElementById('drawer-score-reasons');
  if (scorePill) {
    const sc = Number(l.lead_score || 0);
    const lvl = l.opportunity_level || 'media';
    scorePill.textContent = `${sc}/100 · ${l.opportunity_label || 'Oportunidade'}`;
    scorePill.style.background = lvl === 'alta' ? '#dcfce7' : (lvl === 'media' ? '#fef3c7' : '#e2e8f0');
    scorePill.style.color = lvl === 'alta' ? '#166534' : (lvl === 'media' ? '#92400e' : '#334155');
  }
  if (nextActEl) {
    nextActEl.innerHTML = l.next_action
      ? `<i class="fa-solid fa-wand-magic-sparkles"></i> Próxima Ação Recomendada: ${escapeHtml(l.next_action.label)}`
      : '';
  }
  if (reasonsEl) {
    const reasons = l.score_reasons || [];
    reasonsEl.innerHTML = reasons.map(r => `
      <div>• <strong>+${r.points} pts</strong> (${r.type === 'verified' ? 'Verificado' : 'Critério comercial'}): ${escapeHtml(r.label)}</div>
    `).join('');
  }

  // P1.2 — Reset Copiloto IA Output
  const aiWrap = document.getElementById('drawer-ai-output-wrap');
  if (aiWrap) aiWrap.classList.add('hidden');

  // P1.3 — Follow-up & Interações
  const fuDate = document.getElementById('drawer-followup-date');
  const fuNote = document.getElementById('drawer-followup-note');
  if (fuDate) fuDate.value = (l.next_followup_at || '').slice(0, 10);
  if (fuNote) fuNote.value = l.followup_note || '';
  loadLeadInteractions(l.id);

  // P0.3 & P0.1 — Track lead_viewed
  apiFetch('/api/analytics/event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event_name: 'lead_viewed', metadata: { lead_id: l.id } }),
  }).then(() => loadOnboardingAndActivations()).catch(() => {});

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
      txt.innerHTML = 'O botão de conexão 1-clique estilo Kommo precisa apenas de um <strong>Meta App de Provedor de Tecnologia</strong> configurado uma única vez pelo administrador em <strong>Painel Admin → Conexão Oficial WhatsApp 1-Clique</strong>. Enquanto isso, cada cliente já pode conectar abaixo via Configuração Manual ou usar o WhatsApp QR / Web 1-Clique.';
    }
    btn.addEventListener('click', () => {
      toast('Falta cadastrar o Meta App ID + Embedded Config ID no Painel Admin (veja as instruções no chat). Enquanto isso, use o QR Code ou a Configuração Manual abaixo.', 'info');
    });
    return;
  }

  window.addEventListener('message', (event) => {
    if (event.origin !== 'https://www.facebook.com' && event.origin !== 'https://web.facebook.com') return;
    try {
      const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
      if (data?.type === 'WA_EMBEDDED_SIGNUP' && (data?.event === 'FINISH' || data?.event === 'FINISH_ONLY_WABA' || data?.event === 'FINISH_WHATSAPP_BUSINESS_APP_ONBOARDING')) {
        _embeddedSignupSession.phone_number_id = data.data?.phone_number_id || '';
        _embeddedSignupSession.waba_id = data.data?.waba_id || '';
      }
    } catch (e) {}
  });

  if (txt) {
    txt.textContent = 'Pronto! Clique ao lado para conectar seu WhatsApp Business oficial em 1 clique usando sua conta do Facebook (sem copiar tokens manualmente).';
  }

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
      extras: { setup: {}, featureType: '', sessionInfoVersion: '3' },
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
        meta_app_id: document.getElementById('site-meta-app-id')?.value || '',
        meta_embedded_config_id: document.getElementById('site-meta-config-id')?.value || '',
        meta_app_secret: document.getElementById('site-meta-app-secret')?.value || '',
        oci_backup_par_url: document.getElementById('site-oci-par-url')?.value || '',
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

  document.getElementById('btn-admin-academy-reset')?.addEventListener('click', () => {
    document.getElementById('form-admin-academy-lesson')?.reset();
    const idEl = document.getElementById('adm-lesson-id');
    if (idEl) idEl.value = '';
    const pubEl = document.getElementById('adm-lesson-published');
    if (pubEl) pubEl.checked = true;
  });

  document.getElementById('form-admin-academy-lesson')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const lid = document.getElementById('adm-lesson-id')?.value;
    const payload = {
      module_name: document.getElementById('adm-lesson-module')?.value || '',
      title: document.getElementById('adm-lesson-title')?.value || '',
      video_url: document.getElementById('adm-lesson-url')?.value || '',
      duration_text: document.getElementById('adm-lesson-duration')?.value || '01:00',
      sort_order: Number(document.getElementById('adm-lesson-order')?.value || 10),
      target_tab: document.getElementById('adm-lesson-tab')?.value || '',
      description: document.getElementById('adm-lesson-desc')?.value || '',
      is_published: Boolean(document.getElementById('adm-lesson-published')?.checked),
    };
    const url = lid ? `/api/admin/academy/lessons/${lid}` : '/api/admin/academy/lessons';
    const res = await apiFetch(url, {
      method: lid ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const d = await res.json();
    if (d.success) {
      toast(lid ? 'Videoaula atualizada!' : 'Videoaula adicionada na Academia!', 'success');
      document.getElementById('btn-admin-academy-reset')?.click();
      loadAdminAcademyLessons();
      loadAcademyLessons();
    } else {
      toast(d.error || 'Erro ao salvar videoaula.', 'error');
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
        const mai = document.getElementById('site-meta-app-id');
        const mci = document.getElementById('site-meta-config-id');
        const mas = document.getElementById('site-meta-app-secret');
        const opu = document.getElementById('site-oci-par-url');
        if (mai) mai.value = sd.settings.meta_app_id || '';
        if (mci) mci.value = sd.settings.meta_embedded_config_id || '';
        if (mas) mas.value = sd.settings.meta_app_secret || '';
        if (opu) opu.value = sd.settings.oci_backup_par_url || '';
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
    const usedQuota = u.leads_count || 0;
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
        <button class="btn btn-primary btn-xs" onclick="openAdminEditUserModal(${u.id})" title="Editar plano, vencimento, status, limite e dados da assinatura">
          <i class="fa-solid fa-pen-to-square"></i> Editar
        </button>
        <button class="btn btn-emerald btn-xs" onclick="renewUser(${u.id}, 30, '${escapeHtml(targetPlan)}')" title="Adicionar +30 dias rapidamente">+30d</button>
        <button class="btn btn-outline btn-xs" onclick="toggleUserActive(${u.id}, ${u.is_active ? 0 : 1})">
          ${u.is_active ? 'Bloquear' : 'Liberar'}
        </button>
      </td>
    </tr>`;
  }).join('') : '<tr><td colspan="8" class="text-muted">Nenhuma conta encontrada nesse filtro.</td></tr>';
}

const ADMIN_PLAN_DEFAULT_LIMITS = {
  trial: 25,
  starter: 500,
  pro: 2000,
  enterprise: 0,
};

function openAdminEditUserModal(uid) {
  const u = (_adminUsersCache || []).find(x => Number(x.id) === Number(uid));
  if (!u) return;
  const modal = document.getElementById('modal-admin-edit-user');
  if (!modal) return;

  const normPlan = u.plan === 'agency' ? 'enterprise' : (u.plan || 'trial');
  document.getElementById('adm-edit-id').value = u.id;
  document.getElementById('adm-edit-user-id-badge').textContent = `#${u.id}`;
  document.getElementById('adm-edit-user-meta').textContent = `Cadastrado em ${(u.created_at || '').slice(0, 10) || '-'} · Último acesso: ${(u.last_login_at || 'nunca').slice(0, 16).replace('T', ' ')}`;
  document.getElementById('adm-edit-plan').value = ['trial', 'starter', 'pro', 'enterprise'].includes(normPlan) ? normPlan : 'starter';
  document.getElementById('adm-edit-sub-status').value = u.subscription_status || 'active';
  document.getElementById('adm-edit-expires').value = u.plan_expires_at ? String(u.plan_expires_at).slice(0, 10) : '';
  document.getElementById('adm-edit-max-leads').value = u.max_leads !== undefined && u.max_leads !== null ? u.max_leads : (ADMIN_PLAN_DEFAULT_LIMITS[normPlan] ?? 500);
  document.getElementById('adm-edit-leads-usage').textContent = `Leads salvos hoje nesta conta: ${u.leads_count || 0}`;

  document.getElementById('adm-edit-name').value = u.name || '';
  document.getElementById('adm-edit-company').value = u.company_name || '';
  document.getElementById('adm-edit-email').value = u.email || '';
  document.getElementById('adm-edit-password').value = '';
  document.getElementById('adm-edit-role').value = u.role || 'user';
  document.getElementById('adm-edit-active').value = u.is_active ? '1' : '0';

  const delBtn = document.getElementById('btn-adm-delete-user');
  if (delBtn) {
    const isSelf = window.CURRENT_USER && Number(window.CURRENT_USER.id) === Number(u.id);
    delBtn.classList.toggle('hidden', isSelf);
  }

  modal.classList.remove('hidden');
}

function closeAdminEditUserModal() {
  document.getElementById('modal-admin-edit-user')?.classList.add('hidden');
}

function onAdminEditPlanChange() {
  const plan = document.getElementById('adm-edit-plan')?.value || 'starter';
  const maxEl = document.getElementById('adm-edit-max-leads');
  const statusEl = document.getElementById('adm-edit-sub-status');
  if (maxEl && plan in ADMIN_PLAN_DEFAULT_LIMITS) {
    maxEl.value = ADMIN_PLAN_DEFAULT_LIMITS[plan];
  }
  if (statusEl) {
    statusEl.value = plan === 'trial' ? 'trial' : 'active';
  }
}

function adminEditShiftExpiry(days) {
  const expEl = document.getElementById('adm-edit-expires');
  if (!expEl) return;
  const now = new Date();
  let base = now;
  if (expEl.value) {
    const parsed = new Date(`${expEl.value}T12:00:00`);
    if (!Number.isNaN(parsed.getTime()) && parsed > now) {
      base = parsed;
    }
  }
  base.setDate(base.getDate() + Number(days || 30));
  const yyyy = base.getFullYear();
  const mm = String(base.getMonth() + 1).padStart(2, '0');
  const dd = String(base.getDate()).padStart(2, '0');
  expEl.value = `${yyyy}-${mm}-${dd}`;
  const statusEl = document.getElementById('adm-edit-sub-status');
  if (statusEl && (statusEl.value === 'expired' || statusEl.value === 'suspended' || statusEl.value === 'canceled')) {
    statusEl.value = 'active';
  }
}

function adminEditClearExpiry() {
  const expEl = document.getElementById('adm-edit-expires');
  if (expEl) expEl.value = '';
  const statusEl = document.getElementById('adm-edit-sub-status');
  if (statusEl) statusEl.value = 'active';
}

async function submitAdminEditUser(e) {
  e.preventDefault();
  const uid = document.getElementById('adm-edit-id')?.value;
  if (!uid) return;
  const btn = document.getElementById('btn-adm-save-user');
  if (btn) btn.disabled = true;
  try {
    const payload = {
      name: document.getElementById('adm-edit-name').value.trim(),
      company_name: document.getElementById('adm-edit-company').value.trim(),
      email: document.getElementById('adm-edit-email').value.trim(),
      role: document.getElementById('adm-edit-role').value,
      is_active: parseInt(document.getElementById('adm-edit-active').value, 10),
      plan: document.getElementById('adm-edit-plan').value,
      subscription_status: document.getElementById('adm-edit-sub-status').value,
      plan_expires_at: document.getElementById('adm-edit-expires').value.trim(),
      max_leads: parseInt(document.getElementById('adm-edit-max-leads').value || '0', 10),
    };
    const pwd = document.getElementById('adm-edit-password').value;
    if (pwd) payload.password = pwd;

    const res = await apiFetch(`/api/admin/users/${uid}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const d = await res.json();
    if (!res.ok || !d.success) {
      toast(d.error || 'Erro ao salvar assinatura.', 'error');
      return;
    }
    toast('Assinatura e dados da conta atualizados com sucesso!', 'success');
    closeAdminEditUserModal();
    loadAdminUsers();
    if (typeof loadAdminSaasOverview === 'function') loadAdminSaasOverview();
  } catch (err) {
    toast('Falha ao atualizar assinatura.', 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function deleteAdminUserFromModal() {
  const uid = document.getElementById('adm-edit-id')?.value;
  const email = document.getElementById('adm-edit-email')?.value || '';
  if (!uid) return;
  if (!confirm(`Tem certeza que deseja EXCLUIR DEFINITIVAMENTE a conta #${uid} (${email}) e todos os leads dela?\n\nEsta ação não pode ser desfeita.`)) return;
  try {
    const res = await apiFetch(`/api/admin/users/${uid}`, { method: 'DELETE' });
    const d = await res.json();
    if (!res.ok || !d.success) {
      toast(d.error || 'Não foi possível excluir a conta.', 'error');
      return;
    }
    toast('Conta de assinante excluída com sucesso.', 'info');
    closeAdminEditUserModal();
    loadAdminUsers();
    if (typeof loadAdminSaasOverview === 'function') loadAdminSaasOverview();
  } catch (err) {
    toast('Erro ao excluir conta.', 'error');
  }
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
    if (typeof loadAdminSaasOverview === 'function') loadAdminSaasOverview();
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
  if (typeof loadAdminSaasOverview === 'function') loadAdminSaasOverview();
}

// ==================== ACADEMIA / VIDEOAULAS ====================
function initAcademyControls() {
  document.getElementById('btn-academy-toggle-done')?.addEventListener('click', toggleCurrentAcademyLessonDone);
  document.getElementById('btn-academy-prev')?.addEventListener('click', () => stepAcademyLesson(-1));
  document.getElementById('btn-academy-next')?.addEventListener('click', () => stepAcademyLesson(1));
  document.getElementById('btn-academy-open-tab')?.addEventListener('click', () => {
    const lesson = (STATE.academyLessons || []).find(l => l.id === STATE.activeLessonId);
    if (lesson && lesson.target_tab) switchTab(lesson.target_tab);
  });
}

async function loadAcademyLessons() {
  try {
    const res = await apiFetch('/api/academy/lessons');
    if (!res.ok) return;
    const d = await res.json();
    STATE.academyLessons = d.lessons || [];
    updateAcademyProgressUI(d.completed_count || 0, d.total_count || STATE.academyLessons.length, d.percent || 0);
    renderAcademyModuleFilters();
    renderAcademyPlaylist();
    if (!STATE.activeLessonId && STATE.academyLessons.length) {
      const nextUnread = STATE.academyLessons.find(l => !l.completed) || STATE.academyLessons[0];
      selectAcademyLesson(nextUnread.id, false);
    } else if (STATE.activeLessonId) {
      selectAcademyLesson(STATE.activeLessonId, false);
    }
  } catch (e) {}
}

function updateAcademyProgressUI(done, total, pct) {
  const badge = document.getElementById('badge-academy-progress');
  const lbl = document.getElementById('academy-progress-label');
  const pctEl = document.getElementById('academy-progress-pct');
  const fill = document.getElementById('academy-progress-fill');
  if (badge) badge.textContent = `${done}/${total}`;
  if (lbl) lbl.textContent = `${done} de ${total} aulas concluídas`;
  if (pctEl) pctEl.textContent = `${pct}%`;
  if (fill) fill.style.width = `${pct}%`;
}

function renderAcademyModuleFilters() {
  const wrap = document.getElementById('academy-module-filters');
  if (!wrap) return;
  const mods = ['all', ...Array.from(new Set((STATE.academyLessons || []).map(l => l.module_name)))];
  wrap.innerHTML = mods.map(m => `
    <button type="button" class="seg-btn ${STATE.academyModuleFilter === m ? 'active' : ''}" onclick="setAcademyModuleFilter('${escapeHtml(m).replace(/'/g, "\\'")}')">
      ${m === 'all' ? 'Todos os Módulos' : escapeHtml(m)}
    </button>
  `).join('');
}

function setAcademyModuleFilter(mod) {
  STATE.academyModuleFilter = mod;
  renderAcademyModuleFilters();
  renderAcademyPlaylist();
}

function renderAcademyPlaylist() {
  const box = document.getElementById('academy-playlist');
  if (!box) return;
  const filtered = (STATE.academyLessons || []).filter(
    l => STATE.academyModuleFilter === 'all' || l.module_name === STATE.academyModuleFilter
  );
  if (!filtered.length) {
    box.innerHTML = '<p class="text-muted">Nenhuma videoaula publicada ainda.</p>';
    return;
  }
  const groups = [];
  filtered.forEach(l => {
    let g = groups.find(x => x.name === l.module_name);
    if (!g) { g = { name: l.module_name, items: [] }; groups.push(g); }
    g.items.push(l);
  });
  box.innerHTML = groups.map(g => `
    <div class="academy-module-group">
      <div class="academy-module-title">${escapeHtml(g.name)}</div>
      ${g.items.map(l => {
        const isActive = l.id === STATE.activeLessonId;
        const iconHtml = l.completed
          ? '<i class="fa-solid fa-check"></i>'
          : (isActive ? '<i class="fa-solid fa-play"></i>' : `${l.sort_order || '•'}`);
        return `
          <button type="button" class="academy-lesson-item ${isActive ? 'active' : ''} ${l.completed ? 'completed' : ''}" onclick="selectAcademyLesson(${l.id}, true)">
            <div class="academy-lesson-check">${iconHtml}</div>
            <div class="academy-lesson-info">
              <strong>${escapeHtml(l.title)}</strong>
              <span><i class="fa-regular fa-clock"></i> ${escapeHtml(l.duration_text || '01:00')}${l.completed ? ' · Concluída' : ''}</span>
            </div>
          </button>
        `;
      }).join('')}
    </div>
  `).join('');
}

function getEmbedUrl(url) {
  const raw = String(url || '').trim();
  const yt = raw.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([A-Za-z0-9_-]{6,})/);
  if (yt) return `https://www.youtube.com/embed/${yt[1]}?rel=0`;
  const vim = raw.match(/vimeo\.com\/(\d+)/);
  if (vim) return `https://player.vimeo.com/video/${vim[1]}`;
  return null;
}

function selectAcademyLesson(lessonId, autoplay = false) {
  const lessons = STATE.academyLessons || [];
  const lesson = lessons.find(l => l.id === lessonId);
  if (!lesson) return;
  const changed = STATE.activeLessonId !== lesson.id || autoplay;
  STATE.activeLessonId = lesson.id;

  document.getElementById('academy-current-module').textContent = lesson.module_name || 'Módulo';
  document.getElementById('academy-current-duration').textContent = lesson.duration_text || '01:00';
  document.getElementById('academy-current-title').textContent = lesson.title;
  document.getElementById('academy-current-desc').textContent = lesson.description || '';

  const doneBtn = document.getElementById('btn-academy-toggle-done');
  if (doneBtn) {
    doneBtn.className = lesson.completed ? 'btn btn-emerald btn-sm' : 'btn btn-primary btn-sm';
    doneBtn.innerHTML = lesson.completed
      ? '<i class="fa-solid fa-circle-check"></i> Aula Concluída (Desmarcar)'
      : '<i class="fa-regular fa-circle-check"></i> Marcar como Concluída';
  }
  const openTabBtn = document.getElementById('btn-academy-open-tab');
  if (openTabBtn) openTabBtn.classList.toggle('hidden', !lesson.target_tab);

  const stage = document.getElementById('academy-video-stage');
  if (stage && (changed || !stage.querySelector('video, iframe'))) {
    const embed = getEmbedUrl(lesson.video_url);
    if (embed) {
      stage.innerHTML = `<iframe src="${escapeHtml(embed)}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
    } else {
      stage.innerHTML = `<video id="academy-html5-video" src="${escapeHtml(lesson.video_url)}" controls playsinline preload="metadata"></video>`;
      const vid = document.getElementById('academy-html5-video');
      if (vid) {
        if (autoplay) vid.play().catch(() => {});
        vid.addEventListener('ended', async () => {
          if (!lesson.completed) await markAcademyLessonDone(lesson.id, true);
        });
      }
    }
  }
  renderAcademyPlaylist();
}

async function markAcademyLessonDone(lessonId, completed) {
  const res = await apiFetch(`/api/academy/lessons/${lessonId}/progress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed })
  });
  const d = await res.json();
  if (d.success) {
    const target = (STATE.academyLessons || []).find(l => l.id === lessonId);
    if (target) target.completed = completed;
    updateAcademyProgressUI(d.completed_count || 0, d.total_count || 0, d.percent || 0);
    selectAcademyLesson(lessonId, false);
    toast(completed ? 'Aula marcada como concluída!' : 'Aula marcada como pendente.', 'success');
  }
}

async function toggleCurrentAcademyLessonDone() {
  const lesson = (STATE.academyLessons || []).find(l => l.id === STATE.activeLessonId);
  if (!lesson) return;
  await markAcademyLessonDone(lesson.id, !lesson.completed);
}

function stepAcademyLesson(delta) {
  const lessons = STATE.academyLessons || [];
  const idx = lessons.findIndex(l => l.id === STATE.activeLessonId);
  if (idx < 0) return;
  const next = lessons[idx + delta];
  if (next) selectAcademyLesson(next.id, true);
}

let _adminAcademyLessons = [];
async function loadAdminAcademyLessons() {
  const tb = document.getElementById('admin-academy-tbody');
  if (!tb) return;
  const res = await apiFetch('/api/admin/academy/lessons');
  if (!res.ok) return;
  const d = await res.json();
  _adminAcademyLessons = d.lessons || [];
  tb.innerHTML = _adminAcademyLessons.length ? _adminAcademyLessons.map(l => `
    <tr>
      <td>#${l.sort_order || 0}</td>
      <td>${escapeHtml(l.module_name)}</td>
      <td><strong>${escapeHtml(l.title)}</strong><div class="text-muted" style="font-size:0.75rem">${escapeHtml(l.video_url)}</div></td>
      <td>${escapeHtml(l.duration_text || '-')}</td>
      <td>${l.is_published ? '<span class="status-pill" style="background:#d1fae5;color:#065f46">Publicada</span>' : '<span class="status-pill">Oculta</span>'}</td>
      <td style="white-space:nowrap;">
        <button type="button" class="btn btn-outline btn-xs" onclick="editAdminAcademyLesson(${l.id})"><i class="fa-solid fa-pen"></i></button>
        <button type="button" class="btn btn-outline btn-xs text-danger" onclick="deleteAdminAcademyLesson(${l.id})"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
  `).join('') : '<tr><td colspan="6" class="text-muted">Nenhuma aula cadastrada.</td></tr>';
}

function editAdminAcademyLesson(id) {
  const l = _adminAcademyLessons.find(x => x.id === id);
  if (!l) return;
  document.getElementById('adm-lesson-id').value = l.id;
  document.getElementById('adm-lesson-module').value = l.module_name || '';
  document.getElementById('adm-lesson-title').value = l.title || '';
  document.getElementById('adm-lesson-url').value = l.video_url || '';
  document.getElementById('adm-lesson-duration').value = l.duration_text || '01:00';
  document.getElementById('adm-lesson-order').value = l.sort_order || 1;
  document.getElementById('adm-lesson-tab').value = l.target_tab || '';
  document.getElementById('adm-lesson-desc').value = l.description || '';
  document.getElementById('adm-lesson-published').checked = Boolean(l.is_published);
  document.getElementById('admin-academy-card')?.scrollIntoView({ behavior: 'smooth' });
}

async function deleteAdminAcademyLesson(id) {
  if (!confirm('Excluir esta videoaula da Academia?')) return;
  const res = await apiFetch(`/api/admin/academy/lessons/${id}`, { method: 'DELETE' });
  const d = await res.json();
  if (d.success) {
    toast('Videoaula excluída.', 'info');
    loadAdminAcademyLessons();
    loadAcademyLessons();
  }
}

// ==================== ACADEMIA DE VENDAS PRO (CURSOS + VSLs) ====================
const SA_VALID_MODES = ['course', 'delivery', 'pricing', 'scripts', 'vsl'];
const SA_SIMULATOR_BENCHMARKS = {
  gmn: { setup: 497, mrr: 250 },
  nfc: { setup: 247, mrr: 0 },
  whatsapp: { setup: 497, mrr: 97 },
  cardapio: { setup: 597, mrr: 97 },
  biossite: { setup: 597, mrr: 67 },
  combo: { setup: 1197, mrr: 297 },
};

function initSalesAcademyControls() {
  document.getElementById('btn-sa-toggle-done')?.addEventListener('click', toggleSalesCourseDone);
  document.getElementById('btn-sa-find-leads')?.addEventListener('click', () => {
    const course = (STATE.salesAcademy.items || []).find(c => c.id === STATE.activeSalesCourseId);
    if (course && course.target_opp) {
      openCrmWithOpportunity(course.target_opp);
    } else {
      switchTab('tab-crm');
    }
  });
}

async function loadSalesAcademy() {
  try {
    const res = await apiFetch('/api/sales-academy');
    if (!res.ok) return;
    const d = await res.json();
    STATE.salesAcademy = d;
    if (!STATE.activeSalesCourseId && d.items && d.items.length) {
      STATE.activeSalesCourseId = d.items[0].id;
    }
    if (!STATE.activeSalesLessonNum) {
      STATE.activeSalesLessonNum = 1;
    }
    renderSalesAcademy();
  } catch (e) {}
}

function renderSalesLockedPlaceholder(thumbnailUrl, titleText) {
  return `
    <div style="position:relative; width:100%; height:100%; min-height:240px; display:flex; align-items:center; justify-content:center; flex-direction:column; padding:24px; text-align:center; background:linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,58,138,0.88)), url('${escapeHtml(thumbnailUrl || '')}') center/cover; border-radius:12px;">
      <div style="width:56px; height:56px; border-radius:999px; background:rgba(245,158,11,0.22); border:2px solid #f59e0b; color:#fde68a; display:grid; place-items:center; font-size:1.35rem; margin-bottom:10px;"><i class="fa-solid fa-lock"></i></div>
      <h3 style="color:#fff; margin:0 0 6px; font-size:1.05rem;">${escapeHtml(titleText || 'Material Exclusivo do Plano PRO')}</h3>
      <p style="color:#cbd5e1; max-width:440px; font-size:0.85rem; margin:0 0 14px;">Faça o upgrade para o Plano PRO para estudar todas as 30 aulas passo a passo, acessar os manuais técnicos de fornecedores e baixar as 6 VSLs prontas em MP4.</p>
      <button type="button" class="btn btn-primary btn-sm" style="background:linear-gradient(135deg,#f59e0b,#d97706); border:none; font-weight:800;" onclick="openUpgradeModal('Desbloqueie a Academia de Vendas completa (6 Cursos + 30 Aulas + 6 VSLs Prontas) com o Plano PRO!')">
        <i class="fa-solid fa-crown"></i> Desbloquear no Plano PRO
      </button>
    </div>`;
}

function renderSalesVideoElement(stageEl, url, posterUrl, unlocked, lockTitle) {
  if (!stageEl) return;
  if (!unlocked) {
    stageEl.innerHTML = renderSalesLockedPlaceholder(posterUrl, lockTitle);
    return;
  }
  const prevUrl = stageEl.dataset.renderedUrl || '';
  if (prevUrl === String(url || '') && stageEl.querySelector('video, iframe')) {
    return;
  }
  stageEl.dataset.renderedUrl = String(url || '');
  const embed = getEmbedUrl(url);
  if (embed) {
    stageEl.innerHTML = `<iframe src="${escapeHtml(embed)}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
  } else {
    stageEl.innerHTML = `<video src="${escapeHtml(url)}" controls playsinline preload="metadata" poster="${escapeHtml(posterUrl || '')}"></video>`;
  }
}

function renderSalesAcademy() {
  const sa = STATE.salesAcademy || { unlocked: false, items: [], completed_count: 0, total_count: 0, percent: 0 };
  const unlocked = Boolean(sa.unlocked);

  const upsellBanner = document.getElementById('sales-academy-upsell-banner');
  if (upsellBanner) upsellBanner.classList.toggle('hidden', unlocked);

  const badge = document.getElementById('badge-sales-pro');
  if (badge) {
    badge.textContent = unlocked ? `${sa.completed_count || 0}/${sa.total_count || 6}` : 'PRO';
    badge.style.background = unlocked ? '#10b981' : 'linear-gradient(135deg,#f59e0b,#d97706)';
  }

  const hdrRight = document.getElementById('sales-academy-header-right');
  if (hdrRight) {
    if (unlocked) {
      hdrRight.innerHTML = `
        <div class="academy-progress-box">
          <div class="academy-progress-meta">
            <strong>${sa.completed_count || 0} de ${sa.total_count || 0} formações concluídas</strong>
            <span>${sa.percent || 0}%</span>
          </div>
          <div class="academy-progress-track">
            <div class="academy-progress-fill" style="width:${sa.percent || 0}%"></div>
          </div>
        </div>`;
    } else {
      hdrRight.innerHTML = `
        <button type="button" class="btn btn-primary btn-sm" style="background:linear-gradient(135deg,#f59e0b,#d97706); border:none;" onclick="openUpgradeModal('Libere agora os 6 Cursos Completos (30 Aulas) e todas as VSLs prontas para baixar no Plano PRO!')">
          <i class="fa-solid fa-crown"></i> Liberar no Plano PRO
        </button>`;
    }
  }

  const grid = document.getElementById('sales-strategy-grid');
  if (grid) {
    grid.innerHTML = (sa.items || []).map(item => {
      const isActive = item.id === STATE.activeSalesCourseId;
      const lessonsCount = Array.isArray(item.lessons) && item.lessons.length ? item.lessons.length : 5;
      return `
        <button type="button" class="sales-strategy-card ${isActive ? 'active' : ''}" onclick="selectSalesAcademyCourse(${item.id})">
          <div class="sales-strategy-thumb">
            <img src="${escapeHtml(item.thumbnail_url || '/static/img/academy/gmn-hero.jpg')}" alt="${escapeHtml(item.badge_label)}">
            <span class="sa-lessons-chip"><i class="fa-solid fa-book-open"></i> ${lessonsCount} Aulas + VSL</span>
            ${!unlocked ? '<div class="sa-lock-overlay"><i class="fa-solid fa-lock"></i></div>' : (item.completed ? '<span class="sa-done-chip"><i class="fa-solid fa-check"></i> Concluído</span>' : '')}
          </div>
          <div class="sales-strategy-body">
            <span class="academy-mod-pill">${escapeHtml(item.badge_label)}</span>
            <strong>${escapeHtml(item.title)}</strong>
            <div class="sales-strategy-sub">${escapeHtml(item.subtitle || '')}</div>
            <div class="sales-strategy-ticket"><i class="fa-solid fa-sack-dollar"></i> ${escapeHtml(item.ticket_range || '')}</div>
          </div>
        </button>`;
    }).join('');
  }

  const wsCard = document.getElementById('sales-workspace-card');
  const course = (sa.items || []).find(c => c.id === STATE.activeSalesCourseId);
  if (!wsCard || !course) return;
  wsCard.classList.remove('hidden');

  const mode = SA_VALID_MODES.includes(STATE.salesAcademyMode) ? STATE.salesAcademyMode : 'course';
  STATE.salesAcademyMode = mode;

  document.getElementById('sa-active-badge').textContent = course.badge_label;
  const durEl = document.getElementById('sa-active-duration');
  if (durEl) durEl.innerHTML = `<i class="fa-regular fa-clock"></i> ${escapeHtml(course.course_duration || '5 Aulas • ~45 min')}`;
  document.getElementById('sa-active-ticket').innerHTML = `<i class="fa-solid fa-sack-dollar"></i> ${escapeHtml(course.ticket_range || '')}`;
  document.getElementById('sa-active-title').textContent = mode === 'vsl' ? (course.vsl_title || course.title) : course.title;
  document.getElementById('sa-active-subtitle').textContent = mode === 'vsl'
    ? 'Vídeo VSL White-Label (sem marca MapaLeads) pronto para você baixar em MP4 e enviar para empresários no WhatsApp, Reels ou Anúncios.'
    : (course.subtitle || '');

  const lessons = Array.isArray(course.lessons) ? course.lessons : [];
  const countBadge = document.getElementById('sa-tab-lessons-count');
  if (countBadge) countBadge.textContent = `${lessons.length || 5} Aulas`;

  document.querySelectorAll('#sa-mode-tabs [data-sa-mode]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.saMode === mode);
  });

  SA_VALID_MODES.forEach(m => {
    const pane = document.getElementById(`sa-pane-${m}`);
    if (pane) pane.classList.toggle('hidden', m !== mode);
  });

  const doneBtn = document.getElementById('btn-sa-toggle-done');
  if (doneBtn) {
    doneBtn.classList.toggle('hidden', !unlocked);
    doneBtn.className = course.completed ? 'btn btn-emerald btn-sm' : 'btn btn-primary btn-sm';
    doneBtn.innerHTML = course.completed
      ? '<i class="fa-solid fa-circle-check"></i> Curso Concluído (Desmarcar)'
      : '<i class="fa-regular fa-circle-check"></i> Marcar Curso Concluído';
  }

  for (const dlId of ['btn-sa-download-vsl', 'btn-sa-download-vsl-pane']) {
    const dlBtn = document.getElementById(dlId);
    if (!dlBtn) continue;
    if (unlocked && course.download_url) {
      dlBtn.classList.remove('hidden');
      dlBtn.href = course.download_url;
      dlBtn.setAttribute('download', `${course.slug || 'vsl'}.mp4`);
    } else {
      dlBtn.href = '#';
      dlBtn.onclick = (ev) => {
        if (!unlocked) {
          ev.preventDefault();
          openUpgradeModal('O download das VSLs White-Label em MP4 é exclusivo do Plano PRO!');
        }
      };
    }
  }

  // Render Pane 1: Video + 5 Lessons Playlist + Active Lesson Reader
  renderSalesVideoElement(
    document.getElementById('sa-video-stage'),
    course.course_video_url,
    course.thumbnail_url,
    unlocked,
    'Vídeo Resumo & 5 Aulas Práticas Exclusivas do Plano PRO'
  );
  renderSalesCourseLessons(course, unlocked);

  // Render Pane 2: Technical Delivery Manual + Interactive Checklist
  const deliveryPre = document.getElementById('sa-delivery-pre');
  if (deliveryPre) {
    deliveryPre.textContent = unlocked
      ? (course.delivery_guide || '')
      : 'Manual Técnico de Produção, Fornecedores e Entrega Passo a Passo liberado no Plano PRO.\nFaça o upgrade para ver exatamente onde comprar os insumos, quais ferramentas gratuitas usar e como entregar o serviço em 24h a 48h.';
  }
  renderSalesCourseChecklist(course);

  // Render Pane 3: Pricing Tiers + Simulator
  renderSalesCoursePricing(course);
  updateSalesProfitSimulator();

  // Render Pane 4: 4 Scripts
  const lockedMsg = 'Conteúdo completo liberado no Plano PRO.\nAssine o Plano PRO para copiar todos os scripts validados de abordagem, follow-up, quebra de objeções e proposta comercial.';
  const setScriptText = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = unlocked ? (text || '') : lockedMsg;
  };
  setScriptText('sa-script-approach', course.script_approach);
  setScriptText('sa-script-followup', course.script_followup);
  setScriptText('sa-script-objections', course.script_objections);
  setScriptText('sa-script-proposal', course.proposal_script);

  // Render Pane 5: VSL Player
  if (mode === 'vsl') {
    renderSalesVideoElement(
      document.getElementById('sa-vsl-stage'),
      course.vsl_video_url,
      course.thumbnail_url,
      unlocked,
      'VSL White-Label Pronta para Baixar (.MP4) — Exclusivo PRO'
    );
  }
}

function renderSalesCourseLessons(course, unlocked) {
  const lessons = Array.isArray(course.lessons) && course.lessons.length ? course.lessons : [];
  const playlistEl = document.getElementById('sa-lessons-playlist');
  if (!playlistEl) return;

  if (!lessons.length) {
    playlistEl.innerHTML = '<div class="text-muted" style="font-size:0.82rem;">Nenhuma aula cadastrada neste módulo.</div>';
    return;
  }

  let activeLesson = lessons.find(l => Number(l.num) === Number(STATE.activeSalesLessonNum));
  if (!activeLesson) {
    activeLesson = lessons[0];
    STATE.activeSalesLessonNum = activeLesson.num || 1;
  }

  playlistEl.innerHTML = lessons.map((l, idx) => {
    const num = l.num || (idx + 1);
    const isAct = Number(num) === Number(STATE.activeSalesLessonNum);
    return `
      <button type="button" class="sa-lesson-item ${isAct ? 'active' : ''}" onclick="selectSalesCourseLesson(${num})">
        <div class="sa-lesson-num">${num}</div>
        <div class="sa-lesson-meta">
          <small>${escapeHtml(l.module || `Módulo ${num}`)}</small>
          <strong>${escapeHtml(l.title || `Aula ${num}`)}</strong>
          <span><i class="fa-regular fa-clock"></i> ${escapeHtml(l.duration || '10 min')} ${!unlocked ? '· <i class="fa-solid fa-lock text-amber"></i> PRO' : ''}</span>
        </div>
      </button>`;
  }).join('');

  const modEl = document.getElementById('sa-lesson-module');
  const durEl = document.getElementById('sa-lesson-duration');
  const titleEl = document.getElementById('sa-lesson-title');
  const sumEl = document.getElementById('sa-lesson-summary');
  const bodyEl = document.getElementById('sa-lesson-body');
  const stepEl = document.getElementById('sa-lesson-step-indicator');
  const prevBtn = document.getElementById('btn-sa-prev-lesson');
  const nextBtn = document.getElementById('btn-sa-next-lesson');

  const activeIdx = lessons.findIndex(l => Number(l.num) === Number(activeLesson.num));
  if (modEl) modEl.textContent = activeLesson.module || `Módulo ${activeLesson.num}`;
  if (durEl) durEl.innerHTML = `<i class="fa-regular fa-clock"></i> ${escapeHtml(activeLesson.duration || '10 min')} de estudo prático`;
  if (titleEl) titleEl.textContent = `Aula 0${activeLesson.num} — ${activeLesson.title || ''}`;
  if (sumEl) sumEl.textContent = activeLesson.summary || '';
  if (stepEl) stepEl.textContent = `Aula ${activeIdx + 1} de ${lessons.length}`;
  if (prevBtn) prevBtn.disabled = activeIdx <= 0;
  if (nextBtn) nextBtn.disabled = activeIdx >= lessons.length - 1;

  if (bodyEl) {
    if (!unlocked) {
      bodyEl.innerHTML = renderSalesLockedPlaceholder(course.thumbnail_url, `Aula 0${activeLesson.num}: ${activeLesson.title}`);
    } else {
      bodyEl.innerHTML = activeLesson.content_html || `<p>${escapeHtml(activeLesson.summary || '')}</p>`;
    }
  }
}

function selectSalesCourseLesson(num) {
  STATE.activeSalesLessonNum = Number(num) || 1;
  const course = (STATE.salesAcademy?.items || []).find(c => c.id === STATE.activeSalesCourseId);
  if (course) {
    renderSalesCourseLessons(course, Boolean(STATE.salesAcademy?.unlocked));
    document.getElementById('sa-lesson-reader')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function stepSalesCourseLesson(delta) {
  const course = (STATE.salesAcademy?.items || []).find(c => c.id === STATE.activeSalesCourseId);
  if (!course || !Array.isArray(course.lessons) || !course.lessons.length) return;
  const idx = course.lessons.findIndex(l => Number(l.num) === Number(STATE.activeSalesLessonNum));
  const nextLesson = course.lessons[idx + delta];
  if (nextLesson) {
    selectSalesCourseLesson(nextLesson.num);
  }
}

function getSalesChecklistStorageKey(courseSlug) {
  const uid = window.CURRENT_USER?.id || 0;
  return `ml_sa_check_${uid}_${courseSlug || 'default'}`;
}

function renderSalesCourseChecklist(course) {
  const itemsEl = document.getElementById('sa-checklist-items');
  const progEl = document.getElementById('sa-checklist-progress-text');
  if (!itemsEl) return;
  const list = Array.isArray(course.checklist) ? course.checklist : [];
  const key = getSalesChecklistStorageKey(course.slug);
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem(key) || '{}');
  } catch (e) {
    saved = {};
  }
  const doneCount = list.filter((_, idx) => Boolean(saved[idx])).length;
  if (progEl) progEl.textContent = `${doneCount} de ${list.length} etapas concluídas`;

  itemsEl.innerHTML = list.map((text, idx) => {
    const isChecked = Boolean(saved[idx]);
    return `
      <label class="sa-check-row ${isChecked ? 'checked' : ''}">
        <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="toggleSalesChecklistItem(${idx}, this.checked)">
        <span><strong>Etapa ${idx + 1}:</strong> ${escapeHtml(text)}</span>
      </label>`;
  }).join('');
}

function toggleSalesChecklistItem(idx, checked) {
  const course = (STATE.salesAcademy?.items || []).find(c => c.id === STATE.activeSalesCourseId);
  if (!course) return;
  const key = getSalesChecklistStorageKey(course.slug);
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem(key) || '{}');
  } catch (e) {
    saved = {};
  }
  saved[idx] = Boolean(checked);
  localStorage.setItem(key, JSON.stringify(saved));
  renderSalesCourseChecklist(course);
}

function resetSalesCourseChecklist() {
  const course = (STATE.salesAcademy?.items || []).find(c => c.id === STATE.activeSalesCourseId);
  if (!course) return;
  localStorage.removeItem(getSalesChecklistStorageKey(course.slug));
  renderSalesCourseChecklist(course);
  toast('Checklist reiniciado para um novo cliente!', 'info');
}

function renderSalesCoursePricing(course) {
  const grid = document.getElementById('sa-pricing-grid');
  if (!grid) return;
  const tiers = Array.isArray(course.pricing_tiers) ? course.pricing_tiers : [];
  grid.innerHTML = tiers.map((t, idx) => {
    const isFeatured = idx === 1 || String(t.badge || '').includes('★');
    const delivs = Array.isArray(t.deliverables) ? t.deliverables : [];
    return `
      <div class="sa-pricing-card ${isFeatured ? 'featured' : ''}">
        <span class="sa-pricing-badge">${escapeHtml(t.badge || 'Pacote')}</span>
        <h4>${escapeHtml(t.name || '')}</h4>
        <div class="sa-price-big">${escapeHtml(t.setup_price || '')}</div>
        <div class="sa-price-mrr"><i class="fa-solid fa-repeat"></i> ${escapeHtml(t.monthly_price || 'Venda única')}</div>
        <div class="sa-price-meta-box">
          <span><strong>Custo de Produção:</strong> ${escapeHtml(t.cost || 'R$ 0,00')}</span>
          <span><strong>Margem Estimada:</strong> ${escapeHtml(t.profit_margin || '100%')}</span>
        </div>
        <ul class="sa-price-list">
          ${delivs.map(d => `<li>${escapeHtml(d)}</li>`).join('')}
        </ul>
      </div>`;
  }).join('');
}

function updateSalesProfitSimulator() {
  const course = (STATE.salesAcademy?.items || []).find(c => c.id === STATE.activeSalesCourseId);
  const slider = document.getElementById('sa-sim-clients');
  if (!slider) return;
  const clientsPerMonth = Math.max(1, parseInt(slider.value || '5', 10));
  const bench = SA_SIMULATOR_BENCHMARKS[course?.strategy_key] || { setup: 497, mrr: 197 };

  const monthlySetup = clientsPerMonth * bench.setup;
  const newMrrPerMonth = clientsPerMonth * bench.mrr;
  // In 6 months: 6 months of setup + cumulative MRR (1 + 2 + 3 + 4 + 5 + 6 = 21 client-months of MRR)
  const total6Months = (monthlySetup * 6) + (newMrrPerMonth * 21);

  const fmtBRL = (val) => 'R$ ' + Number(val || 0).toLocaleString('pt-BR');
  const lbl = document.getElementById('sa-sim-clients-label');
  if (lbl) lbl.textContent = `${clientsPerMonth} ${clientsPerMonth === 1 ? 'cliente/mês' : 'clientes/mês'}`;
  const setupEl = document.getElementById('sa-sim-setup-total');
  if (setupEl) setupEl.textContent = `${fmtBRL(monthlySetup)}/mês`;
  const mrrEl = document.getElementById('sa-sim-mrr-total');
  if (mrrEl) mrrEl.textContent = bench.mrr > 0 ? `+ ${fmtBRL(newMrrPerMonth)}/mês` : 'Venda à Vista (800% Lucro)';
  const sixEl = document.getElementById('sa-sim-6m-total');
  if (sixEl) sixEl.textContent = fmtBRL(total6Months);
}

function selectSalesAcademyCourse(courseId) {
  STATE.activeSalesCourseId = courseId;
  STATE.activeSalesLessonNum = 1;
  const stage1 = document.getElementById('sa-video-stage');
  if (stage1) stage1.dataset.renderedUrl = '';
  const stage2 = document.getElementById('sa-vsl-stage');
  if (stage2) stage2.dataset.renderedUrl = '';
  renderSalesAcademy();
}

function setSalesAcademyMode(mode) {
  STATE.salesAcademyMode = SA_VALID_MODES.includes(mode) ? mode : 'course';
  renderSalesAcademy();
}

function copySalesScript(elId) {
  if (!STATE.salesAcademy?.unlocked) {
    openUpgradeModal('Os scripts completos, manuais técnicos e propostas são exclusivos do Plano PRO!');
    return;
  }
  const el = document.getElementById(elId);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent || '');
  toast('Conteúdo copiado para a área de transferência!', 'success');
}

async function toggleSalesCourseDone() {
  const course = (STATE.salesAcademy.items || []).find(c => c.id === STATE.activeSalesCourseId);
  if (!course) return;
  const nextVal = !course.completed;
  const res = await apiFetch(`/api/sales-academy/${course.id}/progress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: nextVal }),
  });
  const d = await res.json();
  if (d.success) {
    course.completed = nextVal;
    STATE.salesAcademy.completed_count = d.completed_count;
    STATE.salesAcademy.total_count = d.total_count;
    STATE.salesAcademy.percent = d.percent;
    renderSalesAcademy();
    toast(nextVal ? 'Formação marcada como concluída!' : 'Formação marcada como pendente.', 'success');
  }
}

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ==================== P0.1 & P0.4 — ONBOARDING INTELIGENTE & ATIVAÇÃO ====================
let _onboardingState = null;

const ONBOARDING_STEPS_CONFIG = [
  { key: 'step_welcome', title: '1. Conhecer a Plataforma', desc: 'Entenda a jornada: Buscar → Analisar → Abordar → Fechar', actionLabel: 'Concluir Boas-vindas', actionFn: 'completeWelcomeOnboardingStep()' },
  { key: 'step_first_search', title: '2. Fazer 1ª Busca no Google', desc: 'Extraia empresas reais com telefone na sua cidade ou rua', actionLabel: 'Ir para Busca', actionFn: "switchTab('tab-search')" },
  { key: 'step_view_lead', title: '3. Analisar Empresa & Score', desc: 'Abra a ficha de um lead para ver o Lead Score e o Copiloto IA', actionLabel: 'Abrir Leads / CRM', actionFn: "switchTab('tab-crm')" },
  { key: 'step_crm', title: '4. Organizar no Funil CRM', desc: 'Mova uma oportunidade no Kanban ou agende um Follow-up', actionLabel: 'Abrir CRM Kanban', actionFn: "switchTab('tab-crm')" },
  { key: 'step_first_contact', title: '5. Iniciar 1º Contato', desc: 'Envie um Quebra-Gelo pelo WhatsApp Web, QR ou API Oficial', actionLabel: 'Enviar 1ª Mensagem', actionFn: 'openFirstLeadForContact()' },
];

async function loadOnboardingAndActivations() {
  try {
    const res = await apiFetch('/api/onboarding');
    if (!res.ok) return;
    const d = await res.json();
    if (d.onboarding) {
      _onboardingState = d.onboarding;
      renderOnboardingChecklist(d.onboarding);
    }
    renderActivationSmartBanner(d.activations || []);
  } catch (e) {}
}

function renderOnboardingChecklist(ob) {
  const card = document.getElementById('onboarding-checklist-card');
  if (!card) return;
  if (ob.dismissed) {
    card.classList.add('hidden');
    return;
  }
  card.classList.remove('hidden');

  const pill = document.getElementById('onboarding-progress-pill');
  const bar = document.getElementById('onboarding-progress-bar');
  if (pill) pill.textContent = `${ob.steps_completed || 0}/${ob.total_steps || 5} concluídos (${ob.percent || 0}%)`;
  if (bar) bar.style.width = `${ob.percent || 0}%`;

  const grid = document.getElementById('onboarding-steps-grid');
  if (!grid) return;
  grid.innerHTML = ONBOARDING_STEPS_CONFIG.map(s => {
    const done = Boolean(ob[s.key]);
    return `
      <div style="padding:11px 13px; border-radius:12px; border:1px solid ${done ? '#10b981' : 'var(--border)'}; background:${done ? 'rgba(16,185,129,0.08)' : 'var(--card-bg, #fff)'}; display:flex; flex-direction:column; justify-content:space-between; gap:8px;">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; margin-bottom:4px;">
            <strong style="font-size:0.83rem;">${escapeHtml(s.title)}</strong>
            ${done ? '<span class="status-pill" style="background:#d1fae5;color:#065f46;font-size:0.7rem;"><i class="fa-solid fa-check"></i> Feito</span>' : '<span class="status-pill" style="font-size:0.7rem;">Pendente</span>'}
          </div>
          <p class="text-muted" style="font-size:0.76rem; margin:0; line-height:1.35;">${escapeHtml(s.desc)}</p>
        </div>
        <button type="button" class="btn ${done ? 'btn-outline' : 'btn-primary'} btn-xs" onclick="${s.actionFn}">
          ${done ? 'Revisar' : escapeHtml(s.actionLabel)}
        </button>
      </div>
    `;
  }).join('');
}

function renderActivationSmartBanner(list) {
  const banner = document.getElementById('activation-smart-banner');
  if (!banner) return;
  if (!list || !list.length) {
    banner.classList.add('hidden');
    return;
  }
  const first = list[0];
  banner.classList.remove('hidden');
  banner.innerHTML = `
    <div style="display:flex; align-items:center; gap:10px; flex:1; min-width:220px;">
      <i class="fa-solid fa-lightbulb text-amber" style="font-size:1.15rem;"></i>
      <div style="font-size:0.84rem;">
        <strong>${escapeHtml(first.title)}:</strong> ${escapeHtml(first.message)}
      </div>
    </div>
    <button type="button" class="btn btn-outline btn-xs" onclick="document.getElementById('activation-smart-banner').classList.add('hidden')">Entendi</button>
  `;
}

async function completeWelcomeOnboardingStep() {
  const res = await apiFetch('/api/onboarding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ step_welcome: 1 }),
  });
  const d = await res.json();
  if (d.onboarding) {
    _onboardingState = d.onboarding;
    renderOnboardingChecklist(d.onboarding);
    toast('Passo 1 concluído! Agora vamos para sua primeira busca no Google Maps.', 'success');
    switchTab('tab-search');
  }
}

function openFirstLeadForContact() {
  if (STATE.leads && STATE.leads.length) {
    openLeadDrawer(STATE.leads[0]);
  } else {
    switchTab('tab-search');
    toast('Faça uma busca primeiro para selecionar uma empresa.', 'info');
  }
}

function continueOnboardingNextStep() {
  const ob = _onboardingState || {};
  if (!ob.step_welcome) return completeWelcomeOnboardingStep();
  if (!ob.step_first_search) { switchTab('tab-search'); document.getElementById('search-location-input')?.focus(); return; }
  if (!ob.step_view_lead) return openFirstLeadForContact();
  if (!ob.step_crm) { switchTab('tab-crm'); return; }
  return openFirstLeadForContact();
}

async function restartOnboardingTutorial() {
  const res = await apiFetch('/api/onboarding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reset: true, dismissed: 0 }),
  });
  const d = await res.json();
  if (d.onboarding) {
    _onboardingState = d.onboarding;
    renderOnboardingChecklist(d.onboarding);
    toast('Tutorial reiniciado!', 'info');
  }
}

async function dismissOnboardingChecklist() {
  await apiFetch('/api/onboarding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dismissed: 1 }),
  });
  document.getElementById('onboarding-checklist-card')?.classList.add('hidden');
}

async function reopenOnboardingChecklist() {
  switchTab('tab-dashboard');
  const res = await apiFetch('/api/onboarding', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dismissed: 0 }),
  });
  const d = await res.json();
  if (d.onboarding) {
    _onboardingState = d.onboarding;
    renderOnboardingChecklist(d.onboarding);
    document.getElementById('onboarding-checklist-card')?.scrollIntoView({ behavior: 'smooth' });
  }
}

// ==================== P1.4 — DASHBOARD DE RESULTADOS DO ASSINANTE ====================
async function loadMyResultsDashboard() {
  const period = document.getElementById('my-results-period')?.value || '30d';
  try {
    const res = await apiFetch(`/api/my-results?period=${encodeURIComponent(period)}`);
    if (!res.ok) return;
    const d = await res.json();
    const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    setEl('res-leads-found', d.leads_found ?? 0);
    setEl('res-leads-saved', d.leads_saved ?? 0);
    setEl('res-in-crm', d.companies_in_crm ?? 0);
    setEl('res-contacts-made', d.contacts_made ?? 0);
    setEl('res-in-progress', d.opportunities_in_progress ?? 0);
    setEl('res-closed-sales', d.closed_sales ?? 0);
    setEl('res-conv-rate', `${d.conversion_rate_pct ?? 0}%`);
    setEl('res-closed-rev', formatBRL(d.closed_revenue_brl || 0));

    const bar = document.getElementById('my-results-timeline-bar');
    if (bar) {
      const tl = d.timeline || [];
      bar.innerHTML = `<strong>Resumo do período:</strong> ${d.searches_run || 0} busca(s) executadas · Taxa de resposta: <strong>${d.reply_rate_pct || 0}%</strong> · Taxa de fechamento sobre contatos: <strong>${d.conversion_rate_pct || 0}%</strong>`
        + (tl.length ? ` · Dias ativos no período: <strong>${tl.length}</strong>` : '');
    }
  } catch (e) {}
}

// ==================== P1.3 — FOLLOW-UPS & INTERAÇÕES NO CRM ====================
async function loadCrmFollowupSummary() {
  try {
    const res = await apiFetch('/api/crm/followups');
    if (!res.ok) return;
    const d = await res.json();
    const dueEl = document.getElementById('fu-cnt-due');
    const duePill = document.getElementById('btn-fu-due-pill');
    const dueCnt = Number(d.due_today_count ?? 0);
    if (dueEl) dueEl.textContent = dueCnt;
    if (duePill) duePill.classList.toggle('hidden', dueCnt <= 0);
  } catch (e) {}
}

function applyFollowupFilter(mode) {
  const sel = document.getElementById('crm-filter-followup');
  if (sel) {
    sel.value = mode;
    loadLeads();
  }
}

async function saveDrawerFollowup() {
  const l = STATE.selectedLead;
  if (!l) return;
  const next_followup_at = document.getElementById('drawer-followup-date')?.value || '';
  const followup_note = document.getElementById('drawer-followup-note')?.value || '';
  const res = await apiFetch(`/api/leads/${l.id}/followup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ next_followup_at, followup_note }),
  });
  const d = await res.json();
  if (d.success) {
    toast(next_followup_at ? `Follow-up agendado para ${next_followup_at}!` : 'Follow-up removido.', 'success');
    loadLeads();
    loadCrmFollowupSummary();
    loadLeadInteractions(l.id);
  }
}

async function loadLeadInteractions(leadId) {
  const box = document.getElementById('drawer-interactions-list');
  if (!box) return;
  try {
    const res = await apiFetch(`/api/leads/${leadId}/interactions`);
    if (!res.ok) return;
    const d = await res.json();
    const items = d.interactions || [];
    box.innerHTML = items.length ? items.map(it => `
      <div class="conv-msg" style="padding:6px 10px; font-size:0.78rem;">
        <div style="display:flex; justify-content:space-between; color:var(--text-muted); font-size:0.71rem;">
          <strong>${escapeHtml(it.kind)}</strong>
          <span>${escapeHtml((it.created_at || '').slice(0, 16).replace('T', ' '))}</span>
        </div>
        <div>${escapeHtml(it.summary)}</div>
      </div>
    `).join('') : '<div class="text-muted" style="font-size:0.78rem;">Nenhuma interação registrada ainda.</div>';
  } catch (e) {}
}

async function addDrawerManualInteraction() {
  const l = STATE.selectedLead;
  const inp = document.getElementById('drawer-new-interaction');
  if (!l || !inp || !inp.value.trim()) return;
  const summary = inp.value.trim();
  const res = await apiFetch(`/api/leads/${l.id}/interactions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kind: 'nota_comercial', summary }),
  });
  const d = await res.json();
  if (d.success) {
    inp.value = '';
    loadLeadInteractions(l.id);
    toast('Interação registrada no histórico!', 'success');
  }
}

// ==================== P1.2 — COPILOTO DE VENDAS COM IA ====================
async function runLeadAiCopilot(action = 'analyze') {
  const l = STATE.selectedLead;
  if (!l) return;
  const wrap = document.getElementById('drawer-ai-output-wrap');
  const out = document.getElementById('drawer-ai-output');
  const qLabel = document.getElementById('drawer-ai-quota-label');
  if (wrap) wrap.classList.remove('hidden');
  if (out) out.value = 'Analisando dados verificados da empresa...';
  try {
    const res = await apiFetch('/api/ai/copilot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_id: l.id, action }),
    });
    const d = await res.json();
    if (!d.success) {
      if (out) out.value = d.error || 'Erro ao executar Copiloto IA.';
      if (d.quota_exceeded) openUpgradeModal(d.error);
      return;
    }
    if (out) out.value = d.content || '';
    if (qLabel && d.quota) {
      qLabel.textContent = `Cota IA hoje: ${d.quota.used_today}/${d.quota.daily_limit}`;
    }
  } catch (e) {
    if (out) out.value = 'Falha ao consultar o Copiloto IA.';
  }
}

function useCopilotTextInWhatsApp() {
  const out = document.getElementById('drawer-ai-output')?.value || '';
  const msgBox = document.getElementById('drawer-message-text');
  if (!out || !msgBox) return;
  // Se houver texto entre aspas (sugestão de mensagem), extrai a 1ª mensagem sugerida; caso contrário copia tudo
  const quoted = out.match(/"([^"]{20,})"/);
  msgBox.value = quoted ? quoted[1] : out;
  msgBox.focus();
  toast('Texto carregado no campo de mensagem! Revise antes de enviar.', 'success');
}

function copyCopilotOutput() {
  const out = document.getElementById('drawer-ai-output')?.value || '';
  if (!out) return;
  navigator.clipboard.writeText(out);
  toast('Análise do Copiloto IA copiada!', 'success');
}

// ==================== P0.2, P0.3, P0.4 & FASE 1 — PAINEL ADMIN SAAS ====================
async function loadAdminSaasOverview() {
  const period = document.getElementById('adm-period-filter')?.value || '30d';
  const plan = document.getElementById('adm-plan-filter')?.value || 'all';
  try {
    const res = await apiFetch(`/api/admin/saas-overview?period=${encodeURIComponent(period)}&plan=${encodeURIComponent(plan)}`);
    if (!res.ok) return;
    const d = await res.json();
    if (!d.success) return;
    const k = d.kpis || {};
    const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
    setEl('adm-kpi-mrr', formatBRL(k.mrr_brl || 0));
    setEl('adm-kpi-rev', formatBRL(k.accumulated_revenue_brl || 0));
    setEl('adm-kpi-paid', k.paying_subscribers ?? 0);
    setEl('adm-kpi-conv', `${k.conversion_trial_to_paid_pct ?? 0}% conv.`);
    setEl('adm-kpi-trial', k.free_trial_users ?? 0);
    setEl('adm-kpi-new', `${k.new_signups_period ?? 0} novos`);
    setEl('adm-kpi-expired', k.overdue_expired_subscriptions ?? 0);
    setEl('adm-kpi-canceled', k.canceled_subscriptions ?? 0);
    setEl('adm-kpi-churn', `${k.churn_rate_pct ?? 0}%`);
    setEl('adm-kpi-clients', k.total_users ?? 0);
    setEl('adm-kpi-act-rate', `${k.activation_rate_pct ?? 0}%`);
    setEl('adm-kpi-leads', k.leads_total ?? 0);
    setEl('adm-kpi-searches', k.searches_total ?? 0);

    const distBar = document.getElementById('adm-plan-dist-bar');
    if (distBar && d.plan_distribution) {
      const pd = d.plan_distribution;
      distBar.innerHTML = `
        <span><strong>Distribuição por Plano:</strong> Trial: <strong>${pd.trial || 0}</strong> · Starter: <strong>${pd.starter || 0}</strong> · PRO: <strong>${pd.pro || 0}</strong> · Enterprise: <strong>${pd.enterprise || 0}</strong></span>
        <span>Usuários Ativos: <strong>${k.active_users || 0}</strong> · Inativos (7d+): <strong>${k.inactive_users_7d || 0}</strong> · Buscas no Período: <strong>${k.searches_period || 0}</strong></span>
      `;
    }

    const funnelGrid = document.getElementById('adm-analytics-funnel-grid');
    if (funnelGrid) {
      const eb = d.event_breakdown || {};
      const funnelKeys = [
        ['signup', 'Cadastros'],
        ['login', 'Logins'],
        ['onboarding_started', 'Onboarding Iniciado'],
        ['first_search', '1ª Busca Executada'],
        ['lead_viewed', 'Ficha Visualizada'],
        ['lead_sent_to_crm', 'Enviado ao CRM'],
        ['first_contact_started', '1º Contato Iniciado'],
        ['ai_copilot_used', 'Uso Copiloto IA'],
        ['payment_approved', 'Pagamento Aprovado'],
      ];
      funnelGrid.innerHTML = funnelKeys.map(([key, label]) => {
        const info = eb[key] || { events: 0, users: 0 };
        return `
          <div style="padding:10px 12px; border:1px solid var(--border); border-radius:10px;">
            <span class="text-muted" style="font-size:0.74rem; display:block;">${escapeHtml(label)}</span>
            <strong style="font-size:1.05rem;">${info.events}</strong>
            <small class="text-muted" style="font-size:0.72rem; display:block;">${info.users} usuário(s)</small>
          </div>
        `;
      }).join('');
    }
  } catch (e) {}
}

async function loadAdminActivationRules() {
  const tb = document.getElementById('admin-activation-rules-tbody');
  if (!tb) return;
  try {
    const res = await apiFetch('/api/admin/activation-rules');
    if (!res.ok) return;
    const d = await res.json();
    const rules = d.rules || [];
    tb.innerHTML = rules.map(r => `
      <tr>
        <td>
          <strong>${escapeHtml(r.name)}</strong>
          <div class="text-muted" style="font-size:0.73rem;"><code>${escapeHtml(r.trigger_key)}</code> · ${escapeHtml(r.description || '')}</div>
        </td>
        <td>
          <input type="text" id="act-tpl-${escapeHtml(r.trigger_key)}" value="${escapeHtml(r.message_template)}" style="width:100%; min-width:260px; font-size:0.8rem;">
        </td>
        <td><strong>${r.triggered_count || 0}</strong></td>
        <td>
          <label class="checkbox-inline">
            <input type="checkbox" id="act-en-${escapeHtml(r.trigger_key)}" ${r.enabled ? 'checked' : ''}>
            <span>Ativa</span>
          </label>
        </td>
        <td>
          <button type="button" class="btn btn-outline btn-xs" onclick="saveAdminActivationRule('${escapeHtml(r.trigger_key)}')">Salvar</button>
        </td>
      </tr>
    `).join('');
  } catch (e) {}
}

async function saveAdminActivationRule(triggerKey) {
  const tpl = document.getElementById(`act-tpl-${triggerKey}`)?.value || '';
  const en = Boolean(document.getElementById(`act-en-${triggerKey}`)?.checked);
  const res = await apiFetch(`/api/admin/activation-rules/${encodeURIComponent(triggerKey)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message_template: tpl, enabled: en }),
  });
  const d = await res.json();
  if (d.success) toast('Regra de ativação atualizada!', 'success');
}

async function loadAdminSystemHealthAndBackups() {
  const strip = document.getElementById('adm-system-health-strip');
  const tb = document.getElementById('admin-backups-tbody');
  if (!strip && !tb) return;
  try {
    const [hRes, bRes] = await Promise.all([
      apiFetch('/api/admin/system-health'),
      apiFetch('/api/admin/backups'),
    ]);
    if (hRes.ok && strip) {
      const h = await hRes.json();
      const mem = h.memory_mb || {};
      const waOk = h.wa_service && h.wa_service.status === 'ok';
      strip.innerHTML = `
        <span class="status-pill" style="background:#d1fae5;color:#065f46">SQLite: ${escapeHtml(h.sqlite_integrity || 'ok')} (${h.db_size_kb || 0} KB)</span>
        <span class="status-pill">Disco Livre: ${h.disk_free_gb || 0} GB / ${h.disk_total_gb || 0} GB</span>
        ${mem.MemTotal ? `<span class="status-pill">RAM Disp.: ${mem.MemAvailable || 0} MB / ${mem.MemTotal || 0} MB</span>` : ''}
        <span class="status-pill" style="background:${waOk ? '#d1fae5' : '#fef3c7'};color:${waOk ? '#065f46' : '#92400e'}">Microserviço WhatsApp: ${waOk ? 'Online (Container Isolado)' : 'Standby'}</span>
      `;
    }
    if (bRes.ok && tb) {
      const b = await bRes.json();
      renderAdminBackupsTable(b.backups || []);
    }
  } catch (e) {}
}

function renderAdminBackupsTable(items) {
  const tb = document.getElementById('admin-backups-tbody');
  if (!tb) return;
  tb.innerHTML = items.length ? items.map(b => `
    <tr>
      <td><code>${escapeHtml(b.filename)}</code></td>
      <td>${b.kind === 'full_bundle' ? 'Pacote Completo (DB + Sessões WA)' : 'Snapshot SQLite Diário'}</td>
      <td>${b.size_kb} KB</td>
      <td>${b.encrypted ? '<span class="status-pill" style="background:#d1fae5;color:#065f46">Criptografado (AES/HMAC)</span>' : '<span class="status-pill">Snapshot Local</span>'}</td>
      <td>${escapeHtml((b.modified_at || '').slice(0, 19).replace('T', ' '))}</td>
    </tr>
  `).join('') : '<tr><td colspan="5" class="text-muted">Nenhum backup encontrado.</td></tr>';
}

async function triggerAdminBackupNow() {
  const btn = document.getElementById('btn-admin-run-backup');
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Criando & Testando Restauração...'; }
  try {
    const res = await apiFetch('/api/admin/backups', { method: 'POST' });
    const d = await res.json();
    if (d.success) {
      const rv = d.restore_verified || {};
      toast(`Backup criado e restauração testada (${rv.users_count || 0} contas, ${rv.leads_count || 0} leads, integridade: ${rv.integrity})!`, 'success');
      renderAdminBackupsTable(d.backups || []);
    } else {
      toast(d.error || 'Erro ao gerar backup.', 'error');
    }
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i> Criar Backup + Testar Restauração Agora'; }
  }
}
