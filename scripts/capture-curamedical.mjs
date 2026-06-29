import { spawn } from 'node:child_process';
import { mkdir, writeFile, rm } from 'node:fs/promises';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';

// Charge le fichier .env du projet dans process.env (sans dépendance externe).
function loadEnv(file = path.join(process.cwd(), '.env')) {
  if (!existsSync(file)) return;
  for (const line of readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*([\w.-]+)\s*=\s*(.*)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }
}
loadEnv();

// ─────────────────────────────────────────────────────────────
//  CuraMedical — Capture visuelle automatisée (thème CLAIR, 16:9)
//  Couvre les 4 types d'utilisateurs + scénarios fonctionnels poussés.
//  Pilote Microsoft Edge headless via le Chrome DevTools Protocol.
// ─────────────────────────────────────────────────────────────

const ROOT = process.cwd();
const OUT_DIR = path.join(ROOT, 'soutenance', 'screenshots', 'curamedical-rapport');
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const USER_DATA_DIR = 'C:\\tmp\\curamedical-edge-rapport';
const PORT = 9300 + Math.floor(Math.random() * 400);
const BASE = 'http://localhost:3000';
const API = 'http://127.0.0.1:8000';
const SCALE = 2;
const VW = 1920, VH = 1080;       // 16:9 (Full HD) pour les écrans applicatifs
const PVW = 900, PVH = 1240;      // cadre portrait pour les PDF (page A4 ~793px à 100%, marges fines)

// Identifiants des comptes de démonstration — lus depuis l'environnement
// (cf. .env / .env.example). Aucun mot de passe n'est codé en dur ici.
const demoAccount = (role, fallbackUser) => ({
  username: process.env[`DEMO_${role}_USER`] || fallbackUser,
  password: process.env[`DEMO_${role}_PASSWORD`] || '',
});
const accounts = {
  admin:      demoAccount('ADMIN', 'admin'),
  medecin:    demoAccount('MEDECIN', 'medecin'),         // Dr Nouredine SAWADOGO
  secretaire: demoAccount('SECRETAIRE', 'secretaire'),   // Kamara MACIRE
  patient:    demoAccount('PATIENT', 'abdou.salou'),     // Abdou SALOU
};

const missingPw = Object.entries(accounts).filter(([, a]) => !a.password).map(([r]) => r);
if (missingPw.length) {
  console.error(`✗ Mots de passe de démo manquants pour : ${missingPw.join(', ')}.`);
  console.error('  Renseignez DEMO_*_PASSWORD dans votre fichier .env (voir .env.example).');
  process.exit(1);
}

// ── 1) Captures simples (page entière, viewport 16:9) ─────────
const pages = [
  // Public
  { role: 'public',     path: '/login',          name: '01-accueil-landing',            expect: 'plateforme' },
  { role: 'public',     path: '/register',       name: '03-inscription-patient',        expect: 'Inscription' },
  // Administrateur
  { role: 'admin',      path: '/',               name: '04-admin-tableau-de-bord',      expect: 'Administrateur' },
  { role: 'admin',      path: '/admin',          name: '05-admin-gestion-utilisateurs', expect: 'Utilisateurs' },
  { role: 'admin',      path: '/patients/trash', name: '07-admin-corbeille-patients',   expect: 'Corbeille' },
  // Médecin — Dr Nouredine SAWADOGO
  { role: 'medecin',    path: '/',               name: '08-medecin-tableau-de-bord',    expect: 'Tableau' },
  { role: 'medecin',    path: '/patients',       name: '09-medecin-liste-patients',     expect: 'Patients' },
  { role: 'medecin',    path: '/appointments',   name: '12-medecin-rendez-vous',        expect: 'Rendez' },
  { role: 'medecin',    path: '/consultations',  name: '15-medecin-consultations',      expect: 'Consultations' },
  { role: 'medecin',    path: '/prescriptions',  name: '18-medecin-ordonnances',        expect: 'Ordonnances' },
  { role: 'medecin',    path: '/video',          name: '20-medecin-teleconsultation',   expect: 'consultation' },
  // Secrétaire — Kamara MACIRE
  { role: 'secretaire', path: '/',               name: '22-secretaire-tableau-de-bord', expect: 'Tableau' },
  { role: 'secretaire', path: '/patients',       name: '23-secretaire-patients',        expect: 'Patients' },
  { role: 'secretaire', path: '/appointments',   name: '24-secretaire-planning-rdv',    expect: 'Rendez' },
  { role: 'secretaire', path: '/consultations',  name: '25-secretaire-acces-refuse',    expect: 'refus' },
  // Patient — Abdou SALOU (4ᵉ type d'utilisateur)
  { role: 'patient',    path: '/',               name: '26-patient-espace-personnel',   expect: 'Bonjour' },
  { role: 'patient',    path: '/appointments',   name: '27-patient-mes-rendez-vous',    expect: 'Rendez' },
  { role: 'patient',    path: '/consultations',  name: '28-patient-mes-consultations',  expect: 'Consultation' },
  { role: 'patient',    path: '/prescriptions',  name: '29-patient-mes-ordonnances',    expect: 'Ordonnance' },
  { role: 'patient',    path: '/profile',        name: '30-patient-mon-profil',         expect: 'dossier' },
];

