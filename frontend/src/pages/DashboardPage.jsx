import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import useAuthStore from '../store/authStore'
import { STATUS_LABELS, API } from '../utils/constants'
import Icon from '../components/Icon'
import Sparkline from '../components/Sparkline'
import Donut from '../components/Donut'
import Bars from '../components/Bars'

const STATUS_COLORS = {
  Confirmé: '#2a9b69', 'En attente': '#c98b1e',
  Annulé: '#d4543f', Terminé: '#4178d6',
  'En cours': '#4178d6',
}

function localDateKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function buildChartData(items, dateField, period) {
  const now = new Date()

  if (period === '7j') {
    const result = []
    for (let i = 6; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i)
      const key = localDateKey(d)
      const raw = d.toLocaleDateString('fr-FR', { weekday: 'short' })
      result.push({ key, label: raw.charAt(0).toUpperCase() + raw.slice(1, 3), value: 0 })
    }
    items.forEach(item => {
      const key = localDateKey(new Date(item[dateField]))
      const found = result.find(r => r.key === key)
      if (found) found.value++
    })
    return result
  }

  if (period === '30j') {
    const result = [
      { label: 'S-4', value: 0 },
      { label: 'S-3', value: 0 },
      { label: 'S-2', value: 0 },
      { label: 'S-1', value: 0 },
    ]
    items.forEach(item => {
      const daysAgo = Math.floor((now - new Date(item[dateField])) / 86400000)
      if (daysAgo < 7)        result[3].value++
      else if (daysAgo < 14)  result[2].value++
      else if (daysAgo < 21)  result[1].value++
      else if (daysAgo < 30)  result[0].value++
    })
    return result
  }

  // 12m — dernier 12 mois glissants
  const MONTHS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
  const result = []
  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    result.push({ key: `${d.getFullYear()}-${d.getMonth()}`, label: MONTHS[d.getMonth()], value: 0 })
  }
  items.forEach(item => {
    const d = new Date(item[dateField])
    const key = `${d.getFullYear()}-${d.getMonth()}`
    const found = result.find(r => r.key === key)
    if (found) found.value++
  })
  return result
}

