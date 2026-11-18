/**
 * MapaLeads PRO - Microserviço WhatsApp (Baileys Multi-Sessão)
 * Porta 5056. Sessões isoladas por usuário em WA_AUTH_ROOT/<session_id>.
 */
const express = require('express');
const qrcode = require('qrcode');
const pino = require('pino');
const path = require('path');
const fs = require('fs');
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  Browsers,
  makeCacheableSignalKeyStore
} = require('@whiskeysockets/baileys');

const PORT = process.env.WA_PORT || 5056;
const HOST = process.env.WA_HOST || '127.0.0.1';
const FLASK_WEBHOOK = process.env.FLASK_WEBHOOK || 'http://127.0.0.1:5055/api/wa/incoming';
const INTERNAL_TOKEN = process.env.WA_INTERNAL_TOKEN || 'mapaleads_internal_wa_2026';
const AUTH_ROOT = process.env.WA_AUTH_ROOT || path.join(__dirname, 'auth_sessions');
const logger = pino({ level: 'silent' });

const app = express();
app.use(express.json({ limit: '2mb' }));

// Mapa de sessões: sessionId -> { sock, state, qrDataUrl, user, initializing, reconnectTimer }
const sessions = new Map();

function getSessionId(req) {
  const raw = req.query?.session_id || req.body?.session_id || '1';
  return String(raw).replace(/[^a-zA-Z0-9_-]/g, '') || '1';
}

function getSession(sid) {
  if (!sessions.has(sid)) {
    sessions.set(sid, {
      sock: null,
      state: 'disconnected',
      qrDataUrl: null,
      user: null,
      initializing: false,
      reconnectTimer: null,
    });
  }
  return sessions.get(sid);
}

function authDirFor(sid) {
  return path.join(AUTH_ROOT, `user_${sid}`);
}

function cleanAuth(sid) {
  try { fs.rmSync(authDirFor(sid), { recursive: true, force: true }); } catch (e) {}
}

function toJid(phone) {
  let digits = String(phone || '').replace(/\D/g, '');
  if (!digits.startsWith('55') && (digits.length === 10 || digits.length === 11)) digits = '55' + digits;
  return digits + '@s.whatsapp.net';
}

async function forwardIncoming(payload) {
  try {
    await fetch(FLASK_WEBHOOK, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Internal-Token': INTERNAL_TOKEN,
      },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    console.error('[WA] Falha ao encaminhar mensagem ao Flask:', e.message);
  }
}

async function initWhatsApp(sid, forceNew = false) {
  const s = getSession(sid);
  if (s.initializing) return;
  s.initializing = true;
  if (s.reconnectTimer) { clearTimeout(s.reconnectTimer); s.reconnectTimer = null; }

  if (s.sock) {
    try { s.sock.ev.removeAllListeners(); s.sock.end(undefined); } catch (e) {}
    s.sock = null;
  }
  if (forceNew) cleanAuth(sid);
  const authDir = authDirFor(sid);
  fs.mkdirSync(authDir, { recursive: true });

  s.state = 'connecting';
  s.qrDataUrl = null;

  try {
    const { state: authState, saveCreds } = await useMultiFileAuthState(authDir);

    let version = [2, 3000, 1015901307];
    try {
      const res = await Promise.race([
        fetchLatestBaileysVersion(),
        new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 3000))
      ]);
      if (res && res.version) version = res.version;
    } catch (e) {}

    const sock = makeWASocket({
      version,
      auth: { creds: authState.creds, keys: makeCacheableSignalKeyStore(authState.keys, logger) },
      logger,
      printQRInTerminal: false,
      browser: Browsers.ubuntu('Chrome'),
      connectTimeoutMs: 60000,
      keepAliveIntervalMs: 25000,
      syncFullHistory: false,
      markOnlineOnConnect: false
    });
    s.sock = sock;

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        s.state = 'qrcode';
        try { s.qrDataUrl = await qrcode.toDataURL(qr, { width: 300, margin: 1 }); } catch (e) {}
        console.log(`[WA:${sid}] Novo QR Code gerado.`);
      }

      if (connection === 'open') {
        s.state = 'connected';
        s.qrDataUrl = null;
        s.initializing = false;
        const id = sock.user?.id || '';
        const num = id.split(':')[0].split('@')[0];
        s.user = { id, phone: num, name: sock.user?.name || sock.user?.verifiedName || 'WhatsApp' };
        console.log(`[WA:${sid}] Conectado como ${s.user.name} (${s.user.phone}).`);
      }

      if (connection === 'close') {
        const code = lastDisconnect?.error?.output?.statusCode;
        const loggedOut = code === DisconnectReason.loggedOut || code === 401;
        console.log(`[WA:${sid}] Conexão fechada (código ${code}).`);
        s.state = 'disconnected';
        s.user = null;
        s.qrDataUrl = null;
        s.initializing = false;
        if (loggedOut) {
          cleanAuth(sid);
          return;
        }
        s.reconnectTimer = setTimeout(() => initWhatsApp(sid, false), 3000);
      }
    });

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
      if (type !== 'notify') return;
      for (const m of messages) {
        try {
          if (!m.message || m.key.fromMe) continue;
          const jid = m.key.remoteJid || '';
          if (!jid.endsWith('@s.whatsapp.net')) continue;
          const text =
            m.message.conversation ||
            m.message.extendedTextMessage?.text ||
            m.message.imageMessage?.caption ||
            m.message.buttonsResponseMessage?.selectedDisplayText ||
            '[mídia]';
          await forwardIncoming({
            user_id: Number(sid) || 1,
            phone: jid.split('@')[0],
            text,
            name: m.pushName || ''
          });
        } catch (e) {}
      }
    });
  } catch (e) {
    console.error(`[WA:${sid}] Erro ao iniciar:`, e.message);
    s.state = 'disconnected';
    s.initializing = false;
  }
}

