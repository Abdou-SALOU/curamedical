import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'

const ALL_LINKS = [
  // ── Tous les rôles voient le tableau de bord ──────────────────
  { to: '/',              icon: 'grid_view',       label: 'Tableau de bord',  roles: ['administrateur','medecin','secretaire','patient'] },

  // ── Administrateur : système uniquement ───────────────────────
  { to: '/admin',         icon: 'shield_person',   label: 'Administration',   roles: ['administrateur'] },

  // ── Médecin + Secrétaire : gestion patients & RDV ────────────
  { to: '/patients',      icon: 'person_search',   label: 'Patients',         roles: ['medecin','secretaire'] },
  { to: '/appointments',  icon: 'event_available', label: 'Agenda & RDV',     roles: ['medecin','secretaire'] },

  // ── Médecin : accès clinique complet ──────────────────────────
  { to: '/consultations', icon: 'stethoscope',     label: 'Consultations',    roles: ['medecin'] },
  { to: '/prescriptions', icon: 'clinical_notes',  label: 'Ordonnances',      roles: ['medecin'] },

  // ── Secrétaire : ordonnances en lecture seule ─────────────────
  { to: '/prescriptions', icon: 'clinical_notes',  label: 'Ordonnances',      roles: ['secretaire'] },

  // ── Patient : ses propres données uniquement ──────────────────
  { to: '/appointments',  icon: 'event_available', label: 'Mes rendez-vous',  roles: ['patient'] },
  { to: '/consultations', icon: 'stethoscope',     label: 'Mes consultations',roles: ['patient'] },
  { to: '/prescriptions', icon: 'clinical_notes',  label: 'Mes ordonnances',  roles: ['patient'] },
  { to: '/profile',       icon: 'person',          label: 'Mon profil',       roles: ['patient'] },
]

