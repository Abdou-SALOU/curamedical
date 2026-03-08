import { useEffect, useState } from 'react'
import api from '../api/axios'
import { FilePlus, Download, Trash2, Plus } from 'lucide-react'

const EMPTY_ITEM = {
  medication: '', dosage: '', frequency: '', duration: '', instructions: ''
}

const EMPTY_FORM = {
  consultation: '',
  notes: '',
  items: [{ ...EMPTY_ITEM }]
}

export default function PrescriptionsPage() {
  const [prescriptions, setPrescriptions] = useState([])
  const [consultations, setConsultations] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(null)
  const [error, setError] = useState('')

  const fetchAll = async () => {
    const [prescs, consults] = await Promise.all([
      api.get('/api/prescriptions/'),
      api.get('/api/consultations/'),
    ])
    setPrescriptions(prescs.data.results || prescs.data)
    setConsultations(consults.data.results || consults.data)
  }

  useEffect(() => { fetchAll() }, [])

  const handleItemChange = (index, field, value) => {
    setForm(prev => {
      const items = [...prev.items]
      items[index] = { ...items[index], [field]: value }
      return { ...prev, items }
    })
  }

  const addItem = () => {
    setForm(prev => ({ ...prev, items: [...prev.items, { ...EMPTY_ITEM }] }))
  }

  const removeItem = (index) => {
    setForm(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post('/api/prescriptions/', form)
      setShowForm(false)
      setForm(EMPTY_FORM)
      fetchAll()
    } catch (err) {
      setError('Erreur lors de la création de l\'ordonnance.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPDF = async (id) => {
    setDownloading(id)
    try {
      const response = await api.get(`/api/prescriptions/${id}/pdf/`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ordonnance_${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      alert('Erreur lors du téléchargement du PDF.')
    } finally {
      setDownloading(null)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Supprimer cette ordonnance ?')) return
    await api.delete(`/api/prescriptions/${id}/`)
    fetchAll()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Ordonnances</h1>
          <p className="text-gray-500 mt-1">{prescriptions.length} ordonnance(s)</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-all"
        >
          <FilePlus size={18} /> Nouvelle ordonnance
        </button>
      </div>

      {/* Liste */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 text-gray-600 text-sm">
            <tr>
              <th className="text-left px-6 py-3">Patient</th>
              <th className="text-left px-6 py-3">Médecin</th>
              <th className="text-left px-6 py-3">Médicaments</th>
              <th className="text-left px-6 py-3">Date</th>
              <th className="text-left px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {prescriptions.map(p => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 font-medium text-gray-800">
                  {p.patient_name || '—'}
                </td>
                <td className="px-6 py-4 text-gray-600">
                  {p.doctor_name || '—'}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {(p.items || []).slice(0, 3).map((item, i) => (
                      <span
                        key={i}
                        className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full"
                      >
                        {item.medication}
                      </span>
                    ))}
                    {(p.items || []).length > 3 && (
                      <span className="text-gray-400 text-xs">
                        +{p.items.length - 3} autres
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-500 text-sm">
                  {new Date(p.created_at).toLocaleDateString('fr-FR')}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDownloadPDF(p.id)}
                      disabled={downloading === p.id}
                      className="flex items-center gap-1 bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg text-sm font-medium transition-all disabled:opacity-50"
                    >
                      <Download size={14} />
                      {downloading === p.id ? 'PDF...' : 'PDF'}
                    </button>
                    <button
                      onClick={() => handleDelete(p.id)}
                      className="text-gray-400 hover:text-red-600 transition-all"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {prescriptions.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center py-12 text-gray-400">
                  Aucune ordonnance enregistrée
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Nouvelle ordonnance</h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >✕</button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Consultation */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Consultation associée
                </label>
                <select
                  required
                  value={form.consultation}
                  onChange={e => setForm({ ...form, consultation: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sélectionner une consultation</option>
                  {consultations.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.patient_name} — {c.diagnosis} —{' '}
                      {new Date(c.created_at).toLocaleDateString('fr-FR')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Médicaments */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Médicaments prescrits
                  </label>
                  <button
                    type="button"
                    onClick={addItem}
                    className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    <Plus size={16} /> Ajouter un médicament
                  </button>
                </div>

                <div className="space-y-4">
                  {form.items.map((item, index) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-xl p-4 bg-gray-50"
                    >
                      <div className="flex justify-between items-center mb-3">
                        <span className="font-medium text-gray-700 text-sm">
                          Médicament {index + 1}
                        </span>
                        {form.items.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeItem(index)}
                            className="text-red-400 hover:text-red-600"
                          >
                            <Trash2 size={15} />
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs text-gray-500 mb-1">
                            Médicament *
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="Ex: Amoxicilline"
                            value={item.medication}
                            onChange={e => handleItemChange(index, 'medication', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-500 mb-1">
                            Dosage *
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="Ex: 500mg"
                            value={item.dosage}
                            onChange={e => handleItemChange(index, 'dosage', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-500 mb-1">
                            Posologie *
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="Ex: 3 fois par jour"
                            value={item.frequency}
                            onChange={e => handleItemChange(index, 'frequency', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-500 mb-1">
                            Durée *
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="Ex: 7 jours"
                            value={item.duration}
                            onChange={e => handleItemChange(index, 'duration', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div className="col-span-2">
                          <label className="block text-xs text-gray-500 mb-1">
                            Instructions spéciales
                          </label>
                          <input
                            type="text"
                            placeholder="Ex: À prendre pendant les repas"
                            value={item.instructions}
                            onChange={e => handleItemChange(index, 'instructions', e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Instructions générales
                </label>
                <textarea
                  rows={2}
                  value={form.notes}
                  onChange={e => setForm({ ...form, notes: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Repos, hydratation, éviter..."
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
                  {loading ? 'Enregistrement...' : 'Créer l\'ordonnance'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}