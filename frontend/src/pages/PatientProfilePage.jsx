import { useEffect, useState } from 'react'
import api from '../api/axios'
import { toast } from '../store/toastStore'
import { SkeletonPanel } from '../components/Skeleton'
import { STATUS_LABELS, STATUS_COLORS, SYMPTOMS_MAP, downloadBlob } from '../utils/constants'
import {
  User, Phone, Mail, MapPin, Droplets, ShieldAlert,
  Calendar, Stethoscope, FileText, Download, Activity, Sparkles,
} from 'lucide-react'

function InfoRow({ icon: Icon, label, value, iconClass = 'text-emerald-600' }) {
  return (
    <div className="info-tile flex items-center gap-3">
      <Icon size={16} className={`shrink-0 ${iconClass}`} />
      <div className="min-w-0">
        <p className="label-xs text-slate-400">{label}</p>
        <p className="text-sm font-semibold text-slate-200 truncate">{value || '—'}</p>
      </div>
    </div>
  )
}

export default function PatientProfilePage() {
  const [profile, setProfile]           = useState(null)
  const [appointments, setAppointments] = useState([])
  const [consultations, setConsultations] = useState([])
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading]           = useState(true)
  const [downloadingPdf, setDownloadingPdf] = useState(null)

  useEffect(() => {
    const fetchAll = async () => {
      const [profRes, apptRes, consultRes, prescRes] = await Promise.allSettled([
        api.get('/api/patients/mes-infos/'),
        api.get('/api/appointments/?page_size=5'),
        api.get('/api/consultations/?page_size=5'),
        api.get('/api/prescriptions/?page_size=5'),
      ])
      if (profRes.status === 'fulfilled') {
        setProfile(profRes.value.data)
      } else {
        toast.error('Impossible de charger votre profil.')
      }
      if (apptRes.status === 'fulfilled')    setAppointments(apptRes.value.data.results ?? apptRes.value.data)
      if (consultRes.status === 'fulfilled') setConsultations(consultRes.value.data.results ?? consultRes.value.data)
      if (prescRes.status === 'fulfilled')   setPrescriptions(prescRes.value.data.results ?? prescRes.value.data)
      setLoading(false)
    }
    fetchAll()
  }, [])

  const handleDownloadPrescription = async (id) => {
    setDownloadingPdf(id)
    try {
      const { data } = await api.get(`/api/prescriptions/${id}/ordonnance-pdf/`, { responseType: 'blob' })
      downloadBlob(data, `ordonnance_${id}.pdf`)
      toast.success('Ordonnance téléchargée !')
    } catch {
      toast.error('Erreur lors du téléchargement.')
    } finally {
      setDownloadingPdf(null)
    }
  }

  if (loading) return (
    <div className="p-6 md:p-8 max-w-[900px] mx-auto">
      <SkeletonPanel />
    </div>
  )

  if (!profile) return (
    <div className="p-6 md:p-8 flex flex-col items-center justify-center min-h-[50vh] text-center">
      <div className="w-16 h-16 rounded-2xl bg-amber-50 flex items-center justify-center mb-4">
        <User size={28} className="text-amber-500" />
      </div>
      <h2 className="section-title text-xl font-black text-slate-200">Dossier patient introuvable</h2>
      <p className="mt-2 text-sm text-slate-400 max-w-xs leading-6">
        Votre compte n'est pas encore lié à un dossier patient. Contactez votre secrétariat.
      </p>
    </div>
  )

  return (
    <div className="p-5 md:p-8 max-w-[1100px] mx-auto space-y-6 page-enter">

      {/* ── Header ── */}
      <section className="surface-panel rounded-3xl px-6 py-5">
        <div className="flex flex-col sm:flex-row gap-5 sm:items-center">
          {/* Avatar */}
          <div className="avatar-patient w-20 h-20 rounded-[1.6rem] flex items-center justify-center text-white text-2xl font-black shrink-0">
            {`${profile.prenom?.[0] || ''}${profile.nom?.[0] || ''}`.toUpperCase() || '?'}
          </div>

          <div className="flex-1">
            <p className="label-xs text-emerald-700">Mon dossier médical</p>
            <h1 className="section-title mt-1 text-3xl font-black text-slate-200">
              {profile.prenom} {profile.nom}
            </h1>
            <div className="flex flex-wrap items-center gap-2 mt-2">
              {profile.groupe_sanguin && (
                <span className="badge badge-rose">{profile.groupe_sanguin}</span>
              )}
              <span className="badge badge-slate">
                {profile.sexe === 'M' ? 'Masculin' : 'Féminin'}
              </span>
              {profile.age && (
                <span className="badge badge-slate">{profile.age} ans</span>
              )}
            </div>
          </div>

          <div className="shrink-0">
            <p className="label-xs text-slate-400 mb-1">CIN</p>
            <p className="text-sm font-bold text-slate-200 font-mono">{profile.cin || '—'}</p>
          </div>
        </div>
      </section>

      {/* ── Main grid ── */}
      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">

        {/* ── Left column: personal info ── */}
        <div className="space-y-4">

          {/* Contact */}
          <div className="surface-panel rounded-3xl p-5 space-y-3">
            <p className="label-xs text-slate-400">Informations personnelles</p>
            <div className="space-y-2">
              <InfoRow icon={Phone}  label="Téléphone"       value={profile.telephone}     iconClass="text-emerald-600" />
              <InfoRow icon={Mail}   label="Email"           value={profile.email}         iconClass="text-indigo-500" />
              <InfoRow icon={MapPin} label="Adresse"         value={profile.adresse}       iconClass="text-amber-500" />
              <InfoRow icon={Calendar} label="Date de naissance" value={profile.date_naissance} iconClass="text-violet-500" />
              <InfoRow icon={Droplets} label="Groupe sanguin"  value={profile.groupe_sanguin} iconClass="text-rose-500" />
            </div>
          </div>

          {/* Medical info */}
          <div className="surface-panel rounded-3xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <ShieldAlert size={16} className="text-amber-400" />
              <p className="text-sm font-bold text-amber-300">Informations cliniques</p>
            </div>
            <div className="space-y-4">
              {[
                { label: 'Allergies',           val: profile.allergies,            empty: 'Aucune allergie connue.' },
                { label: 'Antécédents médicaux', val: profile.antecedents_medicaux, empty: 'Aucun antécédent saisi.' },
              ].map(({ label, val, empty }) => (
                <div key={label}>
                  <p className="label-xs mb-1.5">{label}</p>
                  <p className="text-sm text-slate-400 leading-6 bg-white/4 rounded-xl px-3 py-2.5 border border-white/7">
                    {val || <span className="text-slate-400 italic">{empty}</span>}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right column: activity ── */}
        <div className="space-y-4">

          {/* Recent appointments */}
          <div className="surface-panel rounded-3xl overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center">
                <Calendar size={18} className="text-indigo-500" />
              </div>
              <div>
                <p className="label-xs text-slate-400">Planning</p>
                <h3 className="section-title text-base font-black text-slate-200">Mes rendez-vous récents</h3>
              </div>
            </div>
            {appointments.length === 0 ? (
              <div className="py-10 text-center text-sm text-slate-400">Aucun rendez-vous enregistré</div>
            ) : (
              <ul className="divide-y divide-white/7">
                {appointments.map(a => (
                  <li key={a.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-white/4 transition-colors">
                    <div>
                      <p className="text-sm font-semibold text-slate-200">
                        {a.motif || 'Rendez-vous médical'}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {a.medecin_nom || '—'} ·{' '}
                        {new Date(a.date_heure).toLocaleString('fr-FR', {
                          day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit',
                        })}
                      </p>
                    </div>
                    <span className={`badge ${STATUS_COLORS[a.statut] || 'badge-slate'}`}>
                      {STATUS_LABELS[a.statut] || a.statut}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Recent consultations */}
          <div className="surface-panel rounded-3xl overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 flex items-center justify-center">
                <Stethoscope size={18} className="text-emerald-600" />
              </div>
              <div>
                <p className="label-xs text-slate-400">Suivi clinique</p>
                <h3 className="section-title text-base font-black text-slate-200">Mes consultations récentes</h3>
              </div>
            </div>
            {consultations.length === 0 ? (
              <div className="py-10 text-center text-sm text-slate-400">Aucune consultation enregistrée</div>
            ) : (
              <ul className="divide-y divide-white/7">
                {consultations.map(c => (
                  <li key={c.id} className="px-5 py-3.5 hover:bg-white/4 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-200 truncate">{c.diagnostic || 'Diagnostic non renseigné'}</p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {new Date(c.date_consultation).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })}
                        </p>
                      </div>
                      {c.ia_utilisee && (
                        <span className="badge badge-amber shrink-0">
                          <Sparkles size={10} /> IA
                        </span>
                      )}
                    </div>
                    {c.symptomes?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {c.symptomes.slice(0, 4).map(s => (
                          <span key={s} className="badge badge-slate text-[10px]">
                            {SYMPTOMS_MAP[s] || s}
                          </span>
                        ))}
                        {c.symptomes.length > 4 && (
                          <span className="badge badge-slate text-[10px]">+{c.symptomes.length - 4}</span>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Prescriptions */}
          <div className="surface-panel rounded-3xl overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-violet-50 flex items-center justify-center">
                <FileText size={18} className="text-violet-500" />
              </div>
              <div>
                <p className="label-xs text-slate-400">Documents</p>
                <h3 className="section-title text-base font-black text-slate-200">Mes ordonnances</h3>
              </div>
            </div>
            {prescriptions.length === 0 ? (
              <div className="py-10 text-center text-sm text-slate-400">Aucune ordonnance disponible</div>
            ) : (
              <ul className="divide-y divide-white/7">
                {prescriptions.map(p => (
                  <li key={p.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-white/4 transition-colors">
                    <div>
                      <p className="text-sm font-semibold text-slate-200">
                        {(p.lignes || []).map(l => l.medicament).join(', ') || 'Ordonnance'}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {new Date(p.cree_le).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })}
                      </p>
                    </div>
                    <button
                      onClick={() => handleDownloadPrescription(p.id)}
                      disabled={downloadingPdf === p.id}
                      className="flex items-center gap-1.5 badge badge-indigo hover:bg-indigo-200 transition-colors cursor-pointer disabled:opacity-50"
                    >
                      {downloadingPdf === p.id ? (
                        <span className="w-3 h-3 border-2 border-indigo-400/30 border-t-indigo-600 rounded-full animate-spin" />
                      ) : (
                        <Download size={11} />
                      )}
                      PDF
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
