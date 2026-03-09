import { useEffect, useState } from 'react'
import api from '../api/axios'
import { UserPlus, Trash2, Shield, Stethoscope, ClipboardList } from 'lucide-react'

const ROLE_CONFIG = {
  admin:     { label: 'Administrateur', icon: Shield,        color: 'bg-red-100 text-red-700'     },
  doctor:    { label: 'Médecin',        icon: Stethoscope,   color: 'bg-blue-100 text-blue-700'   },
  secretary: { label: 'Secrétaire',     icon: ClipboardList, color: 'bg-green-100 text-green-700' },
}

const EMPTY_FORM = {
  username: '', first_name: '', last_name: '',
  email: '', phone: '', role: 'secretary', password: ''
}

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
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      await api.post('/api/users/', form)
      setSuccess(`Compte "${form.username}" créé avec succès !`)
      setShowForm(false)
      setForm(EMPTY_FORM)
      fetchUsers()
    } catch (err) {
      setError(JSON.stringify(err.response?.data) || 'Erreur lors de la création.')
    } finally {
      setLoading(false)
    }
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
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Administration</h1>
          <p className="text-gray-500 mt-1">Gestion des comptes utilisateurs</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-all"
        >
          <UserPlus size={18} /> Nouvel utilisateur
        </button>
      </div>

      {/* Message succès */}
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6 flex justify-between">
          {success}
          <button onClick={() => setSuccess('')}>✕</button>
        </div>
      )}

      {/* Statistiques */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        {Object.entries(ROLE_CONFIG).map(([role, { label, icon: Icon, color }]) => (
          <div key={role} className="bg-white rounded-xl shadow-sm p-6 flex items-center gap-4">
            <div className={`p-3 rounded-xl ${color}`}>
              <Icon size={24} />
            </div>
            <div>
              <p className="text-gray-500 text-sm">{label}s</p>
              <p className="text-3xl font-bold text-gray-800">
                {roleGroups[role].length}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Listes par rôle */}
      <div className="space-y-6">
        {Object.entries(ROLE_CONFIG).map(([role, { label, icon: Icon, color }]) => (
          <div key={role} className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className={`px-6 py-4 flex items-center gap-2 border-b border-gray-100`}>
              <div className={`p-1.5 rounded-lg ${color}`}>
                <Icon size={16} />
              </div>
              <h2 className="font-semibold text-gray-800">{label}s</h2>
              <span className="ml-auto bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
                {roleGroups[role].length} compte(s)
              </span>
            </div>

            <table className="w-full">
              <thead className="bg-gray-50 text-gray-600 text-sm">
                <tr>
                  <th className="text-left px-6 py-3">Nom d'utilisateur</th>
                  <th className="text-left px-6 py-3">Nom complet</th>
                  <th className="text-left px-6 py-3">Email</th>
                  <th className="text-left px-6 py-3">Téléphone</th>
                  <th className="text-left px-6 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {roleGroups[role].map(u => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-800">
                      @{u.username}
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {u.first_name} {u.last_name}
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {u.email || '—'}
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {u.phone || '—'}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleDelete(u.id, u.username)}
                        className="text-gray-400 hover:text-red-600 transition-all"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {roleGroups[role].length === 0 && (
                  <tr>
                    <td colSpan={5} className="text-center py-8 text-gray-400 text-sm">
                      Aucun {label.toLowerCase()} enregistré
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {/* Modal création utilisateur */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-lg">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Nouvel utilisateur</h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >✕</button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">

              {/* Rôle */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rôle
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(ROLE_CONFIG).map(([role, { label, icon: Icon, color }]) => (
                    <button
                      key={role}
                      type="button"
                      onClick={() => setForm({ ...form, role })}
                      className={`flex flex-col items-center p-3 rounded-xl border-2 transition-all ${
                        form.role === role
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className={`p-2 rounded-lg ${color} mb-1`}>
                        <Icon size={16} />
                      </div>
                      <span className="text-xs font-medium text-gray-700">{label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Identifiants */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prénom
                  </label>
                  <input
                    type="text"
                    required
                    value={form.first_name}
                    onChange={e => setForm({ ...form, first_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom
                  </label>
                  <input
                    type="text"
                    required
                    value={form.last_name}
                    onChange={e => setForm({ ...form, last_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  required
                  value={form.username}
                  onChange={e => setForm({ ...form, username: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ex: dr.martin"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={e => setForm({ ...form, email: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={e => setForm({ ...form, phone: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mot de passe
                </label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={form.password}
                  onChange={e => setForm({ ...form, password: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Minimum 8 caractères"
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-3 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50"
                >
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