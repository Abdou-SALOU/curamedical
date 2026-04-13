import { useEffect, useState } from 'react'
import api from '../api/axios'

const ROLE_CONFIG = {
  admin:     { label: 'Administrateur', icon: 'shield_person', colorClass: 'bg-error-container text-error'       },
  doctor:    { label: 'Médecin',        icon: 'stethoscope',   colorClass: 'bg-primary/10 text-primary'          },
  secretary: { label: 'Secrétaire',     icon: 'assignment_ind',colorClass: 'bg-secondary/10 text-secondary'      },
}

const EMPTY_FORM = {
  username: '', first_name: '', last_name: '',
  email: '', phone: '', role: 'secretary', password: ''
}

const inputClass = "w-full bg-surface-container-low border-0 rounded-xl px-4 py-3 text-on-surface text-sm placeholder:text-outline-variant/60 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:bg-surface-container-lowest transition-all duration-300"
const labelClass = "block text-xs font-semibold text-on-surface-variant uppercase tracking-widest mb-1.5"

export default function AdminPage() {
  const [users, setUsers] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const fetchUsers = async () => {
    const { data } = await api.get('/api/users/')
    setUsers(data.results || data)
  }
  useEffect(() => { fetchUsers() }, [])

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
    await api.delete(`/api/users/${id}/`)
    fetchUsers()
  }

  const roleGroups = {
    admin:     users.filter(u => u.role === 'admin'),
    doctor:    users.filter(u => u.role === 'doctor'),
    secretary: users.filter(u => u.role === 'secretary'),
  }

  return (
    <div className="p-8 space-y-6 max-w-[1400px]">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-on-surface tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>Administration</h1>
          <p className="text-on-surface-variant text-sm mt-1">Gestion des comptes utilisateurs</p>
        </div>
        <button onClick={() => setShowForm(true)}
          className="flex items-center gap-2 primary-gradient text-white px-5 py-2.5 rounded-xl font-medium text-sm hover:-translate-y-0.5 transition-all"
          style={{ boxShadow: '0 4px 12px rgba(0,104,95,0.2)' }}>
          <span className="material-symbols-outlined text-lg">person_add</span>
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
                    <td className="px-6 py-4 text-sm text-on-surface-variant">{u.phone || '—'}</td>
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
                  <input type="tel" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className={inputClass} />
                </div>
              </div>

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