import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import {
  LayoutDashboard, Users, Calendar,
  Stethoscope, FileText, LogOut
} from 'lucide-react'

const links = [
  { to: '/',               icon: LayoutDashboard, label: 'Tableau de bord' },
  { to: '/patients',       icon: Users,           label: 'Patients'        },
  { to: '/appointments',   icon: Calendar,        label: 'Rendez-vous'     },
  { to: '/consultations',  icon: Stethoscope,     label: 'Consultations'   },
  { to: '/prescriptions',  icon: FileText,        label: 'Ordonnances'     },
]

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-64 min-h-screen bg-blue-900 text-white flex flex-col">
      <div className="p-6 border-b border-blue-700">
        <h1 className="text-2xl font-bold">🏥 MedPredict</h1>
        <p className="text-blue-300 text-sm mt-1">Cabinet Médical</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, icon: Icon, label }) => {
          const active = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                active
                  ? 'bg-blue-600 text-white font-semibold'
                  : 'text-blue-200 hover:bg-blue-800'
              }`}
            >
              <Icon size={20} />
              {label}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-blue-700">
        {user && (
          <div className="mb-3 px-2">
            <p className="font-semibold text-sm">{user.first_name} {user.last_name}</p>
            <p className="text-blue-300 text-xs capitalize">{user.role}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-4 py-2 text-blue-200 hover:bg-blue-800 rounded-lg transition-all"
        >
          <LogOut size={18} />
          Déconnexion
        </button>
      </div>
    </aside>
  )
}