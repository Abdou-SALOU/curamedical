export function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Bonjour'
  if (h < 18) return 'Bon après-midi'
  return 'Bonsoir'
}

export const STATUS_LABELS = {
  DEMANDE:  'En attente',
  PLANIFIE: 'Planifié',
  CONFIRME: 'Confirmé',
  EN_COURS: 'En cours',
  TERMINE:  'Terminé',
  ANNULE:   'Annulé',
}

export const STATUS_COLORS = {
  DEMANDE:  'badge-sky',
  PLANIFIE: 'badge-amber',
  CONFIRME: 'badge-indigo',
  EN_COURS: 'badge-violet',
  TERMINE:  'badge-emerald',
  ANNULE:   'badge-rose',
}

export const API = {
  PATIENTS:      '/api/patients/',
  APPOINTMENTS:  '/api/appointments/',
  CONSULTATIONS: '/api/consultations/',
  PRESCRIPTIONS: '/api/prescriptions/',
  USERS:         '/api/users/',
  CHAT:          '/api/chat/',
  TOKEN:         '/api/token/',
}

export function handleApiError(err, toast) {
  const data = err?.response?.data
  if (!data) { toast?.error('Erreur réseau. Vérifiez votre connexion.'); return }
  if (typeof data === 'string') { toast?.error(data); return }
  const msgs = Object.values(data).flat().join(' ')
  toast?.error(msgs || 'Une erreur est survenue.')
}

// Map symptômes anglais → français (utilisé dans PatientProfilePage)
export const SYMPTOMS_MAP = {
  fever: 'Fièvre', high_fever: 'Fièvre élevée', mild_fever: 'Fièvre légère',
  chills: 'Frissons', sweating: 'Transpiration', fatigue: 'Fatigue',
  lethargy: 'Léthargie', cough: 'Toux', breathlessness: 'Dyspnée',
  chest_pain: 'Douleur thoracique', headache: 'Céphalées', dizziness: 'Vertiges',
  nausea: 'Nausées', vomiting: 'Vomissements', diarrhoea: 'Diarrhée',
  abdominal_pain: 'Douleur abdominale', stomach_pain: 'Douleur gastrique',
  constipation: 'Constipation', indigestion: 'Indigestion',
  back_pain: 'Douleur dorsale', joint_pain: 'Douleurs articulaires',
  muscle_pain: 'Myalgies', neck_stiffness: 'Raideur de nuque',
  skin_rash: 'Éruption cutanée', itching: 'Démangeaisons',
  yellowish_skin: 'Jaunisse', dark_urine: 'Urines foncées',
  weight_loss: 'Perte de poids', loss_of_appetite: 'Anorexie',
  swollen_lymph_nodes: 'Ganglions gonflés', runny_nose: 'Rhinorrhée',
  throat_irritation: 'Mal de gorge', redness_of_eyes: 'Yeux rouges',
  burning_micturition: 'Brûlure miction', fast_heart_rate: 'Tachycardie',
}

// Télécharger un blob binaire (PDF)
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