// ==================== ROTAS ====================
app.get('/status', (req, res) => {
  const sid = getSessionId(req);
  const s = getSession(sid);
  res.json({ state: s.state, qr: s.qrDataUrl, user: s.user, session_id: sid });
});

app.post('/connect', async (req, res) => {
  const sid = getSessionId(req);
  const s = getSession(sid);
  if (s.state === 'connected') return res.json({ success: true, state: s.state, user: s.user });
  initWhatsApp(sid, Boolean(req.body?.force));
  res.json({ success: true, state: s.state });
});

app.post('/logout', async (req, res) => {
  const sid = getSessionId(req);
  const s = getSession(sid);
  if (s.reconnectTimer) { clearTimeout(s.reconnectTimer); s.reconnectTimer = null; }
  try { if (s.sock) await s.sock.logout(); } catch (e) {}
  try { if (s.sock) { s.sock.ev.removeAllListeners(); s.sock.end(undefined); } } catch (e) {}
  s.sock = null;
  cleanAuth(sid);
  s.state = 'disconnected';
  s.user = null;
  s.qrDataUrl = null;
  s.initializing = false;
  res.json({ success: true });
});

app.post('/check', async (req, res) => {
  const sid = getSessionId(req);
  const s = getSession(sid);
  if (s.state !== 'connected' || !s.sock) return res.status(409).json({ success: false, error: 'WhatsApp não conectado' });
  try {
    const jid = toJid(req.body?.phone);
    const [r] = await s.sock.onWhatsApp(jid);
    res.json({ success: true, exists: Boolean(r?.exists), jid: r?.jid || jid });
  } catch (e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

app.post('/check-batch', async (req, res) => {
  const sid = getSessionId(req);
  const s = getSession(sid);
  if (s.state !== 'connected' || !s.sock) return res.status(409).json({ success: false, error: 'WhatsApp não conectado' });
  const phones = req.body?.phones || [];
  if (!Array.isArray(phones) || phones.length === 0) {
    return res.json({ success: true, results: {} });
  }
  const results = {};
  for (const phone of phones) {
    try {
      const jid = toJid(phone);
      const [r] = await s.sock.onWhatsApp(jid);
      results[phone] = { exists: Boolean(r?.exists), jid: r?.jid || jid };
    } catch (e) {
      results[phone] = { exists: false, error: e.message };
    }
  }
  res.json({ success: true, results });
});

app.post('/send', async (req, res) => {
  const sid = getSessionId(req);
  const s = getSession(sid);
  if (s.state !== 'connected' || !s.sock) return res.status(409).json({ success: false, error: 'WhatsApp não conectado' });
  const { phone, text } = req.body || {};
  if (!phone || !text) return res.status(400).json({ success: false, error: 'phone e text são obrigatórios' });
  try {
    const [r] = await s.sock.onWhatsApp(toJid(phone));
    if (!r?.exists) return res.json({ success: false, error: 'Número não possui WhatsApp', not_on_whatsapp: true });

    await s.sock.presenceSubscribe(r.jid).catch(() => {});
    await s.sock.sendPresenceUpdate('composing', r.jid).catch(() => {});
    await new Promise(ok => setTimeout(ok, Math.min(4000, 900 + text.length * 15)));
    await s.sock.sendPresenceUpdate('paused', r.jid).catch(() => {});

    await s.sock.sendMessage(r.jid, { text });
    res.json({ success: true, jid: r.jid });
  } catch (e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', active_sessions: sessions.size });
});

app.listen(PORT, HOST, () => {
  console.log(`[WA] Microserviço WhatsApp Multi-Sessão em http://${HOST}:${PORT}`);
  fs.mkdirSync(AUTH_ROOT, { recursive: true });
  try {
    for (const entry of fs.readdirSync(AUTH_ROOT)) {
      if (entry.startsWith('user_') && fs.existsSync(path.join(AUTH_ROOT, entry, 'creds.json'))) {
        const sid = entry.replace(/^user_/, '');
        initWhatsApp(sid, false);
      }
    }
  } catch (e) {}
});
