import { useEffect, useState, useCallback } from 'react'
import api from '../api/axios'

const ROLE_CONFIG = {
  administrateur: { label: 'Administrateur', icon: 'shield_person', colorClass: 'bg-error-container text-error'       },
  medecin:        { label: 'Médecin',        icon: 'stethoscope',   colorClass: 'bg-primary/10 text-primary'          },
  secretaire:     { label: 'Secrétaire',     icon: 'assignment_ind',colorClass: 'bg-secondary/10 text-secondary'      },
}

const SPECIALITES = [
  'generaliste','cardiologue','dermatologue','gynecologue','pediatre',
  'ophtalmologue','dentiste','radiologue','chirurgien','neurologue',
  'pneumologue','rhumatologue','endocrinologue','gastro','psy','urgentiste','autre',
]

const EMPTY_FORM = {
  username: '', first_name: '', last_name: '',
  email: '', telephone: '', role: 'secretaire', password: '', specialite: '',
}

const inputClass = "w-full bg-surface-container-low border-0 rounded-xl px-4 py-3 text-on-surface text-sm placeholder:text-outline-variant/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-300"
const labelClass = "block text-xs font-semibold text-on-surface-variant uppercase tracking-widest mb-1.5"

export default function AdminPage() {
  const [users, setUsers] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [auditFilter, setAuditFilter] = useState('')
  const [tab, setTab] = useState('users') // 'users' | 'audit'
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const fetchUsers = useCallback(async () => {
    try {
      const { data } = await api.get('/api/users/?page_size=500')
      setUsers(data.results || data)
    } catch { /* liste vide en cas d'erreur réseau */ }
  }, [])
  useEffect(() => {
    let ignore = false
    const charger = async () => {
      const [usersRes, logsRes] = await Promise.allSettled([
        api.get('/api/users/?page_size=500'),
        api.get('/api/auditlog/?page_size=200'),
      ])
      if (ignore) return
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data.results || usersRes.value.data)
      if (logsRes.status === 'fulfilled') setAuditLogs(logsRes.value.data.results || logsRes.value.data)
    }
    charger()
    return () => { ignore = true }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError(''); setSuccess('')
    try {
      await api.post('/api/users/', form)
      setSuccess(`Compte "${form.username}" créé avec succès !`)
      setShowForm(false); setForm(EMPTY_FORM); fetchUsers()
    } catch (err) { setError(JSON.stringify(err.response?.data) || 'Erreur lors de la création.') }
    finally { setLoading(false) }
  }

  const handleDelete = async (id, username) => {
    if (!confirm(`Supprimer le compte "${username}" ?`)) return
    try {
      await api.delete(`/api/users/${id}/`)
      fetchUsers()
    } catch {
      setError('Impossible de supprimer ce compte.')
    }
  }

  const roleGroups = {
    administrateur: users.filter(u => u.role === 'administrateur'),
    medecin:        users.filter(u => u.role === 'medecin'),
    secretaire:     users.filter(u => u.role === 'secretaire'),
  }

  return (
    <div className="cm-page">
      {/* En-tête */}
      <div className="cm-page-head">
        <div>
          <div className="cm-eyebrow">Sécurité</div>
          <div className="cm-title">Administration</div>
          <div className="cm-sub">Gestion des comptes et traçabilité</div>
        </div>
        <button onClick={() => setShowForm(true)} className="cm-btn cm-btn-brand">
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>person_add</span>
          Nouvel utilisateur
        </button>
      </div>

      {/* Succès */}
      {success && (
        <div className="flex items-center justify-between bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl text-sm">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-green-600 text-lg">check_circle</span>
            {success}
          </div>
          <button onClick={() => setSuccess('')} className="text-green-500 hover:text-green-700">
            <span className="material-symbols-outlined text-base">close</span>
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 bg-slate-100 p-1 rounded-2xl w-fit">
        {[
          { key: 'users',  label: 'Utilisateurs', icon: 'group' },
          { key: 'audit',  label: 'Logs d\'audit', icon: 'history' },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
              tab === t.key ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'audit' && (
        <div className="bg-surface-container-lowest rounded-2xl ghost-border overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-outline-variant/10 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>Journal d'audit</h2>
              <p className="text-xs text-on-surface-variant mt-0.5">{auditLogs.length} entrée(s) enregistrée(s)</p>
            </div>
            <div className="flex gap-2">
              {[
                { key: '', label: 'Tout' },
                { key: '0', label: 'Créations' },
                { key: '1', label: 'Modifications' },
                { key: '2', label: 'Suppressions' },
              ].map(f => (
                <button
                  key={f.key}
                  onClick={() => setAuditFilter(f.key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    auditFilter === f.key
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                  }`}
                >{f.label}</button>
              ))}
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-widest text-slate-400 border-b border-slate-100">
                <tr>
                  <th className="px-5 py-3.5">Date &amp; heure</th>
                  <th className="px-5 py-3.5">Auteur</th>
                  <th className="px-5 py-3.5">Action</th>
                  <th className="px-5 py-3.5">Module</th>
                  <th className="px-5 py-3.5">Objet concerné</th>
                  <th className="px-5 py-3.5">Détails</th>
                  <th className="px-5 py-3.5">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {auditLogs
                  .filter(log => auditFilter === '' || String(log.action) === auditFilter)
                  .slice(0, 100)
                  .map((log, i) => (
                  <tr key={i} className="hover:bg-emerald-50/30 transition-colors">

                    {/* Date */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <p className="text-slate-700 font-medium text-xs">
                        {new Date(log.timestamp).toLocaleDateString('fr-FR')}
                      </p>
                      <p className="text-slate-400 text-[11px] mt-0.5">
                        {new Date(log.timestamp).toLocaleTimeString('fr-FR')}
                      </p>
                    </td>

                    {/* Auteur */}
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 text-[10px] font-black shrink-0">
                          {log.actor_name === 'Système' ? '⚙' : log.actor_name?.charAt(0)?.toUpperCase() || '?'}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-800 text-xs leading-tight">{log.actor_name || 'Système'}</p>
                          {log.actor_role && (
                            <p className="text-[10px] text-slate-400 leading-tight">{log.actor_role}</p>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* Action badge */}
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold ${
                        log.action === 0 ? 'bg-emerald-100 text-emerald-700' :
                        log.action === 1 ? 'bg-amber-100 text-amber-700' :
                                           'bg-rose-100 text-rose-700'
                      }`}>
                        {log.action === 0 ? '＋' : log.action === 1 ? '✎' : '✕'}
                        {log.action_label || (log.action === 0 ? 'Création' : log.action === 1 ? 'Modification' : 'Suppression')}
                      </span>
                    </td>

                    {/* Module */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1.5 text-xs text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg font-medium">
                        <span>{log.module_icon || '📋'}</span>
                        {log.module || '—'}
                      </span>
                    </td>

                    {/* Objet */}
                    <td className="px-5 py-3.5 max-w-[200px]">
                      <p className="text-slate-700 text-xs leading-5 truncate" title={log.object_repr}>
                        {log.object_repr || '—'}
                      </p>
                    </td>

                    {/* Détails (changes_summary) */}
                    <td className="px-5 py-3.5 max-w-[200px]">
                      {log.changes_summary?.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {log.changes_summary.map((change, ci) => (
                            <span key={ci} className="inline-block text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md leading-5">
                              {change}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-300 text-xs">—</span>
                      )}
                    </td>

                    {/* IP */}
                    <td className="px-5 py-3.5">
                      <span className="font-mono text-[11px] text-slate-400">{log.remote_addr || '—'}</span>
                    </td>

                  </tr>
                ))}
                {auditLogs.length === 0 && (
                  <tr>
                    <td colSpan={7} className="py-16 text-center">
                      <div className="flex flex-col items-center gap-3 text-slate-400">
                        <span className="material-symbols-outlined text-4xl opacity-30">manage_search</span>
                        <p className="text-sm font-medium">Aucun log d'audit disponible</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'users' && (
      <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-5">
        {Object.entries(ROLE_CONFIG).map(([role, { label, icon, colorClass }]) => (
          <div key={role} className="bg-surface-container-lowest rounded-2xl ghost-border p-6 flex items-center gap-4">
            <div className={`p-3 rounded-xl ${colorClass}`}>
              <span className="material-symbols-outlined text-2xl" style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
            </div>
            <div>
              <p className="text-on-surface-variant text-sm">{label}s</p>
              <p className="text-3xl font-bold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>{roleGroups[role].length}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Listes par rôle */}
      <div className="space-y-5">
        {Object.entries(ROLE_CONFIG).map(([role, { label, icon, colorClass }]) => (
          <div key={role} className="bg-surface-container-lowest rounded-2xl ghost-border overflow-hidden">
            <div className="px-6 py-4 flex items-center gap-3 border-b border-outline-variant/10">
              <div className={`p-1.5 rounded-lg ${colorClass}`}>
                <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
              </div>
              <h2 className="font-semibold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>{label}s</h2>
              <span className="ml-auto bg-surface-container-high text-on-surface-variant text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-widest">
                {roleGroups[role].length} compte{roleGroups[role].length !== 1 ? 's' : ''}
              </span>
            </div>
            <table className="w-full text-left">
              <thead>
                <tr className="text-on-surface-variant text-[10px] uppercase font-bold tracking-widest">
                  <th className="px-6 py-3">Nom d'utilisateur</th>
                  <th className="px-6 py-3">Nom complet</th>
                  <th className="px-6 py-3">Email</th>
                  <th className="px-6 py-3">Téléphone</th>
                  <th className="px-6 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/5">
                {roleGroups[role].map(u => (
                  <tr key={u.id} className="hover:bg-surface-container-low/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full primary-gradient flex items-center justify-center text-white text-[10px] font-bold">
                          {(u.first_name?.charAt(0) || '') + (u.last_name?.charAt(0) || '')}
                        </div>
                        <span className="font-mono text-sm text-on-surface">@{u.username}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-on-surface">{u.first_name} {u.last_name}</td>
                    <td className="px-6 py-4 text-sm text-on-surface-variant">{u.email || '—'}</td>
                    <td className="px-6 py-4 text-sm text-on-surface-variant">{u.telephone || '—'}</td>
                    <td className="px-6 py-4">
                      <button onClick={() => handleDelete(u.id, u.username)}
                        className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-error-container text-on-surface-variant hover:text-error transition-all">
                        <span className="material-symbols-outlined text-base">delete</span>
                      </button>
                    </td>
                  </tr>
                ))}
                {roleGroups[role].length === 0 && (
                  <tr><td colSpan={5} className="text-center py-8 text-on-surface-variant/50 text-sm">
                    Aucun {label.toLowerCase()} enregistré
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      </div>
      )}

      {/* Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-on-surface/30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface-container-lowest rounded-3xl ghost-border p-8 w-full max-w-lg" style={{ boxShadow: '0 24px 64px rgba(25,28,30,0.12)' }}>
            <div className="flex justify-between items-center mb-7">
              <h2 className="text-xl font-bold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>Nouvel utilisateur</h2>
              <button onClick={() => setShowForm(false)} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-high text-on-surface-variant">
                <span className="material-symbols-outlined text-lg">close</span>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Rôle */}
              <div>
                <label className={labelClass}>Rôle</label>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(ROLE_CONFIG).map(([role, { label, icon, colorClass }]) => (
                    <button key={role} type="button" onClick={() => setForm({ ...form, role })}
                      className={`flex flex-col items-center p-3 rounded-xl border-2 transition-all ${
                        form.role === role ? 'border-primary bg-primary/5' : 'border-outline-variant/20 hover:border-outline-variant/50'
                      }`}>
                      <div className={`p-2 rounded-lg ${colorClass} mb-1`}>
                        <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
                      </div>
                      <span className="text-xs font-medium text-on-surface">{label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Prénom</label>
                  <input type="text" required value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Nom</label>
                  <input type="text" required value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} className={inputClass} />
                </div>
              </div>

              <div>
                <label className={labelClass}>Nom d'utilisateur</label>
                <input type="text" required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} className={inputClass} placeholder="ex: dr.martin" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Email</label>
                  <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} className={inputClass} />
                </div>
                <div>
                  <label className={labelClass}>Téléphone</label>
                  <input type="tel" value={form.telephone} onChange={e => setForm({ ...form, telephone: e.target.value })} className={inputClass} />
                </div>
              </div>

              {form.role === 'medecin' && (
                <div>
                  <label className={labelClass}>Spécialité</label>
                  <select value={form.specialite} onChange={e => setForm({ ...form, specialite: e.target.value })} className={inputClass}>
                    <option value="">Sélectionner une spécialité</option>
                    {SPECIALITES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
                  </select>
                </div>
              )}

              <div>
                <label className={labelClass}>Mot de passe</label>
                <input type="password" required minLength={8} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} className={inputClass} placeholder="Minimum 8 caractères" />
              </div>

              {error && (
                <div className="flex items-center gap-2 bg-error-container text-on-error-container px-4 py-3 rounded-xl text-sm">
                  <span className="material-symbols-outlined text-error text-lg">error</span>
                  {error}
                </div>
              )}

              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="px-6 py-2.5 bg-surface-container-high text-on-surface rounded-xl text-sm font-medium hover:bg-surface-container transition-all">
                  Annuler
                </button>
                <button type="submit" disabled={loading} className="px-6 py-2.5 primary-gradient text-white rounded-xl text-sm font-medium disabled:opacity-60 hover:-translate-y-0.5 transition-all" style={{ boxShadow: '0 4px 12px rgba(0,104,95,0.2)' }}>
                  {loading ? 'Création...' : 'Créer le compte'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
