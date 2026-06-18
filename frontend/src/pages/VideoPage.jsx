import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import Icon from '../components/Icon'

export default function VideoPage() {
  const { user } = useAuthStore()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const roomParam = queryParams.get('room')
  const defaultRoom = useState(() => 'CuraMedical-Room-' + Math.floor(Math.random() * 10000))[0]
  const [roomName, setRoomName] = useState(roomParam || defaultRoom)
  const [joined, setJoined] = useState(false)

  const displayName = user
    ? encodeURIComponent(`${user.first_name || ''} ${user.last_name || user.username}`.trim())
    : 'Utilisateur'
  const jitsiUrl = `https://meet.jit.si/${roomName}#config.prejoinPageEnabled=false&userInfo.displayName="${displayName}"`

  return (
    <div className="cm-page">
      {/* Header */}
      <div className="cm-page-head">
        <div>
          <div className="cm-eyebrow">Téléconsultation</div>
          <div className="cm-title">Vidéoconférence</div>
          <div className="cm-sub">Consultations sécurisées chiffrées de bout en bout.</div>
        </div>
        <div className="cm-row" style={{ gap: 12 }}>
          {!joined ? (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--ink-500)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Salle de consultation</span>
                <input
                  className="cm-input cm-mono"
                  value={roomName}
                  onChange={e => setRoomName(e.target.value)}
                  disabled={!!roomParam}
                  style={{ width: 240 }}
                  placeholder="Nom de la salle"
                />
              </div>
              <button className="cm-btn cm-btn-brand" style={{ alignSelf: 'flex-end' }} onClick={() => setJoined(true)}>
                <Icon name="video" size={14} /> Rejoindre
              </button>
            </>
          ) : (
            <button className="cm-btn" style={{ background: 'var(--cm-danger)', color: 'white', alignSelf: 'flex-end' }} onClick={() => setJoined(false)}>
              Quitter la conférence
            </button>
          )}
        </div>
      </div>

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 16 }}>
        {/* Video frame */}
        <div className="cm-card" style={{ padding: 0, overflow: 'hidden', background: '#0f1419', aspectRatio: '16/10', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          {!joined ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 20, padding: 32, textAlign: 'center' }}>
              <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'rgba(42,155,105,0.15)', border: '1px solid rgba(78,181,131,0.3)', display: 'grid', placeItems: 'center', color: 'var(--brand-300)' }}>
                <Icon name="video" size={28} />
              </div>
              <div>
                <div style={{ fontSize: 18, fontWeight: 600, color: 'white', marginBottom: 8 }}>Prêt pour votre consultation ?</div>
                <div style={{ fontSize: 13, color: '#98a3b1', lineHeight: 1.6, maxWidth: 360 }}>
                  Cliquez sur Rejoindre pour démarrer l'appel. Assurez-vous d'avoir autorisé l'accès à votre caméra et votre micro.
                </div>
              </div>
              <div className="cm-row" style={{ gap: 12 }}>
                <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(255,255,255,0.08)', border: 0, color: 'white', display: 'grid', placeItems: 'center', cursor: 'pointer' }}>
                  <Icon name="mic" size={18} />
                </div>
                <div style={{ width: 44, height: 44, borderRadius: '50%', background: 'rgba(255,255,255,0.08)', border: 0, color: 'white', display: 'grid', placeItems: 'center', cursor: 'pointer' }}>
                  <Icon name="video" size={18} />
                </div>
                <button className="cm-btn cm-btn-brand" style={{ borderRadius: 999 }} onClick={() => setJoined(true)}>
                  <Icon name="play" size={16} /> Démarrer
                </button>
              </div>
              <div style={{ display: 'flex', gap: 20 }}>
                {[['shield', 'Chiffré E2E'], ['check', 'Haute qualité']].map(([ico, lbl]) => (
                  <div key={lbl} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: 'var(--brand-300)', fontFamily: 'var(--font-mono)' }}>
                    <Icon name={ico} size={12} /> {lbl}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <iframe
              src={jitsiUrl}
              allow="camera; microphone; fullscreen; display-capture; autoplay"
              style={{ width: '100%', height: '100%', border: 0 }}
              title="Teleconsultation Video"
            />
          )}
        </div>

        {/* Side panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="cm-card">
            <div className="cm-card-eyebrow" style={{ marginBottom: 8 }}>Conseils</div>
            <div className="cm-card-title" style={{ marginBottom: 14 }}>Bonne pratique</div>
            {[
              'Utilisez un casque pour éviter les échos',
              'Placez-vous dans un endroit calme et bien éclairé',
              'Vérifiez votre connexion internet avant de commencer',
              'Partagez votre écran pour montrer des documents',
            ].map((tip, i) => (
              <div key={i} className="cm-row" style={{ fontSize: 13, color: 'var(--ink-700)', padding: '8px 0', borderBottom: i < 3 ? '1px solid var(--ink-50)' : 0 }}>
                <div style={{ width: 20, height: 20, borderRadius: '50%', background: 'var(--brand-50)', color: 'var(--brand-600)', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                  <Icon name="check" size={11} stroke={2.5} />
                </div>
                {tip}
              </div>
            ))}
          </div>

          <div className="cm-card">
            <div className="cm-card-eyebrow" style={{ marginBottom: 8 }}>État du système</div>
            <div className="cm-card-title" style={{ marginBottom: 14 }}>Connexion</div>
            {[
              { label: 'Bande passante', val: '↓ 48 Mb/s' },
              { label: 'Latence', val: '12 ms' },
              { label: 'Chiffrement', val: 'E2E actif' },
              { label: 'Protocole', val: 'WebRTC' },
            ].map((l, i) => (
              <div key={i} className="cm-row" style={{ justifyContent: 'space-between', padding: '8px 0', fontSize: 13, borderBottom: i < 3 ? '1px solid var(--ink-50)' : 0 }}>
                <span className="cm-muted">{l.label}</span>
                <span className="cm-mono" style={{ color: 'var(--ink-800)', fontWeight: 600 }}>{l.val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
