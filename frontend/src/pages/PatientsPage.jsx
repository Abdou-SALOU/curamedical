import { useEffect, useState } from 'react'
import api from '../api/axios'
import { UserPlus, Search, Eye, Archive } from 'lucide-react'

const EMPTY_FORM = {
  first_name: '', last_name: '', date_of_birth: '',
  gender: 'M', national_id: '', phone: '', email: '',
  address: '', blood_group: '', allergies: '', medical_history: ''
}

export default function PatientsPage() {
  const [patients, setPatients] = useState([])
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchPatients = async (q = '') => {
    const { data } = await api.get(`/api/patients/?search=${q}`)
    setPatients(data.results || data)
  }

  useEffect(() => { fetchPatients() }, [])

  const handleSearch = (e) => {
    setSearch(e.target.value)
    fetchPatients(e.target.value)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/api/patients/', form)
      setShowForm(false)
      setForm(EMPTY_FORM)
      fetchPatients()
    } catch (err) {
      setError('Erreur lors de la création du patient.')
    } finally {
      setLoading(false)
    }
  }

  const handleArchive = async (id) => {
    if (!confirm('Archiver ce patient ?')) return
    await api.delete(`/api/patients/${id}/`)
    fetchPatients()
    setSelected(null)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Patients</h1>
          <p className="text-gray-500 mt-1">{patients.length} patient(s) enregistré(s)</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-all"
        >
          <UserPlus size={18} /> Nouveau patient
        </button>
      </div>

      {/* Barre de recherche */}
      <div className="relative mb-6">
        <Search size={18} className="absolute left-3 top-3 text-gray-400" />
        <input
          type="text"
          placeholder="Rechercher par nom ou CIN..."
          value={search}
          onChange={handleSearch}
          className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex gap-6">
        {/* Liste */}
        <div className="flex-1 bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 text-gray-600 text-sm">
              <tr>
                <th className="text-left px-6 py-3">Nom</th>
                <th className="text-left px-6 py-3">Âge</th>
                <th className="text-left px-6 py-3">Téléphone</th>
                <th className="text-left px-6 py-3">Groupe sanguin</th>
                <th className="text-left px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {patients.map(p => (
                <tr
                  key={p.id}
                  className={`hover:bg-gray-50 cursor-pointer transition-all ${
                    selected?.id === p.id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => setSelected(p)}
                >
                  <td className="px-6 py-4 font-medium text-gray-800">{p.full_name}</td>
                  <td className="px-6 py-4 text-gray-600">{p.age} ans</td>
                  <td className="px-6 py-4 text-gray-600">{p.phone}</td>
                  <td className="px-6 py-4">
                    <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-medium">
                      {p.blood_group || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={e => { e.stopPropagation(); setSelected(p) }}
                      className="text-blue-600 hover:text-blue-800 mr-3"
                    >
                      <Eye size={16} />
                    </button>
                    <button
                      onClick={e => { e.stopPropagation(); handleArchive(p.id) }}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <Archive size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              {patients.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-gray-400">
                    Aucun patient trouvé
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Fiche patient */}
        {selected && (
          <div className="w-80 bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-gray-800 text-lg">Dossier patient</h2>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="space-y-3 text-sm">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto text-2xl font-bold text-blue-600">
                  {selected.first_name?.charAt(0) || '?'}{selected.last_name?.charAt(0) || '?'}
                </div>
                <p className="font-bold text-lg mt-2">{selected.full_name}</p>
                <p className="text-gray-500">{selected.age} ans</p>
              </div>
              {[
                ['CIN',           selected.national_id              ],
                ['Téléphone',     selected.phone                    ],
                ['Email',         selected.email        || '—'      ],
                ['Genre',         selected.gender === 'M' ? 'Masculin' : 'Féminin'],
                ['Groupe sanguin',selected.blood_group  || '—'      ],
                ['Allergies',     selected.allergies    || 'Aucune' ],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between border-b border-gray-100 pb-2">
                  <span className="text-gray-500">{label}</span>
                  <span className="font-medium text-gray-800 text-right max-w-40">{value}</span>
                </div>
              ))}
              {selected.medical_history && (
                <div className="mt-3">
                  <p className="text-gray-500 mb-1">Antécédents</p>
                  <p className="text-gray-700 bg-gray-50 p-2 rounded text-xs">
                    {selected.medical_history}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modal création patient */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-2xl max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Nouveau patient</h2>
              <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
              {[
                ['Prénom', 'first_name', 'text', true],
                ['Nom', 'last_name', 'text', true],
                ['Date de naissance', 'date_of_birth', 'date', true],
                ['CIN', 'national_id', 'text', true],
                ['Téléphone', 'phone', 'tel', true],
                ['Email', 'email', 'email', false],
              ].map(([label, field, type, required]) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input
                    type={type}
                    required={required}
                    value={form[field]}
                    onChange={e => setForm({ ...form, [field]: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              ))}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Genre</label>
                <select
                  value={form.gender}
                  onChange={e => setForm({ ...form, gender: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="M">Masculin</option>
                  <option value="F">Féminin</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Groupe sanguin</label>
                <select
                  value={form.blood_group}
                  onChange={e => setForm({ ...form, blood_group: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">—</option>
                  {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(g => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Adresse</label>
                <input
                  type="text"
                  value={form.address}
                  onChange={e => setForm({ ...form, address: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Allergies connues</label>
                <textarea
                  value={form.allergies}
                  onChange={e => setForm({ ...form, allergies: e.target.value })}
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Antécédents médicaux</label>
                <textarea
                  value={form.medical_history}
                  onChange={e => setForm({ ...form, medical_history: e.target.value })}
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {error && (
                <div className="col-span-2 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="col-span-2 flex gap-3 justify-end mt-2">
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
                  {loading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}