function exportDashboardCSV({ period, monthlyData, stats, apptDist, isSecretary, topDx }) {
  const title = isSecretary ? 'Rendez-vous' : 'Consultations'
  const now = new Date().toLocaleDateString('fr-FR')
  const lines = [
    `Tableau de bord CuraMedical - Exporté le ${now}`,
    `Période sélectionnée,${period}`,
    '',
    '=== STATISTIQUES GÉNÉRALES ===',
    `Patients actifs,${stats.patients}`,
    `Rendez-vous,${stats.appointments}`,
    ...(isSecretary ? [] : [`Consultations,${stats.consultations}`, `Analyses IA,${stats.ia_used}`]),
    '',
    `=== ACTIVITÉ ${title.toUpperCase()} (${period}) ===`,
    'Période,Nombre',
    ...monthlyData.map(m => `${m.label},${m.value}`),
    '',
    '=== STATUT DES RENDEZ-VOUS ===',
    'Statut,Nombre',
    ...apptDist.map(s => `${s.label},${s.value}`),
    ...(topDx.length > 0 ? [
      '',
      '=== TOP DIAGNOSTICS ===',
      'Diagnostic,Occurrences',
      ...topDx.map(d => `"${d.name}",${d.count}`),
    ] : []),
  ]

  const bom = '﻿'
  const blob = new Blob([bom + lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `curamedical-dashboard-${period}-${localDateKey(new Date())}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/* ── Dashboard Administrateur — stats système uniquement ── */
function AdminSystemDashboard({ user }) {
  const [sysStats, setSysStats] = useState({ medecins: 0, secretaires: 0, patients: 0, admins: 0, total: 0 })
  const [loading, setLoading]   = useState(true)

  useEffect(() => {
    api.get('/api/users/?page_size=1000').then(r => {
      const list = r.data.results || r.data || []
      setSysStats({
        medecins:    list.filter(u => u.role === 'medecin').length,
        secretaires: list.filter(u => u.role === 'secretaire').length,
        admins:      list.filter(u => u.role === 'administrateur').length,
        patients:    list.filter(u => u.role === 'patient').length,
        total:       list.length,
      })
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const today = new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  const cards = [
    { label: 'Médecins',    value: sysStats.medecins,    icon: 'stethoscope', color: '#2a9b69', bg: 'var(--brand-50)'  },
    { label: 'Secrétaires', value: sysStats.secretaires, icon: 'badge',       color: '#6a5acd', bg: '#ece9fb'          },
    { label: 'Patients',    value: sysStats.patients,    icon: 'users',       color: '#4178d6', bg: '#eaf1fb'          },
    { label: 'Admins',      value: sysStats.admins,      icon: 'shield',      color: '#d4543f', bg: '#fbeae6'          },
  ]

  return (
    <div className="cm-page page-enter">
      <div className="cm-page-head">
        <div>
          <div className="cm-eyebrow">Système</div>
          <div className="cm-title">Bonjour, {user?.first_name || user?.username} 👋</div>
          <div className="cm-sub" style={{ textTransform: 'capitalize' }}>{today}</div>
        </div>
        <Link to="/admin" className="cm-btn cm-btn-brand" style={{ textDecoration: 'none' }}>
          <Icon name="settings" size={14} /> Gérer les utilisateurs
        </Link>
      </div>

      <div className="cm-stat-grid" style={{ gridTemplateColumns: 'repeat(4,1fr)' }}>
        {loading ? [1, 2, 3, 4].map(i => (
          <div key={i} className="cm-stat" style={{ height: 110, background: 'var(--ink-50)', animation: 'pulse 1.5s infinite' }} />
        )) : cards.map(c => (
          <div key={c.label} className="cm-stat">
            <div className="cm-stat-icon" style={{ background: c.bg, color: c.color }}>
              <Icon name={c.icon} size={16} />
            </div>
            <div className="cm-stat-label">{c.label}</div>
            <div className="cm-stat-value">{c.value}</div>
            <div className="cm-stat-delta up" style={{ color: c.color }}>
              <Icon name="users" size={11} /> utilisateurs actifs
            </div>
          </div>
        ))}
      </div>

      <div className="cm-card" style={{ marginTop: 0 }}>
        <div className="cm-card-head">
          <div>
            <div className="cm-card-eyebrow">Accès rapide</div>
            <div className="cm-card-title">Actions administrateur</div>
          </div>
        </div>
        <div className="cm-qa-grid" style={{ gridTemplateColumns: 'repeat(3,1fr)' }}>
          {[
            { icon: 'users',  title: 'Gérer les comptes', sub: 'Créer, modifier, supprimer', to: '/admin' },
            { icon: 'shield', title: "Logs d'audit",       sub: 'Traçabilité des actions',   to: '/admin' },
            { icon: 'chart',  title: 'Statistiques',       sub: 'Activité de la plateforme', to: '/admin' },
          ].map((q, i) => (
            <Link key={i} to={q.to} className="cm-qa" style={{ textDecoration: 'none' }}>
              <div className="cm-qa-ico"><Icon name={q.icon} size={18} /></div>
              <div>
                <div className="cm-qa-title">{q.title}</div>
                <div className="cm-qa-sub">{q.sub}</div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="cm-card" style={{ marginTop: 16, background: 'var(--brand-50)', border: '1px solid var(--brand-100)' }}>
        <div className="cm-row" style={{ gap: 12 }}>
          <Icon name="shield" size={20} style={{ color: 'var(--brand-600)', flexShrink: 0 }} />
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--brand-800)', marginBottom: 4 }}>
              Périmètre administrateur
            </div>
            <div style={{ fontSize: 13, color: 'var(--brand-700)', lineHeight: 1.6 }}>
              Vous gérez les <strong>comptes utilisateurs</strong> et les <strong>droits d'accès</strong>.
              Les données cliniques des patients (consultations, ordonnances, dossiers médicaux)
              sont réservées aux médecins et au personnel soignant conformément aux règles de confidentialité.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Dashboard Médecin / Secrétaire / Patient ── */
function MedicalDashboard({ user, isSecretary, isPatient }) {
  const [period, setPeriod]           = useState('12m')
  const [stats, setStats]             = useState({ patients: 0, appointments: 0, consultations: 0, ia_used: 0 })
  const [rawApptList, setRawApptList] = useState([])
  const [rawConsList, setRawConsList] = useState([])
  const [apptDist, setApptDist]       = useState([])
  const [topDx, setTopDx]             = useState([])
  const [loading, setLoading]         = useState(true)

  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })

  useEffect(() => {
    const load = async () => {
      try {
        // Toutes les requêtes en parallèle — une seule vague réseau
        const reqs = [api.get(`${API.APPOINTMENTS}?page_size=200`)]
        if (!isPatient)                 reqs.push(api.get(`${API.PATIENTS}?page_size=1`))
        if (!isSecretary && !isPatient) reqs.push(api.get(`${API.CONSULTATIONS}?page_size=200`))
        const results = await Promise.all(reqs)

        const apptRes = results[0]
        const consRes = (!isSecretary && !isPatient) ? results[2] : null

        const apptList = apptRes.data.results ?? apptRes.data ?? []
        const consList = consRes ? (consRes.data.results ?? consRes.data ?? []) : []

        const aCount = apptRes.data.count ?? apptList.length
        const pCount = !isPatient ? (results[1].data.count ?? 0) : 0
        const cCount = consRes ? (consRes.data.count ?? consList.length) : 0

        const iaUsed = consList.filter(c => c.ia_utilisee).length
        setStats({ patients: pCount, appointments: aCount, consultations: cCount, ia_used: iaUsed })
        setRawApptList(apptList)
        setRawConsList(consList)

        const stCounts = {}
        apptList.forEach(a => {
          const label = STATUS_LABELS[a.statut] || a.statut
          stCounts[label] = (stCounts[label] || 0) + 1
        })
        setApptDist(
          Object.entries(stCounts).map(([label, value]) => ({
            label, value, color: STATUS_COLORS[label] || '#98a3b1',
          }))
        )

        if (!isSecretary && !isPatient) {
          const dx = {}
          consList.forEach(c => { if (c.diagnostic) dx[c.diagnostic] = (dx[c.diagnostic] || 0) + 1 })
          setTopDx(
            Object.entries(dx)
              .map(([name, count]) => ({ name, count }))
              .sort((a, b) => b.count - a.count)
              .slice(0, 5)
          )
        }
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [isSecretary, isPatient])

  const monthlyData = useMemo(() => {
    const src       = isSecretary ? rawApptList : rawConsList
    const dateField = isSecretary ? 'date_heure' : 'date_consultation'
    return buildChartData(src, dateField, period)
  }, [rawApptList, rawConsList, isSecretary, period])

  if (loading) return (
    <div className="cm-page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{ width: 40, height: 40, borderRadius: '50%', border: '3px solid var(--brand-100)', borderTopColor: 'var(--brand-500)', animation: 'spin 0.8s linear infinite' }} />
        <p style={{ fontSize: 14, color: 'var(--ink-500)', fontWeight: 600 }}>Chargement du tableau de bord…</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )

  const statCards = [
    { label: 'Patients actifs', value: stats.patients,     icon: 'users',       delta: '+3.2%', up: true, roles: ['administrateur', 'medecin', 'secretaire'] },
    { label: 'Rendez-vous',      value: stats.appointments, icon: 'calendar',    delta: '+5',    up: true, roles: ['administrateur', 'medecin', 'secretaire', 'patient'] },
    { label: 'Consultations',    value: stats.consultations,icon: 'stethoscope', delta: '+2',    up: true, roles: ['administrateur', 'medecin'] },
    { label: 'Analyses IA',      value: stats.ia_used,      icon: 'sparkle',     delta: '+8.1%', up: true, roles: ['administrateur', 'medecin'] },
  ].filter(c => c.roles.includes(user?.role))

  const quickLinks = [
    { label: 'Nouveau patient',    sub: 'Créer un dossier', to: '/patients',      icon: 'users',       roles: ['administrateur', 'medecin', 'secretaire'] },
    { label: 'Nouveau RDV',        sub: 'Planifier',        to: '/appointments',  icon: 'calendar',    roles: ['administrateur', 'medecin', 'secretaire', 'patient'] },
    { label: 'Créer consultation', sub: 'Démarrer examen',  to: '/consultations', icon: 'stethoscope', roles: ['administrateur', 'medecin'] },
    { label: 'Rédiger ordonnance', sub: 'Prescription',     to: '/prescriptions', icon: 'file',        roles: ['administrateur', 'medecin'] },
  ].filter(l => l.roles.includes(user?.role))

  const sparklineValues = monthlyData.map(m => m.value)
  const sparklineLabels = monthlyData.map(m => m.label)
  const periodTotal     = sparklineValues.reduce((s, v) => s + v, 0)
  const barsData        = monthlyData.slice(-6).map((m, i, arr) => ({ ...m, highlight: i >= arr.length - 2 }))
  const iaRate          = stats.consultations > 0 ? Math.round((stats.ia_used / stats.consultations) * 100) : 0

  const handleExport = () => exportDashboardCSV({ period, monthlyData, stats, apptDist, isSecretary, topDx })

  return (
    <div className="cm-page page-enter">
      {/* Header */}
      <div className="cm-page-head">
        <div>
          <div className="cm-eyebrow">Tableau de bord</div>
          <div className="cm-title">
            Bonjour, {user?.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user?.username} 👋
          </div>
          <div className="cm-sub" style={{ textTransform: 'capitalize' }}>{today}</div>
        </div>
        <div className="cm-row" style={{ gap: 12 }}>
          <button className="cm-btn cm-btn-ghost" onClick={handleExport}>
            <Icon name="download" size={14} /> Exporter
          </button>
          {!isPatient && !isSecretary && (
            <Link to="/consultations" className="cm-btn cm-btn-brand" style={{ textDecoration: 'none' }}>
              <Icon name="plus" size={14} /> Nouvelle consultation
            </Link>
          )}
        </div>
      </div>

      {/* Stat grid */}
      <div className="cm-stat-grid">
        {statCards.map((s, i) => (
          <div className="cm-stat" key={i}>
            <div className="cm-stat-icon"><Icon name={s.icon} size={16} /></div>
            <div className="cm-stat-label">{s.label}</div>
            <div className="cm-stat-value">{s.value.toLocaleString('fr-FR')}</div>
            <div className={`cm-stat-delta ${s.up ? 'up' : 'down'}`}>
              <Icon name={s.up ? 'arrowUp' : 'arrowDown'} size={12} />
              {s.delta} vs mois dernier
            </div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="cm-grid-2-1 cm-mb-4">
        {/* Sparkline card */}
        <div className="cm-card">
          <div className="cm-card-head">
            <div>
              <div className="cm-card-eyebrow">Évolution mensuelle</div>
              <div className="cm-card-title">
                {isSecretary ? 'Activité des rendez-vous' : 'Activité des consultations'}
              </div>
            </div>
            <div className="cm-segmented">
              {['12m', '30j', '7j'].map(p => (
                <button
                  key={p}
                  className={`cm-seg${period === p ? ' active' : ''}`}
                  onClick={() => setPeriod(p)}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
          <div className="cm-row" style={{ alignItems: 'baseline', gap: 12, marginBottom: 8 }}>
            <div className="cm-mono" style={{ fontSize: 32, fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--ink-900)' }}>
              {periodTotal.toLocaleString('fr-FR')}
            </div>
            <span className="cm-pill cm-pill-success"><Icon name="arrowUp" size={11} /> +12.4%</span>
          </div>
          <Sparkline
            data={sparklineValues.length > 1 ? sparklineValues : [0, 1]}
            labels={sparklineLabels}
            height={130}
            width={600}
            color="#2a9b69"
          />
          <div className="cm-row" style={{ justifyContent: 'space-between', marginTop: 6 }}>
            {sparklineLabels.map((m, i) => (
              <span key={i} className="cm-mono cm-muted" style={{ fontSize: 10 }}>{m}</span>
            ))}
          </div>
        </div>

        {/* Donut card */}
        <div className="cm-card">
          <div className="cm-card-head">
            <div>
              <div className="cm-card-eyebrow">Distribution</div>
              <div className="cm-card-title">Statut des rendez-vous</div>
            </div>
          </div>
          {apptDist.length > 0 ? (
            <div className="cm-row" style={{ alignItems: 'center', gap: 16 }}>
              <Donut segments={apptDist} size={140} />
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {apptDist.map(s => (
                  <div key={s.label} className="cm-row" style={{ justifyContent: 'space-between', fontSize: 12 }}>
                    <div className="cm-row" style={{ gap: 6 }}>
                      <span style={{ width: 8, height: 8, borderRadius: 2, background: s.color, flexShrink: 0 }} />
                      <span style={{ color: 'var(--ink-700)' }}>{s.label}</span>
                    </div>
                    <span className="cm-mono" style={{ color: 'var(--ink-900)', fontWeight: 600 }}>{s.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '32px 0', color: 'var(--ink-400)', fontSize: 13 }}>
              Aucun rendez-vous trouvé
            </div>
          )}
        </div>
      </div>

      {/* IA + top diagnostics — médecin/admin only */}
      {!isSecretary && !isPatient && (
        <div className="cm-grid-2 cm-mb-4">
          <div className="cm-card">
            <div className="cm-card-head">
              <div>
                <div className="cm-card-eyebrow">IA Médicale</div>
                <div className="cm-card-title">Taux d'adoption IA</div>
              </div>
              <span className="cm-pill cm-pill-success"><Icon name="sparkle" size={11} /> +8.1%</span>
            </div>
            <div className="cm-row" style={{ alignItems: 'baseline', gap: 12, marginBottom: 8 }}>
              <div className="cm-mono" style={{ fontSize: 32, fontWeight: 700 }}>
                {iaRate}<span style={{ fontSize: 18, color: 'var(--ink-400)' }}>%</span>
              </div>
              <span className="cm-muted" style={{ fontSize: 12 }}>
                {stats.ia_used} / {stats.consultations} consultations assistées
              </span>
            </div>
            {barsData.length > 0
              ? <Bars data={barsData} height={120} />
              : <div style={{ height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink-400)', fontSize: 13 }}>Données insuffisantes</div>
            }
          </div>

          <div className="cm-card">
            <div className="cm-card-head">
              <div>
                <div className="cm-card-eyebrow">Analyse clinique</div>
                <div className="cm-card-title">Top diagnostics</div>
              </div>
              <Link to="/consultations" className="cm-btn cm-btn-ghost cm-btn-sm" style={{ textDecoration: 'none' }}>
                Voir tout <Icon name="chevron" size={12} />
              </Link>
            </div>
            {topDx.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {topDx.map((d, i) => (
                  <div key={i}>
                    <div className="cm-row" style={{ justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 13, color: 'var(--ink-800)', fontWeight: 500, flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {d.name}
                      </span>
                      <span className="cm-mono" style={{ fontSize: 12, color: 'var(--ink-600)', marginLeft: 8 }}>{d.count}</span>
                    </div>
                    <div style={{ height: 4, background: 'var(--ink-50)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ width: `${(d.count / topDx[0].count) * 100}%`, height: '100%', background: i === 0 ? 'var(--brand-500)' : 'var(--brand-300)' }} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '24px 0', color: 'var(--ink-400)', fontSize: 13 }}>
                Aucun diagnostic enregistré
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quick actions */}
      {quickLinks.length > 0 && (
        <div className="cm-card">
          <div className="cm-card-head">
            <div>
              <div className="cm-card-eyebrow">Actions rapides</div>
              <div className="cm-card-title">Raccourcis cliniques</div>
            </div>
          </div>
          <div className="cm-qa-grid">
            {quickLinks.map((q, i) => (
              <Link key={i} to={q.to} className="cm-qa" style={{ textDecoration: 'none' }}>
                <div className="cm-qa-ico"><Icon name={q.icon} size={18} /></div>
                <div>
                  <div className="cm-qa-title">{q.label}</div>
                  <div className="cm-qa-sub">{q.sub}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const isAdmin     = user?.role === 'administrateur'
  const isSecretary = user?.role === 'secretaire'
  const isPatient   = user?.role === 'patient'

  if (isAdmin) return <AdminSystemDashboard user={user} />
  return <MedicalDashboard user={user} isSecretary={isSecretary} isPatient={isPatient} />
}
