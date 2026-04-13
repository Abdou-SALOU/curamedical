import { useState } from 'react'
import useAuthStore from '../store/authStore'

import { useLocation } from 'react-router-dom'

export default function VideoPage() {
  const { user } = useAuthStore()
  const location = useLocation()
  
  // Try to parse room name from URL query params
  const queryParams = new URLSearchParams(location.search)
  const roomParam = queryParams.get('room')
  
  // Génération d'un nom de salle unique par défaut si non fourni
  const defaultRoom = useState(() => 'MedPredict-Room-' + Math.floor(Math.random() * 10000))[0]
  const [roomName, setRoomName] = useState(roomParam || defaultRoom)
  const [joined, setJoined] = useState(false)
  const isPredefinedRoom = !!roomParam

  // On utilise Jitsi Meet (Embed gratuit et performant)
  const displayName = user ? encodeURIComponent(`${user.first_name || ''} ${user.last_name || user.username}`.trim()) : 'Utilisateur'
  const jitsiUrl = `https://meet.jit.si/${roomName}#config.prejoinPageEnabled=false&config.startWithAudioMuted=false&config.startWithVideoMuted=false&userInfo.displayName="${displayName}"`

  return (
    <div className="p-8 space-y-6 max-w-[1400px] mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-on-surface tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Vidéoconférence
          </h1>
          <p className="text-on-surface-variant text-sm mt-1">
            Connectez-vous en toute sécurité avec vos patients via notre service de téléconsultation.
          </p>
        </div>
        
        {!joined && (
           <div className="flex flex-col md:flex-row items-start md:items-center gap-3">
             <div className="flex flex-col">
               <label className="text-xs font-bold text-on-surface-variant mb-1 uppercase tracking-wider">Salle de consultation</label>
               <input 
                 type="text" 
                 value={roomName}
                 onChange={(e) => setRoomName(e.target.value)}
                 disabled={isPredefinedRoom}
                 className="bg-white/70 border border-white/80 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/20 outline-none w-64 disabled:opacity-70 disabled:bg-surface-container-lowest"
                 placeholder="Nom de la salle"
               />
               {isPredefinedRoom && (
                 <span className="text-[10px] text-emerald-600 font-bold mt-1 ml-1 flex items-center gap-1">
                   <span className="material-symbols-outlined text-[12px]">check_circle</span>
                   Salle sécurisée associée au rendez-vous
                 </span>
               )}
             </div>
             <button 
               onClick={() => setJoined(true)}
               className="mt-5 md:mt-0 primary-gradient text-white px-8 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-emerald-500/20 hover:-translate-y-0.5 transition-all w-full md:w-auto flex items-center justify-center gap-2"
             >
               <span className="material-symbols-outlined text-[18px]">meeting_room</span>
               Rejoindre
             </button>
           </div>
        )}
        
        {joined && (
          <button 
            onClick={() => setJoined(false)}
            className="bg-rose-500 text-white px-6 py-2 rounded-xl text-sm font-semibold shadow-lg shadow-rose-500/20 hover:-translate-y-0.5 transition-all"
          >
            Quitter la conférence
          </button>
        )}
      </div>

      <div className="bg-white/40 backdrop-blur-xl border border-white/80 rounded-[2rem] overflow-hidden min-h-[600px] shadow-xl relative group">
        {!joined ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center space-y-6">
            <div className="w-24 h-24 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-500 animate-pulse">
               <span className="material-symbols-outlined text-5xl">videocam</span>
            </div>
            <div className="max-w-md">
              <h3 className="text-xl font-bold text-on-surface mb-2">Prêt pour votre consultation ?</h3>
              <p className="text-on-surface-variant text-sm leading-relaxed">
                Cliquez sur le bouton ci-dessus pour démarrer l'appel vidéo. Assurez-vous d'avoir autorisé l'accès à votre caméra et votre micro.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4 w-full max-w-sm pt-4">
               <div className="p-4 rounded-2xl bg-white/60 border border-white/40 text-left">
                  <span className="material-symbols-outlined text-emerald-500 mb-2">lock</span>
                  <p className="text-xs font-bold text-on-surface">Sécurisé</p>
                  <p className="text-[10px] text-on-surface-variant">Flux crypté de bout en bout</p>
               </div>
               <div className="p-4 rounded-2xl bg-white/60 border border-white/40 text-left">
                  <span className="material-symbols-outlined text-blue-500 mb-2">hd</span>
                  <p className="text-xs font-bold text-on-surface">Haute Qualité</p>
                  <p className="text-[10px] text-on-surface-variant">Vidéo HD et audio cristallin</p>
               </div>
            </div>
          </div>
        ) : (
          <iframe
            src={jitsiUrl}
            allow="camera; microphone; fullscreen; display-capture; autoplay"
            className="w-full h-[700px] border-0"
            title="Teleconsultation Video"
          />
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <div className="md:col-span-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl p-6 text-white shadow-lg shadow-indigo-500/20">
            <h4 className="font-bold flex items-center gap-2 mb-3">
               <span className="material-symbols-outlined">info</span>
               Conseils pour une bonne téléconsultation
            </h4>
            <ul className="text-sm space-y-2 opacity-90 list-disc list-inside">
               <li>Utilisez un casque pour éviter les échos</li>
               <li>Placez-vous dans un endroit calme et bien éclairé</li>
               <li>Vérifiez votre connexion internet avant de commencer</li>
               <li>Partagez votre écran si vous devez montrer des documents</li>
            </ul>
         </div>
         <div className="bg-white/70 backdrop-blur-xl border border-white/80 rounded-3xl p-6 shadow-sm">
            <h4 className="font-bold text-on-surface mb-3 flex items-center gap-2">
               <span className="material-symbols-outlined text-emerald-500">support_agent</span>
               Besoin d'aide ?
            </h4>
            <p className="text-xs text-on-surface-variant mb-4">Si vous rencontrez des problèmes techniques pendant l'appel, n'hésitez pas à contacter le support ou à rafraîchir la page.</p>
            <button className="w-full py-2 bg-surface-container-high text-on-surface rounded-xl text-xs font-bold hover:bg-surface-container transition-all">
               Consulter la FAQ
            </button>
         </div>
      </div>
    </div>
  )
}