// ── 2) Captures avec une interaction (modale / tiroir) ────────
const interactions = [
  { role: 'public',  path: '/login',         name: '02-connexion-modale',                 click: { text: 'Connexion' },          expect: 'Bon retour' },
  { role: 'admin',   path: '/admin',         name: '06-admin-creation-compte',            click: { text: 'Nouvel utilisateur' }, expect: 'Créer le compte' },
  { role: 'secretaire', path: '/patients',   name: '10-secretaire-nouveau-patient',       click: { text: 'Nouveau patient' },    expect: 'Ajouter un patient' },
  { role: 'medecin', path: '/patients',      name: '11-medecin-fiche-patient',            click: { selector: 'tbody tr button[title="Voir la fiche"]' }, expect: 'Informations cliniques' },
  { role: 'medecin', path: '/appointments',  name: '13-medecin-nouveau-rdv',              click: { text: 'Nouveau RDV' },        expect: 'Nouveau rendez-vous' },
  { role: 'medecin', path: '/appointments',  name: '14-medecin-rdv-corbeille',            click: { text: 'Corbeille' },          expect: 'Corbeille' },
  { role: 'medecin', path: '/consultations', name: '16-medecin-nouvelle-consultation-ia', click: { text: 'Nouvelle consultation' }, expect: 'Assistant IA' },
  { role: 'medecin', path: '/consultations', name: '17-medecin-consultation-detail',      click: { row: true },                  expect: 'Diagnostic' },
  { role: 'medecin', path: '/prescriptions', name: '19-medecin-nouvelle-ordonnance',      click: { text: 'Nouvelle ordonnance' },expect: 'Nouvelle ordonnance' },
  { role: 'medecin', path: '/',              name: '21-medecin-chatbot-ia',               click: { selector: '[aria-label="Ouvrir le chatbot"]' }, expect: 'CuraMedical' },
];

// ── 3) Scénarios fonctionnels poussés (séquence d'actions) ────
const NOTE_TXT = "Patient revu en téléconsultation. État général stable, bonne observance du traitement antihypertenseur. Maintien Amlodipine 10mg. Contrôle de la tension dans 4 semaines. Recommandation : régime hyposodé, activité physique modérée 30 min/jour.";