const roleConfig = {
  administrateur: { label: 'Administrateur' },
  medecin:        { label: 'Médecin'        },
  secretaire:     { label: 'Secrétaire'     },
  patient:        { label: 'Patient'        },
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
  const navigate  = useNavigate()

  const links     = ALL_LINKS.filter(l => !user || l.roles.includes(user.role))
  const role      = roleConfig[user?.role] || { label: user?.role || '' }

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside
      className={`sidebar-dark hidden md:flex fixed inset-y-0 left-0 z-50 flex-col transition-all duration-300 ${
        isCollapsed ? 'w-[80px]' : 'w-[272px]'
      }`}
    >
      {/* ── Ambient glows ── */}
      <div className="absolute inset-x-0 top-0 h-56 pointer-events-none overflow-hidden">
        <div className="absolute -top-16 left-1/2 -translate-x-1/2 w-48 h-48 rounded-full bg-emerald-500/18 blur-3xl" />
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent" />
      </div>
      <div className="absolute inset-x-0 bottom-0 h-40 pointer-events-none overflow-hidden">
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-32 h-32 rounded-full bg-indigo-500/12 blur-3xl" />
      </div>

      {/* ── Collapse toggle ── */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="sidebar-toggle absolute -right-3.5 top-9 w-7 h-7 flex items-center justify-center rounded-full z-50"
        title={isCollapsed ? 'Ouvrir le menu' : 'Réduire le menu'}
      >
        <span
          className="material-symbols-outlined transition-transform duration-300"
          style={{ fontSize: '16px', transform: isCollapsed ? 'rotate(180deg)' : 'rotate(0deg)' }}
        >
          chevron_left
        </span>
      </button>

      {/* ── Logo ── */}
      <Link
        to="/"
        className={`relative z-10 px-5 py-6 flex items-center cursor-pointer group ${
          isCollapsed ? 'justify-center !px-0' : 'gap-3.5'
        }`}
      >
        <div className="logo-icon w-10 h-10 rounded-[14px] flex items-center justify-center shrink-0 transition-transform duration-300 group-hover:scale-105">
          <span
            className="material-symbols-outlined text-white"
            style={{ fontSize: '20px', fontVariationSettings: "'FILL' 1" }}
          >
            biotech
          </span>
        </div>
        {!isCollapsed && (
          <div className="animate-in fade-in zoom-in duration-300 whitespace-nowrap overflow-hidden">
            <h1
              className="text-[17px] font-black leading-none tracking-tight text-white group-hover:text-emerald-400 transition-colors duration-300"
              style={{ fontFamily: 'Manrope, sans-serif' }}
            >
              CuraMedical
            </h1>
            <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.22em] text-emerald-400/75">
              Système médical IA
            </p>
          </div>
        )}
      </Link>

      {/* Divider */}
      <div className="mx-4 h-px opacity-60 bg-gradient-to-r from-transparent via-white/6 to-transparent" />

      {/* ── Nav label ── */}
      {!isCollapsed && (
        <div className="px-5 pt-4 pb-1.5">
          <p className="text-[9px] font-black uppercase tracking-[0.25em] text-slate-500/60">Navigation</p>
        </div>
      )}

      {/* ── Nav links ── */}
      <nav className="relative flex-1 px-3 py-1 space-y-0.5 overflow-y-auto soft-scrollbar">
        {links.map(({ to, icon, label }) => {
          const isActive = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              title={isCollapsed ? label : ''}
              className={`
                group relative flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm font-medium
                transition-all duration-200 overflow-hidden
                ${isCollapsed ? 'justify-center' : ''}
                ${isActive ? 'nav-link-active' : 'nav-link'}
              `}
            >
              {isActive && (
                <span className="absolute right-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-white/40" />
              )}
              <span
                className="material-symbols-outlined relative z-10 transition-transform duration-200 group-hover:scale-110"
                style={{ fontSize: '20px', fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
              >
                {icon}
              </span>
              {!isCollapsed && (
                <span className="relative z-10 font-semibold whitespace-nowrap overflow-hidden animate-in fade-in zoom-in duration-300 text-[13.5px]">
                  {label}
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* ── Bottom section ── */}
      <div className="relative z-10">
        <div className="mx-4 h-px opacity-50 bg-gradient-to-r from-transparent via-white/6 to-transparent" />

        <div className={`px-3 pb-5 pt-3 ${isCollapsed ? 'space-y-3' : 'space-y-1.5'}`}>
          {/* User info */}
          {user && (
            <div
              className={`flex items-center py-2.5 rounded-2xl cursor-default ${
                isCollapsed ? 'justify-center' : 'gap-3 px-3'
              }`}
              title={isCollapsed ? `${user.first_name || user.username} — ${role.label}` : ''}
            >
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-white text-xs font-black shrink-0 shadow-[0_4px_12px_rgba(16,185,129,0.3)]">
                {getInitials(user)}
              </div>
              {!isCollapsed && (
                <div className="min-w-0 flex-1 animate-in fade-in zoom-in duration-300 whitespace-nowrap overflow-hidden">
                  <p className="text-[13px] font-bold text-white truncate leading-tight">
                    {user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username}
                  </p>
                  <p className="text-[10px] font-semibold uppercase tracking-wider mt-0.5 truncate text-emerald-400/65">
                    {role.label}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Logout */}
          <button
            onClick={handleLogout}
            title={isCollapsed ? 'Déconnexion' : ''}
            className={`logout-btn group flex w-full items-center py-2.5 rounded-2xl text-[11px] font-bold uppercase tracking-widest ${
              isCollapsed ? 'justify-center' : 'justify-start gap-2.5 px-4'
            }`}
          >
            <span
              className="material-symbols-outlined transition-transform duration-200 group-hover:-translate-x-0.5"
              style={{ fontSize: '17px' }}
            >
              logout
            </span>
            {!isCollapsed && (
              <span className="whitespace-nowrap overflow-hidden animate-in fade-in zoom-in duration-300">
                Déconnexion
              </span>
            )}
          </button>
        </div>
      </div>
    </aside>
  )
}
