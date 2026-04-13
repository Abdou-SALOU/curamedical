import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const ALL_LINKS = [
  { to: '/',              icon: 'grid_view',       label: 'Vue d\'ensemble', roles: ['admin','doctor','secretary','patient'] },
  { to: '/patients',      icon: 'person_search',   label: 'Patients',        roles: ['admin','doctor','secretary'] },
  { to: '/appointments',  icon: 'event_available', label: 'Rendez-vous',     roles: ['admin','doctor','secretary','patient'] },
  { to: '/consultations', icon: 'stethoscope',     label: 'Consultations',   roles: ['admin','doctor','patient']            },
  { to: '/video',         icon: 'videocam',        label: 'Vidéoconférence', roles: ['admin','doctor','patient']            },
  { to: '/prescriptions', icon: 'clinical_notes',  label: 'Ordonnances',     roles: ['admin','doctor','patient']            },
  { to: '/admin',         icon: 'shield_person',   label: 'Administration',  roles: ['admin']                     },
]

const roleConfig = {
  admin:     { label: 'Administrateur' },
  doctor:    { label: 'Médecin'        },
  secretary: { label: 'Secrétaire'     },
  patient:   { label: 'Patient'        },
}

function getInitials(user) {
  if (!user) return '?'
  const f = user.first_name?.charAt(0) || ''
  const l = (user.last_name || user.username)?.charAt(0) || ''
  return (f + l).toUpperCase() || user.username?.charAt(0).toUpperCase() || '?'
}

export default function Navbar({ isCollapsed, setIsCollapsed }) {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  const links = ALL_LINKS.filter(link => !user || link.roles.includes(user.role))
  const role = roleConfig[user?.role] || { label: user?.role || '' }

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside className={`hidden md:flex fixed inset-y-0 left-0 z-50 flex-col bg-slate-950/95 backdrop-blur-2xl border-r border-white/[0.07] shadow-[12px_0_48px_rgba(0,0,0,0.2)] transition-all duration-300 ${isCollapsed ? 'w-[80px]' : 'w-[272px]'}`}>
      
      {/* Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3.5 top-9 w-7 h-7 bg-slate-800 border border-white/10 rounded-full flex items-center justify-center text-white hover:bg-slate-700 hover:scale-110 transition-all z-50 shadow-md"
        title={isCollapsed ? "Ouvrir le menu" : "Réduire le menu"}
      >
        <span className="material-symbols-outlined text-[16px] transition-transform duration-300" style={{ transform: isCollapsed ? 'rotate(180deg)' : 'rotate(0deg)' }}>
          chevron_left
        </span>
      </button>
      {/* Subtle green glow at top */}
      <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-emerald-500/12 to-transparent pointer-events-none" />

      {/* Logo */}
      <div className={`relative px-7 py-7 flex items-center ${isCollapsed ? 'justify-center !px-0' : 'gap-3.5'}`}>
        <div className="w-10 h-10 rounded-[14px] bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-[0_8px_24px_rgba(16,185,129,0.35)] shrink-0">
          <span className="material-symbols-outlined text-white text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>
            biotech
          </span>
        </div>
        {!isCollapsed && (
          <div className="animate-in fade-in zoom-in duration-300 whitespace-nowrap overflow-hidden">
            <h1 className="text-[17px] font-black leading-none tracking-tight text-white">
              MedPredict
            </h1>
            <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.22em] text-emerald-400/80">
              Système médical IA
            </p>
          </div>
        )}
      </div>

      {/* Nav links */}
      <nav className="relative flex-1 px-3 py-2 space-y-0.5 overflow-y-auto soft-scrollbar">
        {links.map(({ to, icon, label }) => {
          const isActive = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              className={`
                group relative flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm font-medium
                transition-all duration-200 overflow-hidden
                ${isActive
                  ? 'text-slate-950 shadow-[0_4px_16px_rgba(16,185,129,0.35)]'
                  : 'text-slate-400 hover:text-white hover:bg-white/[0.06]'
                }
                ${isCollapsed ? 'justify-center' : ''}
              `}
              title={isCollapsed ? label : ''}
            >
              {isActive && (
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-2xl" />
              )}
              <span
                className="material-symbols-outlined relative z-10 text-[21px] transition-transform duration-200 group-hover:scale-105"
                style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
              >
                {icon}
              </span>
              {!isCollapsed && <span className="relative z-10 font-semibold whitespace-nowrap overflow-hidden animate-in fade-in zoom-in duration-300">{label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Divider */}
      <div className={`mx-5 h-px bg-white/[0.06] my-1 ${isCollapsed ? 'mx-3' : ''}`} />

      {/* User + logout */}
      <div className={`px-3 pb-5 pt-2 ${isCollapsed ? 'space-y-4' : 'space-y-1'}`}>
        {user && (
          <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-3 px-3'} py-2.5 rounded-2xl hover:bg-white/[0.05] transition-colors cursor-default`} title={isCollapsed ? user.first_name || user.username : ''}>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-white text-xs font-black shadow-[0_4px_12px_rgba(16,185,129,0.3)] shrink-0">
              {getInitials(user)}
            </div>
            {!isCollapsed && (
              <div className="min-w-0 flex-1 animate-in fade-in zoom-in duration-300 whitespace-nowrap overflow-hidden">
                <p className="text-sm font-bold text-white truncate leading-tight">
                  {user.first_name || user.username} {user.last_name || ''}
                </p>
                <p className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400/70 mt-0.5 truncate">
                  {role.label}
                </p>
              </div>
            )}
          </div>
        )}
        <button
          onClick={handleLogout}
          title={isCollapsed ? 'Déconnexion' : ''}
          className={`group flex w-full items-center ${isCollapsed ? 'justify-center' : 'justify-start gap-2 px-4'} py-2.5 rounded-2xl text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-rose-400 hover:bg-rose-400/8 transition-all duration-200`}
        >
          <span className="material-symbols-outlined text-[17px] transition-transform duration-200 group-hover:-translate-x-0.5">
            logout
          </span>
          {!isCollapsed && <span className="whitespace-nowrap overflow-hidden animate-in fade-in zoom-in duration-300">Déconnexion</span>}
        </button>
      </div>
    </aside>
  )
}
