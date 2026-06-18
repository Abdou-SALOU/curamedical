import { useState } from 'react'
import Icon from './Icon'

const BLOOD_TYPES = ['A+', 'A−', 'B+', 'B−', 'AB+', 'AB−', 'O+', 'O−']
const COMMON_ALLERGIES = ['Pénicilline', 'Aspirine', 'Iode', 'Arachides', 'Latex', 'Pollen', 'Acariens']
const DOCTORS = ['Dr. Hakimi', 'Dr. El Mansouri', 'Dr. Benali', 'Dr. Cherkaoui']

const EMPTY = {
  firstName: '', lastName: '', dob: '', gender: 'F',
  phone: '', email: '', address: '', city: '',
  cin: '', insurance: 'CNSS', insuranceNum: '',
  blood: '', weight: '', height: '',
  allergies: [], antecedents: '', treatments: '',
  doctor: 'Dr. Hakimi', notes: '',
}

export default function AddPatientModal({ onClose, onSave }) {
  const [form, setForm] = useState(EMPTY)
  const [allergyInput, setAllergyInput] = useState('')
  const [step, setStep] = useState(1)

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const addAllergy = (a) => {
    const v = a.trim()
    if (!v || form.allergies.includes(v)) return
    update('allergies', [...form.allergies, v])
    setAllergyInput('')
  }
  const removeAllergy = (a) => update('allergies', form.allergies.filter(x => x !== a))

  const canNext = step === 1 ? !!(form.firstName && form.lastName && form.dob) : true
  const canSave = !!(form.firstName && form.lastName && form.dob && form.phone)

  const handleSave = () => {
    if (!canSave) return
    const age = form.dob ? new Date().getFullYear() - new Date(form.dob).getFullYear() : 0
    onSave({
      name: `${form.firstName} ${form.lastName}`,
      prenom: form.firstName, nom: form.lastName,
      date_naissance: form.dob, sexe: form.gender,
      telephone: form.phone, email: form.email,
      adresse: form.address, cin: form.cin,
      groupe_sanguin: form.blood,
      allergies: form.allergies.join(', '),
      antecedents_medicaux: form.antecedents,
      age, lastVisit: new Date().toISOString().slice(0, 10),
      status: 'Nouveau', dx: 'Première visite',
    })
  }

  return (
    <div className="modal-backdrop-cm" onClick={onClose}>
      <div className="modal-cm" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-head-cm">
          <div>
            <div className="modal-title-cm">Nouveau patient</div>
            <div className="modal-sub-cm">Création d'un dossier médical · Étape {step}/3</div>
          </div>
          <button className="modal-close-cm" onClick={onClose}>
            <Icon name="x" size={14} stroke={2.4} />
          </button>
        </div>

        {/* Progress bar */}
        <div style={{ padding: '16px 28px 0', display: 'flex', gap: 6 }}>
          {[1, 2, 3].map(i => (
            <div key={i} style={{
              flex: 1, height: 3, borderRadius: 2,
              background: i <= step ? 'var(--brand-500)' : 'var(--ink-100)',
              transition: 'background .25s',
            }} />
          ))}
        </div>

        {/* Body */}
        <div className="modal-body-cm">
          {step === 1 && (
            <div className="form-section-cm">
              <div className="form-section-title-cm"><Icon name="user" size={12} /> Identité</div>
              <div className="form-grid-cm">
                <div className="form-field-cm">
                  <label className="form-label-cm">Prénom <span className="req">*</span></label>
                  <input className="form-input-cm" value={form.firstName} onChange={e => update('firstName', e.target.value)} placeholder="Karim" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Nom <span className="req">*</span></label>
                  <input className="form-input-cm" value={form.lastName} onChange={e => update('lastName', e.target.value)} placeholder="Bensalem" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Date de naissance <span className="req">*</span></label>
                  <input className="form-input-cm" type="date" value={form.dob} onChange={e => update('dob', e.target.value)} />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Sexe</label>
                  <div className="radio-grid-cm">
                    {[['F', 'Femme'], ['M', 'Homme'], ['O', 'Autre']].map(([v, l]) => (
                      <div key={v} className={`radio-card-cm ${form.gender === v ? 'active' : ''}`} onClick={() => update('gender', v)}>{l}</div>
                    ))}
                  </div>
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">CIN / Pièce d'identité</label>
                  <input className="form-input-cm" value={form.cin} onChange={e => update('cin', e.target.value)} placeholder="BK123456" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Médecin traitant</label>
                  <select className="form-select-cm" value={form.doctor} onChange={e => update('doctor', e.target.value)}>
                    {DOCTORS.map(d => <option key={d}>{d}</option>)}
                  </select>
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="form-section-cm">
              <div className="form-section-title-cm"><Icon name="phone" size={12} /> Coordonnées</div>
              <div className="form-grid-cm">
                <div className="form-field-cm">
                  <label className="form-label-cm">Téléphone <span className="req">*</span></label>
                  <input className="form-input-cm" value={form.phone} onChange={e => update('phone', e.target.value)} placeholder="+212 661 23 45 67" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Email</label>
                  <input className="form-input-cm" type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="karim@email.com" />
                </div>
                <div className="form-field-cm full">
                  <label className="form-label-cm">Adresse</label>
                  <input className="form-input-cm" value={form.address} onChange={e => update('address', e.target.value)} placeholder="12 rue Hassan II, Apt 4" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Ville</label>
                  <input className="form-input-cm" value={form.city} onChange={e => update('city', e.target.value)} placeholder="Casablanca" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Assurance</label>
                  <select className="form-select-cm" value={form.insurance} onChange={e => update('insurance', e.target.value)}>
                    {['CNSS', 'CNOPS', 'RAMED', 'Privée', 'Aucune'].map(o => <option key={o}>{o}</option>)}
                  </select>
                </div>
                <div className="form-field-cm full">
                  <label className="form-label-cm">N° d'assurance</label>
                  <input className="form-input-cm" value={form.insuranceNum} onChange={e => update('insuranceNum', e.target.value)} placeholder="AS-2026-001234" />
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="form-section-cm">
              <div className="form-section-title-cm"><Icon name="stethoscope" size={12} /> Informations médicales</div>
              <div className="form-grid-3-cm">
                <div className="form-field-cm">
                  <label className="form-label-cm">Groupe sanguin</label>
                  <select className="form-select-cm" value={form.blood} onChange={e => update('blood', e.target.value)}>
                    <option value="">—</option>
                    {BLOOD_TYPES.map(b => <option key={b}>{b}</option>)}
                  </select>
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Poids (kg)</label>
                  <input className="form-input-cm" type="number" value={form.weight} onChange={e => update('weight', e.target.value)} placeholder="72" />
                </div>
                <div className="form-field-cm">
                  <label className="form-label-cm">Taille (cm)</label>
                  <input className="form-input-cm" type="number" value={form.height} onChange={e => update('height', e.target.value)} placeholder="175" />
                </div>
              </div>

              <div className="form-field-cm" style={{ marginTop: 4 }}>
                <label className="form-label-cm">Allergies connues</label>
                <div className="chips-input-cm">
                  {form.allergies.map(a => (
                    <span key={a} className="chip-cm">
                      {a}<span className="chip-x-cm" onClick={() => removeAllergy(a)}>×</span>
                    </span>
                  ))}
                  <input
                    className="chip-input-cm"
                    value={allergyInput}
                    onChange={e => setAllergyInput(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addAllergy(allergyInput) } }}
                    placeholder={form.allergies.length ? '' : 'Tapez puis Entrée…'}
                  />
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 6 }}>
                  {COMMON_ALLERGIES.filter(a => !form.allergies.includes(a)).map(a => (
                    <button key={a} className="chip-cm" style={{ background: 'var(--ink-50)', color: 'var(--ink-600)', border: 0, cursor: 'pointer' }} onClick={() => addAllergy(a)}>+ {a}</button>
                  ))}
                </div>
              </div>

              <div className="form-field-cm">
                <label className="form-label-cm">Antécédents médicaux</label>
                <textarea className="form-textarea-cm" value={form.antecedents} onChange={e => update('antecedents', e.target.value)} placeholder="Hypertension depuis 2018…" />
              </div>
              <div className="form-field-cm">
                <label className="form-label-cm">Traitements en cours</label>
                <textarea className="form-textarea-cm" value={form.treatments} onChange={e => update('treatments', e.target.value)} placeholder="Amlodipine 5mg, 1cp/jour…" />
              </div>
              <div className="form-field-cm">
                <label className="form-label-cm">Notes</label>
                <textarea className="form-textarea-cm" value={form.notes} onChange={e => update('notes', e.target.value)} placeholder="Observations particulières…" />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-foot-cm">
          <div style={{ fontSize: 11, color: 'var(--ink-500)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Icon name="lock" size={12} /> Données chiffrées · conforme HDS
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {step > 1 && <button className="btn-ghost-cm" onClick={() => setStep(step - 1)}>Précédent</button>}
            <button className="btn-ghost-cm" onClick={onClose}>Annuler</button>
            {step < 3 && (
              <button className="btn-brand-cm" disabled={!canNext} onClick={() => setStep(step + 1)}>
                Suivant <Icon name="chevron" size={13} />
              </button>
            )}
            {step === 3 && (
              <button className="btn-brand-cm" disabled={!canSave} onClick={handleSave}>
                <Icon name="check" size={13} /> Créer le dossier
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
