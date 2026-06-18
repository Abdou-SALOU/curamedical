import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import ChatbotWidget from './ChatbotWidget'
import useAuthStore from '../store/authStore'
import useThemeStore from '../store/themeStore'

const MOBILE_LINKS = [
  { to: '/',              icon: 'grid_view',       label: 'Accueil',  roles: ['administrateur','medecin','secretaire','patient'] },
  { to: '/admin',         icon: 'shield_person',   label: 'Admin',    roles: ['administrateur'] },
  { to: '/patients',      icon: 'people',          label: 'Patients', roles: ['medecin','secretaire'] },
  { to: '/appointments',  icon: 'event_available', label: 'RDV',      roles: ['medecin','secretaire','patient'] },
  { to: '/consultations', icon: 'stethoscope',     label: 'Consult.', roles: ['medecin','patient'] },
  { to: '/prescriptions', icon: 'clinical_notes',  label: 'Ordonn.',  roles: ['medecin','secretaire','patient'] },
  { to: '/profile',       icon: 'person',          label: 'Profil',   roles: ['patient'] },
]

const PAGE_TITLES = {
  '/':              { label: 'Vue d\'ensemble',  icon: 'grid_view'       },
  '/patients':      { label: 'Patients',         icon: 'person_search'   },
  '/appointments':  { label: 'Rendez-vous',      icon: 'event_available' },
  '/consultations': { label: 'Consultations',    icon: 'stethoscope'     },
  '/prescriptions': { label: 'Ordonnances',      icon: 'clinical_notes'  },
  '/profile':       { label: 'Mon profil',       icon: 'person'          },
  '/admin':         { label: 'Administration',   icon: 'shield_person'   },
  '/patients/trash':{ label: 'Corbeille',        icon: 'delete'          },
}

export default function Layout({ children }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { user } = useAuthStore()
  const { pathname } = useLocation()
  const { resolvedTheme, toggle } = useThemeStore()

  const mobileLinks = MOBILE_LINKS.filter(l => l.roles.includes(user?.role))
  const pageInfo    = PAGE_TITLES[pathname] || { label: 'CuraMedical', icon: 'home' }

  return (
    <div className="flex min-h-screen">
      <Navbar isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />

      <main
        className={`flex-1 overflow-auto transition-all duration-300 ${
          isCollapsed ? 'md:ml-[80px]' : 'md:ml-[272px]'
        }`}
      >
        {/* ── Top bar (desktop) ── */}
        <div className="topbar hidden md:flex items-center justify-between px-8 py-4 sticky top-0 z-30">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2.5">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span
                className="material-symbols-outlined"
                style={{ fontSize: '18px', color: '#10b981', fontVariationSettings: "'FILL' 1" }}
              >
                {pageInfo.icon}
              </span>
              <span className="text-xs font-bold uppercase tracking-widest text-slate-400 hover:text-emerald-500 transition-colors">
                CuraMedical
              </span>
            </Link>
            <span className="text-slate-300">/</span>
            <span className="text-sm font-bold text-slate-700">{pageInfo.label}</span>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-400 capitalize">
              {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'short' })}
            </span>
            {/* Theme toggle */}
            <button
              onClick={toggle}
              className="theme-toggle-btn"
              title={resolvedTheme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
              aria-label="Changer le thème"
            >
              {resolvedTheme === 'dark' ? (
                /* Soleil — mode clair */
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="4"/>
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
                </svg>
              ) : (
                /* Lune — mode sombre */
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Page content */}
        <div className="page-enter min-h-[calc(100vh-64px)]">
          {children}
        </div>
      </main>

      {/* AI Chatbot */}
      <ChatbotWidget />

      {/* ── Mobile bottom navigation ── */}
      <nav className="mobile-nav">
        {mobileLinks.map(({ to, icon, label }) => {
          const active = pathname === to
          return (
            <Link
              key={to}
              to={to}
              className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-all ${
                active ? 'text-emerald-600' : 'text-slate-400 hover:text-slate-600'
              }`}
            >
              <div className={`relative w-8 h-8 flex items-center justify-center rounded-lg transition-all ${
                active ? 'bg-emerald-50' : ''
              }`}>
                <span
                  className="material-symbols-outlined"
                  style={{ fontSize: '20px', fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0" }}
                >
                  {icon}
                </span>
                {active && (
                  <span className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-4 h-0.5 rounded-full bg-emerald-500" />
                )}
              </div>
              <span className="text-[9px] font-black tracking-wide uppercase">{label}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