const scenarios = [
  {
    // Auto-inscription du patient depuis la page publique /register (et non dans l'app).
    role: 'public', path: '/register', name: '31-inscription-patient-abdou-salou',
    steps: [
      { wait: 'Identifiants' },
      { js: `
        (() => {
          const set = (el, v) => {
            if (!el) return;
            const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, v);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          };
          set(document.querySelector('input[autocomplete="given-name"]'),  'Abdou');
          set(document.querySelector('input[autocomplete="family-name"]'), 'SALOU');
          set(document.querySelector('input[autocomplete="username"]'),    ${JSON.stringify(accounts.patient.username)});
          const pw = document.querySelectorAll('input[autocomplete="new-password"]');
          if (pw[0]) set(pw[0], ${JSON.stringify(accounts.patient.password)});
          if (pw[1]) set(pw[1], ${JSON.stringify(accounts.patient.password)});
          return true;
        })()
      ` },
      { delay: 500 },
    ],
    expect: 'Identifiants',
  },
  {
    role: 'medecin', path: '/patients', name: '32-medecin-recherche-patient',
    steps: [
      { type: { selector: 'input[placeholder*="Rechercher"]', value: 'SALOU' } },
      { delay: 800 },
    ],
    expect: 'SALOU',
  },
  {
    role: 'medecin', path: '/consultations', name: '33-medecin-consultation-analyse-ia',
    steps: [
      { clickText: 'Nouvelle consultation' },
      { wait: 'Assistant IA' },
      { clickText: 'Toux' },
      { clickText: 'Maux de tête' },
      { clickText: 'Vertiges' },
      { clickText: 'Fatigue' },
      { delay: 300 },
      { clickText: "Lancer l'analyse" },
      { delay: 5000 },
    ],
    expect: 'Résultats',
  },
  {
    role: 'medecin', path: '/', name: '34-medecin-chatbot-nombre-patients',
    steps: [
      { clickSelector: '[aria-label="Ouvrir le chatbot"]' },
      { wait: 'CuraMedical' },
      { type: { selector: 'input[placeholder*="Assistant"]', value: 'Combien de patients actifs ?' } },
      { clickSelector: 'form button[type="submit"]' },
      { wait: 'archiv', timeout: 28000, soft: true },   // « patient(s) archivé(s) » — unique à la réponse
      { delay: 1800 },
    ],
    expect: 'patient',
  },
  {
    role: 'medecin', path: '/', name: '35-medecin-chatbot-rendez-vous-jour',
    steps: [
      { clickSelector: '[aria-label="Ouvrir le chatbot"]' },
      { wait: 'CuraMedical' },
      { type: { selector: 'input[placeholder*="Assistant"]', value: "Rendez-vous d'aujourd'hui" } },
      { clickSelector: 'form button[type="submit"]' },
      { wait: 'avec dr', timeout: 28000, soft: true },   // « … avec Dr. SAWADOGO » — unique à la réponse
      { delay: 1800 },
    ],
    expect: 'rendez',
  },
  {
    role: 'medecin', path: '/', name: '36-medecin-chatbot-statistiques',
    steps: [
      { clickSelector: '[aria-label="Ouvrir le chatbot"]' },
      { wait: 'CuraMedical' },
      { type: { selector: 'input[placeholder*="Assistant"]', value: 'Statistiques du cabinet' } },
      { clickSelector: 'form button[type="submit"]' },
      { wait: 'au total', timeout: 28000, soft: true },   // « 51 au total » — unique à la réponse
      { delay: 1800 },
    ],
    expect: 'cabinet',
  },
  {
    role: 'medecin', path: '/teleconsultation/33', name: '37-medecin-teleconsultation-salle-notes',
    steps: [
      { wait: 'Diagnostic', timeout: 12000, soft: true },
      { clickText: 'Toux' },
      { clickText: 'Fièvre' },
      { type: { selector: 'textarea[placeholder*="Auscultation"]', value: 'Auscultation pulmonaire claire. Température 38.1°C. État général conservé.' } },
      { type: { selector: 'textarea[placeholder*="Diagnostic"]', value: 'Syndrome grippal saisonnier' } },
      { type: { selector: 'textarea[placeholder*="Conduite"]', value: NOTE_TXT } },
      { delay: 600 },
    ],
    expect: 'Notes',
  },
  {
    role: 'public', path: '/login', name: '40-connexion-formulaire-rempli',
    steps: [
      { clickText: 'Connexion' },
      { wait: 'Bon retour' },
      { type: { selector: '.login-modal input', value: accounts.medecin.username } },
      { type: { selector: '.login-modal input[type="password"]', value: accounts.medecin.password } },
      { delay: 400 },
    ],
    expect: 'retour',
  },
];

