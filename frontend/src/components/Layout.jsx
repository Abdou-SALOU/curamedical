import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import ChatbotWidget from './ChatbotWidget'
import useAuthStore from '../store/authStore'

const MOBILE_LINKS = [
  { to: '/',              icon: 'dashboard',    label: 'Accueil',  roles: ['admin','doctor','secretary','patient'] },
  { to: '/patients',      icon: 'group',        label: 'Patients', roles: ['admin','doctor','secretary'] },
  { to: '/appointments',  icon: 'event',        label: 'RDV',      roles: ['admin','doctor','secretary','patient'] },
  { to: '/consultations', icon: 'stethoscope',  label: 'Consult.', roles: ['admin','doctor','patient'] },
  { to: '/prescriptions', icon: 'medication',   label: 'Ordonn.',  roles: ['admin','doctor','patient'] },
]

export default function Layout({ children }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { user } = useAuthStore()
  const { pathname } = useLocation()
  const isPatient = user?.role === 'patient'

  const mobileLinks = MOBILE_LINKS.filter(l => l.roles.includes(user?.role))

  return (
    <div className="flex min-h-screen">
      <Navbar isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />

      <main
        className={`flex-1 overflow-auto transition-all duration-300 ${
          isCollapsed ? 'md:ml-[80px]' : 'md:ml-[272px]'
        }`}
      >
        <div className="page-enter min-h-screen">
          {children}
        </div>
      </main>

      {/* AI Chatbot – only for staff */}
      {!isPatient && <ChatbotWidget />}

      {/* ── Mobile bottom navigation ── */}
      <nav className="mobile-nav">
        {mobileLinks.map(({ to, icon, label }) => {
          const active = pathname === to
          return (
            <Link
              key={to}
              to={to}
              className={`flex flex-col items-center gap-0.5 px-3 py-1 rounded-xl transition-colors ${
                active ? 'text-emerald-600' : 'text-slate-400'
              }`}
            >
              <span
                className="material-symbols-outlined text-[22px]"
                style={{ fontVariationSettings: active ? "'FILL' 1" : "'FILL' 0" }}
              >
                {icon}
              </span>
              <span className="text-[10px] font-bold tracking-wide">{label}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
