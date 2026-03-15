import { useEffect, useState } from 'react'
import api from '../api/axios'
import { CalendarPlus } from 'lucide-react'

const STATUS_COLORS = {
  planned:     'bg-yellow-100 text-yellow-700',
  confirmed:   'bg-blue-100 text-blue-700',
  in_progress: 'bg-purple-100 text-purple-700',
  completed:   'bg-green-100 text-green-700',
  cancelled:   'bg-red-100 text-red-700',
}

const STATUS_LABELS = {
  planned: 'Planifié', confirmed: 'Confirmé',
  in_progress: 'En cours', completed: 'Terminé', cancelled: 'Annulé'
}

const EMPTY_FORM = {
  patient: '', doctor: '', scheduled_at: '',
  duration: 30, reason: '', status: 'planned'
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [patients, setPatients] = useState([])
  const [doctors, setDoctors] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [filterDate, setFilterDate] = useState('')

  const fetchAll = async () => {
    const params = filterDate ? `?date=${filterDate}` : ''
    const [appts, pts, users] = await Promise.all([
      api.get(`/api/appointments/${params}`),
      api.get('/api/patients/'),
      api.get('/api/users/doctors/'),
    ])
    setAppointments(appts.data.results || appts.data)
    setPatients(pts.data.results || pts.data)
    setDoctors((users.data.results || users.data).filter(u => u.role === 'doctor'))
  }

  useEffect(() => { fetchAll() }, [filterDate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/api/appointments/', form)
      setShowForm(false)
      setForm(EMPTY_FORM)
      fetchAll()
    } catch (err) {
      setError(err.response?.data?.non_field_errors?.[0] || 'Erreur lors de la création.')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (id, status) => {
    await api.patch(`/api/appointments/${id}/`, { status })
    fetchAll()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Rendez-vous</h1>
          <p className="text-gray-500 mt-1">{appointments.length} rendez-vous</p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="date"
            value={filterDate}
            onChange={e => setFilterDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-all"
          >
            <CalendarPlus size={18} /> Nouveau rendez-vous
          </button>
        </div>
      </div>

      {/* Liste */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 text-gray-600 text-sm">
            <tr>
              <th className="text-left px-6 py-3">Patient</th>
              <th className="text-left px-6 py-3">Médecin</th>
              <th className="text-left px-6 py-3">Date & Heure</th>
              <th className="text-left px-6 py-3">Durée</th>
              <th className="text-left px-6 py-3">Motif</th>
              <th className="text-left px-6 py-3">Statut</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {appointments.map(a => (
              <tr key={a.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-gray-800">
                  {a.patient_detail?.full_name || '—'}
                </td>
                <td className="px-6 py-4 text-gray-600">
                  Dr. {a.doctor_detail?.last_name || '—'}
                </td>
                <td className="px-6 py-4 text-gray-600">
                  {new Date(a.scheduled_at).toLocaleString('fr-FR', {
                    day: '2-digit', month: '2-digit', year: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                  })}
                </td>
                <td className="px-6 py-4 text-gray-600">{a.duration} min</td>
                <td className="px-6 py-4 text-gray-600">{a.reason}</td>
                <td className="px-6 py-4">
                  <select
                    value={a.status}
                    onChange={e => handleStatusChange(a.id, e.target.value)}
                    className={`text-xs font-medium px-2 py-1 rounded-full border-0 cursor-pointer ${STATUS_COLORS[a.status]}`}
                  >
                    {Object.entries(STATUS_LABELS).map(([v, l]) => (
                      <option key={v} value={v}>{l}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {appointments.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-12 text-gray-400">
                  Aucun rendez-vous trouvé
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-lg">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Nouveau rendez-vous</h2>
              <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Patient</label>
                <select
                  required
                  value={form.patient}
                  onChange={e => setForm({ ...form, patient: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sélectionner un patient</option>
                  {patients.map(p => (
                    <option key={p.id} value={p.id}>{p.full_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Médecin</label>
                <select
                  required
                  value={form.doctor}
                  onChange={e => setForm({ ...form, doctor: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sélectionner un médecin</option>
                  {doctors.map(d => (
                    <option key={d.id} value={d.id}>Dr. {d.last_name} {d.first_name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date et heure</label>
                  <input
                    type="datetime-local"
                    required
                    value={form.scheduled_at}
                    onChange={e => setForm({ ...form, scheduled_at: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Durée (min)</label>
                  <input
                    type="number"
                    min={15}
                    max={120}
                    value={form.duration}
                    onChange={e => setForm({ ...form, duration: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Motif de consultation</label>
                <input
                  type="text"
                  required
                  value={form.reason}
                  onChange={e => setForm({ ...form, reason: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Consultation de routine"
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