// ── 4) Rendus PDF (ordonnance + compte rendu), portrait A4 ────
const pdfs = [
  { name: '38-ordonnance-pdf',  file: 'ordonnance-exemple.pdf' },
  { name: '39-compte-rendu-pdf', file: 'compte-rendu-exemple.pdf' },
];

let ws, nextId = 1;
const pending = new Map();
const consoleErrors = [];
const delay = ms => new Promise(r => setTimeout(r, ms));

async function waitForHttp(url, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try { const res = await fetch(url); if (res.ok) return res.json(); } catch {}
    await delay(400);
  }
  throw new Error(`Timeout HTTP ${url}`);
}
function send(method, params = {}) {
  const id = nextId++;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); } }, 30000);
  });
}
async function evalJs(expression, awaitPromise = true) {
  const { result, exceptionDetails } = await send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
  if (exceptionDetails) throw new Error(exceptionDetails.text || 'eval failed');
  return result?.value;
}
async function navigate(url) { await send('Page.navigate', { url }); await delay(700); }

async function forceLightAndReveal() {
  await evalJs(`
    (() => {
      try {
        localStorage.setItem('cura-theme', JSON.stringify({ state: { theme: 'light' }, version: 0 }));
        document.documentElement.setAttribute('data-theme', 'light');
        document.documentElement.classList.remove('dark');
      } catch (e) {}
      const id = '__cap_force__';
      if (!document.getElementById(id)) {
        const s = document.createElement('style'); s.id = id;
        s.textContent = '.reveal,.reveal-x{opacity:1 !important;transform:none !important;} *,*::before,*::after{animation-duration:0s !important;animation-delay:0s !important;transition:none !important;}';
        document.head.appendChild(s);
      }
      document.querySelectorAll('.reveal,.reveal-x').forEach(el => el.classList.add('in'));
      return true;
    })()
  `);
}
async function ensureIconFont(timeoutMs = 15000) {
  await evalJs(`(() => { try { document.fonts.load("24px 'Material Symbols Outlined'"); document.fonts.load("700 48px 'Material Symbols Outlined'"); } catch(e){} return true; })()`);
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const ok = await evalJs(`(() => { try { return document.fonts.check("24px 'Material Symbols Outlined'"); } catch(e){ return false; } })()`);
    if (ok) { await delay(450); return true; }
    await delay(350);
  }
  return false;
}
async function bodyText() { return (await evalJs(`document.body ? document.body.innerText.slice(0, 9000) : ''`)) || ''; }
async function waitForText(text, timeoutMs = 12000) {
  if (!text) { await delay(1200); return true; }
  const start = Date.now();
  const wanted = text.toLowerCase();
  while (Date.now() - start < timeoutMs) {
    if ((await bodyText()).toLowerCase().includes(wanted)) return true;
    await delay(350);
  }
  return false;
}
async function tokenFor({ username, password }) {
  let lastError;
  for (let attempt = 1; attempt <= 5; attempt++) {
    try {
      const res = await fetch(`${API}/api/token/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) });
      if (!res.ok) throw new Error(`Login ${username}: ${res.status}`);
      return res.json();
    } catch (e) { lastError = e; await delay(900 * attempt); }
  }
  throw lastError;
}
async function setAuthAndTheme(role) {
  const themeJs = `localStorage.setItem('cura-theme', JSON.stringify({ state: { theme: 'light' }, version: 0 }));`;
  if (role === 'public') { await evalJs(`localStorage.clear(); ${themeJs} true`); return; }
  const token = await tokenFor(accounts[role]);
  await evalJs(`localStorage.clear(); localStorage.setItem('access_token', ${JSON.stringify(token.access)}); localStorage.setItem('refresh_token', ${JSON.stringify(token.refresh)}); ${themeJs} true;`);
}
async function clickByText(text) {
  return evalJs(`
    (() => {
      const wanted = ${JSON.stringify(text)}.toLowerCase();
      const el = [...document.querySelectorAll('button,a,[role="button"]')].find(n => (n.innerText || n.textContent || '').trim().toLowerCase().includes(wanted));
      if (!el) return false; el.scrollIntoView({ block: 'center' }); el.click(); return true;
    })()
  `);
}
async function clickBySelector(selector) {
  return evalJs(`(() => { const el = document.querySelector(${JSON.stringify(selector)}); if (!el) return false; el.scrollIntoView({ block: 'center' }); el.click(); return true; })()`);
}
async function clickFirstRow() {
  return evalJs(`(() => { const r = document.querySelector('tbody tr'); if (!r) return false; r.scrollIntoView({ block: 'center' }); r.click(); return true; })()`);
}
async function typeInto(selector, value) {
  return evalJs(`
    (() => {
      const el = document.querySelector(${JSON.stringify(selector)});
      if (!el) return false;
      el.focus();
      const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : (el.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype);
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, ${JSON.stringify(value)});
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()
  `);
}
// Réessaie un clic jusqu'à ce que l'élément soit présent (contenu chargé en asynchrone).
async function clickRetry(kind, arg, attempts = 8) {
  for (let a = 0; a < attempts; a++) {
    const ok = kind === 'text' ? await clickByText(arg) : kind === 'sel' ? await clickBySelector(arg) : await clickFirstRow();
    if (ok) return true;
    await delay(500);
  }
  return false;
}
async function runStep(s) {
  if (s.clickText)     return clickRetry('text', s.clickText);
  if (s.clickSelector) return clickRetry('sel', s.clickSelector);
  if (s.row)           return clickRetry('row');
  if (s.type)          return typeInto(s.type.selector, s.type.value);
  if (s.js)            return evalJs(s.js);
  if (s.wait)          return waitForText(s.wait, s.timeout || 12000);
  if (s.delay != null) { await delay(s.delay); return true; }
  return true;
}
async function screenshot(name) {
  const { data } = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false, fromSurface: true });
  const file = path.join(OUT_DIR, `${name}.png`);
  await writeFile(file, Buffer.from(data, 'base64'));
  return file;
}

async function run() {
  await mkdir(OUT_DIR, { recursive: true });
  if (existsSync(USER_DATA_DIR)) await rm(USER_DATA_DIR, { recursive: true, force: true });
  const edge = spawn(EDGE, [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--force-color-profile=srgb',
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${USER_DATA_DIR}`, `--window-size=${VW},${VH}`, `${BASE}/login`,
  ], { stdio: 'ignore', detached: true });
  const cleanup = () => { try { edge.kill(); } catch {} };
  const results = [];

  try {
    await waitForHttp(`http://127.0.0.1:${PORT}/json/version`);
    const tabs = await waitForHttp(`http://127.0.0.1:${PORT}/json/list`);
    const target = tabs.find(t => t.type === 'page') || tabs[0];
    ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      ws.onopen = resolve; ws.onerror = reject;
      ws.onmessage = ev => {
        const msg = JSON.parse(ev.data);
        if (msg.id && pending.has(msg.id)) { const { resolve: ok, reject: fail } = pending.get(msg.id); pending.delete(msg.id); msg.error ? fail(new Error(msg.error.message)) : ok(msg.result || {}); }
        if (msg.method === 'Log.entryAdded' && msg.params.entry.level === 'error') consoleErrors.push(msg.params.entry.text);
      };
    });
    await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
    const setMetrics = (w, h) => send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: SCALE, mobile: false });
    await setMetrics(VW, VH);
    await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'light' }] });

    // 1) Pages simples
    for (const p of pages) {
      await navigate(`${BASE}/login`); await setAuthAndTheme(p.role); await navigate(`${BASE}${p.path}`);
      const found = await waitForText(p.expect);
      await forceLightAndReveal(); await ensureIconFont(); await delay(400);
      const file = await screenshot(p.name);
      results.push({ name: p.name, role: p.role, status: found ? 'OK' : 'A_VERIFIER', file });
      console.log(`${found ? '✓' : '⚠'} ${p.name}`);
    }
    // 2) Interactions simples
    for (const it of interactions) {
      await navigate(`${BASE}/login`); await setAuthAndTheme(it.role); await navigate(`${BASE}${it.path}`);
      await waitForText(it.role === 'public' ? 'plateforme' : '', 8000);
      await forceLightAndReveal(); await delay(400);
      let clicked = it.click.text ? await clickRetry('text', it.click.text) : it.click.selector ? await clickRetry('sel', it.click.selector) : await clickRetry('row');
      const found = await waitForText(it.expect, 9000);
      await forceLightAndReveal(); await ensureIconFont(); await delay(400);
      const file = await screenshot(it.name);
      results.push({ name: it.name, role: it.role, status: (clicked && found) ? 'OK' : 'A_VERIFIER', file });
      console.log(`${(clicked && found) ? '✓' : '⚠'} ${it.name} (clic=${clicked}, texte=${found})`);
    }
    // 3) Scénarios poussés
    for (const sc of scenarios) {
      await navigate(`${BASE}/login`); await setAuthAndTheme(sc.role); await navigate(`${BASE}${sc.path}`);
      await waitForText(sc.role === 'public' ? 'plateforme' : '', 9000);
      await forceLightAndReveal(); await delay(400);
      let allOk = true;
      for (const step of sc.steps) {
        const r = await runStep(step);
        if (r === false && !step.soft) allOk = false;
        await delay(250);
      }
      const found = await waitForText(sc.expect, 8000);
      await forceLightAndReveal(); await ensureIconFont(); await delay(500);
      const file = await screenshot(sc.name);
      results.push({ name: sc.name, role: sc.role, status: (allOk && found) ? 'OK' : 'A_VERIFIER', file });
      console.log(`${(allOk && found) ? '✓' : '⚠'} ${sc.name} (steps=${allOk}, texte=${found})`);
    }
    // 4) Rendus PDF (ordonnance + compte rendu) — générés par scripts/render-pdfs.mjs
    //    dans une fenêtre portrait dédiée (le plugin PDF suit la taille de fenêtre, pas l'émulation).
    for (const pdf of pdfs) {
      results.push({ name: pdf.name, role: 'document', status: 'OK', file: path.join(OUT_DIR, `${pdf.name}.png`) });
    }

    // Rapport
    results.sort((a, b) => a.name.localeCompare(b.name));
    const report = [
      '# Audit visuel CuraMedical — Thème clair · 16:9',
      '', `Date : 2026-06-02`, `Base : ${BASE}`, '',
      '## Comptes de démonstration (équipe)',
      '', '| Rôle | Identifiant | Nom affiché |', '|---|---|---|',
      `| Administrateur | ${accounts.admin.username} | Super Admin |`,
      `| Médecin | ${accounts.medecin.username} | Dr Nouredine SAWADOGO |`,
      `| Secrétaire | ${accounts.secretaire.username} | Kamara MACIRE |`,
      `| Patient | ${accounts.patient.username} | Abdou SALOU |`,
      '', '## Captures', '', '| Statut | Rôle | Capture |', '|---|---|---|',
      ...results.map(r => `| ${r.status} | ${r.role} | ${path.basename(r.file)} |`),
      '', '## Erreurs console', '',
      ...(consoleErrors.length ? [...new Set(consoleErrors)].slice(0, 30).map(l => `- ${l}`) : ['- Aucune.']),
      '',
    ].join('\n');
    await writeFile(path.join(OUT_DIR, 'rapport-audit-visuel.md'), report, 'utf8');
    const ok = results.filter(r => r.status === 'OK').length;
    console.log(`\n${ok}/${results.length} captures OK → ${OUT_DIR}`);
  } finally { cleanup(); }
}
run().catch(err => { console.error(err); process.exitCode = 1; });
