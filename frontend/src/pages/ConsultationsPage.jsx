import { useEffect, useState } from 'react'
import api from '../api/axios'
import { FilePlus, Brain, AlertTriangle } from 'lucide-react'

const SYMPTOMS_LIST = [
  'fever', 'cough', 'fatigue', 'difficulty_breathing'
]

const EMPTY_FORM = {
  appointment: '',
  symptoms: [],
  clinical_exam: '',
  diagnosis: '',
  notes: '',
  ia_suggestions: null,
  ia_used: false
}

const EMPTY_IA_PARAMS = {
  age: 30,
  gender: 'M',
  blood_pressure: 'Normal',
  cholesterol: 'Normal'
}

export default function ConsultationsPage() {
  const [consultations, setConsultations] = useState([])
  const [appointments, setAppointments] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [iaParams, setIaParams] = useState(EMPTY_IA_PARAMS)
  const [loading, setLoading] = useState(false)
  const [iaLoading, setIaLoading] = useState(false)
  const [iaSuggestions, setIaSuggestions] = useState(null)
  const [iaError, setIaError] = useState('')
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)

  const fetchAll = async () => {
    const [consults, appts] = await Promise.all([
      api.get('/api/consultations/'),
      api.get('/api/appointments/'),
    ])
    setConsultations(consults.data.results || consults.data)
    setAppointments(appts.data.results || appts.data)
  }

  useEffect(() => { fetchAll() }, [])

  const toggleSymptom = (symptom) => {
    setIaSuggestions(null)
    setForm(prev => ({
      ...prev,
      symptoms: prev.symptoms.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...prev.symptoms, symptom]
    }))
  }

  const handleAskIA = async () => {
    if (form.symptoms.length === 0) {
      setIaError('Sélectionnez au moins un symptôme.')
      return
    }
    setIaLoading(true)
    setIaError('')
    setIaSuggestions(null)
    try {
      const { data } = await api.post('/api/consultations/ia/suggest/', {
        symptoms: form.symptoms,
        age: iaParams.age,
        gender: iaParams.gender,
        blood_pressure: iaParams.blood_pressure,
        cholesterol: iaParams.cholesterol,
      })
      setIaSuggestions(data.suggestions)
      setForm(prev => ({
        ...prev,
        ia_suggestions: data.suggestions,
        ia_used: true
      }))
    } catch {
      setIaError('Service IA temporairement indisponible.')
    } finally {
      setIaLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const payload = {
        appointment: parseInt(form.appointment),
        symptoms: form.symptoms,
        clinical_exam: form.clinical_exam,
        diagnosis: form.diagnosis,
        notes: form.notes,
        ia_suggestions: form.ia_suggestions,
        ia_used: form.ia_used,
      }
      await api.post('/api/consultations/', payload)
      setShowForm(false)
      setForm(EMPTY_FORM)
      setIaParams(EMPTY_IA_PARAMS)
      setIaSuggestions(null)
      fetchAll()
    } catch (err) {
      setError(JSON.stringify(err.response?.data) || 'Erreur lors de la création.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Consultations</h1>
          <p className="text-gray-500 mt-1">{consultations.length} consultation(s)</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-all"
        >
          <FilePlus size={18} /> Nouvelle consultation
        </button>
      </div>

      {/* Liste des consultations */}
      <div className="flex gap-6">
        <div className="flex-1 bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 text-gray-600 text-sm">
              <tr>
                <th className="text-left px-6 py-3">Patient</th>
                <th className="text-left px-6 py-3">Médecin</th>
                <th className="text-left px-6 py-3">Diagnostic</th>
                <th className="text-left px-6 py-3">IA</th>
                <th className="text-left px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {consultations.map(c => (
                <tr
                  key={c.id}
                  onClick={() => setSelected(c)}
                  className={`hover:bg-gray-50 cursor-pointer transition-all ${
                    selected?.id === c.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <td className="px-6 py-4 font-medium text-gray-800">
                    {c.patient_name || '—'}
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {c.appointment_detail?.doctor_detail?.last_name
                      ? `Dr. ${c.appointment_detail.doctor_detail.last_name}`
                      : '—'}
                  </td>
                  <td className="px-6 py-4 text-gray-700">{c.diagnosis}</td>
                  <td className="px-6 py-4">
                    {c.ia_used
                      ? <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full font-medium">✓ IA consultée</span>
                      : <span className="text-gray-300 text-xs">—</span>
                    }
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    {new Date(c.created_at).toLocaleDateString('fr-FR')}
                  </td>
                </tr>
              ))}
              {consultations.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-gray-400">
                    Aucune consultation enregistrée
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Détail consultation */}
        {selected && (
          <div className="w-80 bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-bold text-gray-800">Détail</h2>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-gray-500 text-xs mb-1">Symptômes</p>
                <div className="flex flex-wrap gap-1">
                  {(selected.symptoms || []).map(s => (
                    <span key={s} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs">
                      {s.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-gray-500 text-xs mb-1">Examen clinique</p>
                <p className="text-gray-700">{selected.clinical_exam || '—'}</p>
              </div>
              <div>
                <p className="text-gray-500 text-xs mb-1">Diagnostic</p>
                <p className="font-semibold text-gray-800">{selected.diagnosis}</p>
              </div>
              {selected.ia_suggestions && (
                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-purple-700 font-medium text-xs mb-2">🤖 Suggestions IA</p>
                  {selected.ia_suggestions.map((s, i) => (
                    <div key={i} className="flex justify-between text-xs mb-1">
                      <span className="text-gray-700">{s.disease}</span>
                      <span className="font-bold text-purple-600">{s.confidence}%</span>
                    </div>
                  ))}
                </div>
              )}
              {selected.notes && (
                <div>
                  <p className="text-gray-500 text-xs mb-1">Notes</p>
                  <p className="text-gray-700 text-xs bg-gray-50 p-2 rounded">{selected.notes}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modal nouvelle consultation */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Nouvelle consultation</h2>
              <button
                onClick={() => { setShowForm(false); setIaSuggestions(null) }}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >✕</button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Rendez-vous */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rendez-vous associé
                </label>
                <select
                  required
                  value={form.appointment}
                  onChange={e => setForm({ ...form, appointment: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sélectionner un rendez-vous</option>
                  {appointments.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.patient_detail?.full_name} —{' '}
                      {new Date(a.scheduled_at).toLocaleString('fr-FR', {
                        day: '2-digit', month: '2-digit',
                        hour: '2-digit', minute: '2-digit'
                      })}
                    </option>
                  ))}
                </select>
              </div>

              {/* Symptômes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Symptômes observés
                  <span className="text-gray-400 font-normal ml-2">
                    ({form.symptoms.length} sélectionné(s))
                  </span>
                </label>
                <div className="flex flex-wrap gap-2 p-3 border border-gray-300 rounded-lg bg-gray-50">
                  {SYMPTOMS_LIST.map(s => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => toggleSymptom(s)}
                      className={`px-3 py-1 rounded-full text-sm transition-all ${
                        form.symptoms.includes(s)
                          ? 'bg-blue-600 text-white font-medium'
                          : 'bg-white text-gray-600 border border-gray-300 hover:border-blue-400'
                      }`}
                    >
                      {s.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </div>

              {/* Module IA */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Brain size={20} className="text-purple-600" />
                    <span className="font-semibold text-gray-800">Assistant IA</span>
                  </div>
                  <button
                    type="button"
                    onClick={handleAskIA}
                    disabled={iaLoading || form.symptoms.length === 0}
                    className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 transition-all"
                  >
                    {iaLoading ? '⏳ Analyse...' : '🔍 Analyser les symptômes'}
                  </button>
                </div>

                {/* Paramètres patient pour l'IA */}
                <div className="grid grid-cols-4 gap-3 mb-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Âge</label>
                    <input
                      type="number"
                      min={1} max={120}
                      value={iaParams.age}
                      onChange={e => setIaParams({ ...iaParams, age: parseInt(e.target.value) })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Genre</label>
                    <select
                      value={iaParams.gender}
                      onChange={e => setIaParams({ ...iaParams, gender: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="M">Masculin</option>
                      <option value="F">Féminin</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Pression</label>
                    <select
                      value={iaParams.blood_pressure}
                      onChange={e => setIaParams({ ...iaParams, blood_pressure: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="Low">Basse</option>
                      <option value="Normal">Normale</option>
                      <option value="High">Haute</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Cholestérol</label>
                    <select
                      value={iaParams.cholesterol}
                      onChange={e => setIaParams({ ...iaParams, cholesterol: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="Low">Bas</option>
                      <option value="Normal">Normal</option>
                      <option value="High">Élevé</option>
                    </select>
                  </div>
                </div>

                {/* Avertissement */}
                <div className="flex items-center gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-3">
                  <AlertTriangle size={14} />
                  Outil d'aide — ne remplace pas le diagnostic médical
                </div>

                {/* Erreur IA */}
                {iaError && (
                  <p className="text-red-600 text-sm">{iaError}</p>
                )}

                {/* Résultats IA */}
                {iaSuggestions && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700">Top 3 pathologies probables :</p>
                    {iaSuggestions.map((s, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <span className="text-xs w-4 text-gray-500">{i + 1}.</span>
                        <div className="flex-1">
                          <div className="flex justify-between text-sm mb-0.5">
                            <span
                              className="font-medium text-gray-800 cursor-pointer hover:text-blue-600"
                              onClick={() => setForm(prev => ({ ...prev, diagnosis: s.disease }))}
                              title="Cliquer pour utiliser comme diagnostic"
                            >
                              {s.disease}
                            </span>
                            <span className="font-bold text-purple-600">{s.confidence}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-purple-500 h-1.5 rounded-full"
                              style={{ width: `${s.confidence}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                    <p className="text-xs text-gray-400 mt-2">
                      💡 Cliquez sur un diagnostic pour l'utiliser
                    </p>
                  </div>
                )}
              </div>

              {/* Examen clinique */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Examen clinique
                </label>
                <textarea
                  rows={3}
                  value={form.clinical_exam}
                  onChange={e => setForm({ ...form, clinical_exam: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Résultats de l'examen clinique..."
                />
              </div>

              {/* Diagnostic */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Diagnostic retenu <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={form.diagnosis}
                  onChange={e => setForm({ ...form, diagnosis: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Diagnostic du médecin..."
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  rows={2}
                  value={form.notes}
                  onChange={e => setForm({ ...form, notes: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Notes complémentaires..."
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
                  onClick={() => { setShowForm(false); setIaSuggestions(null) }}
                  className="px-6 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? 'Enregistrement...' : 'Enregistrer la consultation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}