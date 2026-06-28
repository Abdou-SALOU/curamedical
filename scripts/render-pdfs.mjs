import { spawn } from 'node:child_process';
import { writeFile, mkdir, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

// ─────────────────────────────────────────────────────────────
//  Rend les PDF (ordonnance + compte rendu) en PNG pleine page.
//  Fenêtre PORTRAIT dédiée + deviceScaleFactor 1 : le visualiseur PDF
//  de Chrome ajuste la page à la largeur de la FENÊTRE (et ignore
//  l'émulation), donc il faut une vraie fenêtre au bon ratio A4.
// ─────────────────────────────────────────────────────────────

const ROOT = process.cwd();
const OUT_DIR = path.join(ROOT, 'soutenance', 'screenshots', 'curamedical-rapport');
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const UDD = 'C:\\tmp\\cura-pdf';
const PORT = 9500 + Math.floor(Math.random() * 200);
const API = 'http://127.0.0.1:8000';
const VW = 1240, VH = 1754;  // A4 ratio, deviceScaleFactor 1
const delay = ms => new Promise(r => setTimeout(r, ms));

async function token() {
  const r = await fetch(`${API}/api/token/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: 'medecin', password: 'medecinpassword' }) });
  return (await r.json()).access;
}
async function firstId(ep, t) {
  const r = await fetch(`${API}/api/${ep}/`, { headers: { Authorization: `Bearer ${t}` } });
  const d = await r.json();
  const list = Array.isArray(d) ? d : (d.results || []);
  return list[0]?.id;
}
async function download(url, t, dest) {
  const r = await fetch(url, { headers: { Authorization: `Bearer ${t}` } });
  const buf = Buffer.from(await r.arrayBuffer());
  await writeFile(dest, buf);
}

let ws, id = 1; const pend = new Map();
function send(m, p = {}) { const i = id++; ws.send(JSON.stringify({ id: i, method: m, params: p })); return new Promise((res, rej) => { pend.set(i, { res, rej }); setTimeout(() => { if (pend.has(i)) { pend.delete(i); rej(new Error('to ' + m)); } }, 20000); }); }
async function waitJson(u, t = 20000) { const s = Date.now(); while (Date.now() - s < t) { try { const r = await fetch(u); if (r.ok) return r.json(); } catch {} await delay(300); } throw new Error('to'); }

async function run() {
  await mkdir(OUT_DIR, { recursive: true });
  const t = await token();
  const pid = await firstId('prescriptions', t);
  const cid = await firstId('consultations', t);
  const jobs = [];
  if (pid) { const f = path.join(OUT_DIR, 'ordonnance-exemple.pdf'); await download(`${API}/api/prescriptions/${pid}/ordonnance-pdf/`, t, f); jobs.push({ name: '38-ordonnance-pdf', file: f }); }
  if (cid) { const f = path.join(OUT_DIR, 'compte-rendu-exemple.pdf'); await download(`${API}/api/consultations/${cid}/compte-rendu-pdf/`, t, f); jobs.push({ name: '39-compte-rendu-pdf', file: f }); }

  if (existsSync(UDD)) await rm(UDD, { recursive: true, force: true });
  const edge = spawn(EDGE, ['--headless=new', '--no-sandbox', '--disable-gpu', `--remote-debugging-port=${PORT}`, `--user-data-dir=${UDD}`, `--window-size=${VW},${VH}`, 'about:blank'], { stdio: 'ignore', detached: true });
  try {
    await waitJson(`http://127.0.0.1:${PORT}/json/version`);
    const tabs = await waitJson(`http://127.0.0.1:${PORT}/json/list`);
    ws = new WebSocket(tabs.find(x => x.type === 'page').webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { const { res } = pend.get(m.id); pend.delete(m.id); res(m.result || {}); } }; });
    await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: VW, height: VH, deviceScaleFactor: 1, mobile: false });
    for (const job of jobs) {
      const url = encodeURI('file:///' + job.file.replace(/\\/g, '/')) + '#toolbar=0&navpanes=0&view=FitH';
      await send('Page.navigate', { url });
      await delay(3000);
      const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false, fromSurface: true });
      await writeFile(path.join(OUT_DIR, `${job.name}.png`), Buffer.from(data, 'base64'));
      console.log('✓', job.name);
    }
  } finally { try { edge.kill(); } catch {} }
}
run().catch(e => { console.error(e); process.exitCode = 1; });
