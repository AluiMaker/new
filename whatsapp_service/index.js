/**
 * MapaLeads PRO - Microserviço WhatsApp (Baileys)
 * Porta 5056. Sessão própria em ./auth_session (independente de outros apps).
 *
 * Endpoints:
 *   GET  /status          -> { state, qr (dataURL|null), user }
 *   POST /connect         -> inicia/gera QR
 *   POST /logout          -> desconecta e apaga sessão
 *   POST /check           -> { phone } => { exists, jid }
 *   POST /send            -> { phone, text } => { success, jid }
 * Mensagens recebidas são encaminhadas para o Flask:
 *   POST http://127.0.0.1:5055/api/wa/incoming { phone, text, name }
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
const FLASK_WEBHOOK = process.env.FLASK_WEBHOOK || 'http://127.0.0.1:5055/api/wa/incoming';
const AUTH_DIR = path.join(__dirname, 'auth_session');
const logger = pino({ level: 'silent' });

const app = express();
app.use(express.json({ limit: '2mb' }));

let sock = null;
let state = 'disconnected'; // disconnected | connecting | qrcode | connected
let qrDataUrl = null;
let user = null;
let initializing = false;
let reconnectTimer = null;

function cleanAuth() {
  try { fs.rmSync(AUTH_DIR, { recursive: true, force: true }); } catch (e) {}
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  } catch (e) {
    console.error('[WA] Falha ao encaminhar mensagem ao Flask:', e.message);
  }
}

async function initWhatsApp(forceNew = false) {
  if (initializing) return;
  initializing = true;
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }

  if (sock) {
    try { sock.ev.removeAllListeners(); sock.end(undefined); } catch (e) {}
    sock = null;
  }
  if (forceNew) cleanAuth();
  fs.mkdirSync(AUTH_DIR, { recursive: true });

  state = 'connecting';
  qrDataUrl = null;

  try {
    const { state: authState, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

    let version = [2, 3000, 1015901307];
    try {
      const res = await Promise.race([
        fetchLatestBaileysVersion(),
        new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 2500))
      ]);
      if (res && res.version) version = res.version;
    } catch (e) {}

    sock = makeWASocket({
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

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        state = 'qrcode';
        try { qrDataUrl = await qrcode.toDataURL(qr, { width: 300, margin: 1 }); } catch (e) {}
        console.log('[WA] Novo QR Code gerado.');
      }

      if (connection === 'open') {
        state = 'connected';
        qrDataUrl = null;
        const id = sock.user?.id || '';
        const num = id.split(':')[0].split('@')[0];
        user = { id, phone: num, name: sock.user?.name || sock.user?.verifiedName || 'WhatsApp' };
        console.log(`[WA] Conectado como ${user.name} (${user.phone}).`);
      }

      if (connection === 'close') {
        const code = lastDisconnect?.error?.output?.statusCode;
        const loggedOut = code === DisconnectReason.loggedOut || code === 401;
        console.log(`[WA] Conexão fechada (código ${code}).`);
        state = 'disconnected';
        user = null;
        qrDataUrl = null;
        initializing = false;
        if (loggedOut) {
          cleanAuth();
          return; // usuário precisa clicar em "Conectar" de novo
        }
        reconnectTimer = setTimeout(() => initWhatsApp(false), 3000);
      }
    });

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
      if (type !== 'notify') return;
      for (const m of messages) {
        try {
          if (!m.message || m.key.fromMe) continue;
          const jid = m.key.remoteJid || '';
          if (!jid.endsWith('@s.whatsapp.net')) continue; // ignora grupos/status
          const text =
            m.message.conversation ||
            m.message.extendedTextMessage?.text ||
            m.message.imageMessage?.caption ||
            m.message.buttonsResponseMessage?.selectedDisplayText ||
            '[mídia]';
          await forwardIncoming({ phone: jid.split('@')[0], text, name: m.pushName || '' });
        } catch (e) {}
      }
    });
  } catch (e) {
    console.error('[WA] Erro ao iniciar:', e.message);
    state = 'disconnected';
  } finally {
    initializing = false;
  }
}

// ==================== ROTAS ====================
app.get('/status', (req, res) => {
  res.json({ state, qr: qrDataUrl, user });
});

app.post('/connect', async (req, res) => {
  if (state === 'connected') return res.json({ success: true, state });
  await initWhatsApp(Boolean(req.body?.force));
  res.json({ success: true, state });
});

app.post('/logout', async (req, res) => {
  try { if (sock) await sock.logout(); } catch (e) {}
  try { if (sock) { sock.ev.removeAllListeners(); sock.end(undefined); } } catch (e) {}
  sock = null;
  cleanAuth();
  state = 'disconnected';
  user = null;
  qrDataUrl = null;
  res.json({ success: true });
});

app.post('/check', async (req, res) => {
  if (state !== 'connected' || !sock) return res.status(409).json({ success: false, error: 'WhatsApp não conectado' });
  try {
    const jid = toJid(req.body?.phone);
    const [r] = await sock.onWhatsApp(jid);
    res.json({ success: true, exists: Boolean(r?.exists), jid: r?.jid || jid });
  } catch (e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

app.post('/check-batch', async (req, res) => {
  if (state !== 'connected' || !sock) return res.status(409).json({ success: false, error: 'WhatsApp não conectado' });
  const phones = req.body?.phones || [];
  if (!Array.isArray(phones) || phones.length === 0) {
    return res.json({ success: true, results: {} });
  }
  const results = {};
  for (const phone of phones) {
    try {
      const jid = toJid(phone);
      const [r] = await sock.onWhatsApp(jid);
      results[phone] = { exists: Boolean(r?.exists), jid: r?.jid || jid };
    } catch (e) {
      results[phone] = { exists: false, error: e.message };
    }
  }
  res.json({ success: true, results });
});

app.post('/send', async (req, res) => {
  if (state !== 'connected' || !sock) return res.status(409).json({ success: false, error: 'WhatsApp não conectado' });
  const { phone, text } = req.body || {};
  if (!phone || !text) return res.status(400).json({ success: false, error: 'phone e text são obrigatórios' });
  try {
    const [r] = await sock.onWhatsApp(toJid(phone));
    if (!r?.exists) return res.json({ success: false, error: 'Número não possui WhatsApp', not_on_whatsapp: true });

    // Simula digitação humana proporcional ao tamanho do texto
    await sock.presenceSubscribe(r.jid).catch(() => {});
    await sock.sendPresenceUpdate('composing', r.jid).catch(() => {});
    await new Promise(ok => setTimeout(ok, Math.min(8000, 1500 + text.length * 25)));
    await sock.sendPresenceUpdate('paused', r.jid).catch(() => {});

    await sock.sendMessage(r.jid, { text });
    res.json({ success: true, jid: r.jid });
  } catch (e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[WA] Microserviço WhatsApp MapaLeads em http://127.0.0.1:${PORT}`);
  // Reconecta automaticamente se já houver sessão salva
  if (fs.existsSync(path.join(AUTH_DIR, 'creds.json'))) initWhatsApp(false);
});
