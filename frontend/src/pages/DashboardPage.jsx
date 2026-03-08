import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie,
  Cell, Legend
} from 'recharts'
import { Users, Calendar, Stethoscope, Brain } from 'lucide-react'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4']

export default function DashboardPage() {
  const [stats, setStats] = useState({
    patients: 0, appointments: 0,
    consultations: 0, ia_used: 0
  })
  const [diagnosisData, setDiagnosisData] = useState([])
  const [appointmentStatusData, setAppointmentStatusData] = useState([])
  const [monthlyData, setMonthlyData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [patients, appointments, consultations] = await Promise.all([
          api.get('/api/patients/'),
          api.get('/api/appointments/'),
          api.get('/api/consultations/'),
        ])

        const patientsList = patients.data.results || patients.data
        const appointmentsList = appointments.data.results || appointments.data
        const consultationsList = consultations.data.results || consultations.data

        // Stats principales
        const iaUsed = consultationsList.filter(c => c.ia_used).length
        setStats({
          patients: patientsList.length,
          appointments: appointmentsList.length,
          consultations: consultationsList.length,
          ia_used: iaUsed
        })

        // Répartition des diagnostics
        const diagCounts = {}
        consultationsList.forEach(c => {
          if (c.diagnosis) {
            diagCounts[c.diagnosis] = (diagCounts[c.diagnosis] || 0) + 1
          }
        })
        const diagData = Object.entries(diagCounts)
          .map(([name, value]) => ({ name, value }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 6)
        setDiagnosisData(diagData)

        // Statuts des rendez-vous
        const statusCounts = {}
        const statusLabels = {
          planned: 'Planifié', confirmed: 'Confirmé',
          in_progress: 'En cours', completed: 'Terminé', cancelled: 'Annulé'
        }
        appointmentsList.forEach(a => {
          const label = statusLabels[a.status] || a.status
          statusCounts[label] = (statusCounts[label] || 0) + 1
        })
        setAppointmentStatusData(
          Object.entries(statusCounts).map(([name, value]) => ({ name, value }))
        )

        // Consultations par mois
        const monthlyCounts = {}
        const monthNames = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                            'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        consultationsList.forEach(c => {
          const date = new Date(c.created_at)
          const key = monthNames[date.getMonth()]
          monthlyCounts[key] = (monthlyCounts[key] || 0) + 1
        })
        setMonthlyData(
          Object.entries(monthlyCounts).map(([month, count]) => ({ month, count }))
        )

      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  const cards = [
    { label: 'Patients',       value: stats.patients,       icon: Users,        color: 'bg-blue-500',   to: '/patients'       },
    { label: 'Rendez-vous',    value: stats.appointments,   icon: Calendar,     color: 'bg-green-500',  to: '/appointments'   },
    { label: 'Consultations',  value: stats.consultations,  icon: Stethoscope,  color: 'bg-purple-500', to: '/consultations'  },
    { label: 'IA consultée',   value: stats.ia_used,        icon: Brain,        color: 'bg-orange-500', to: '/consultations'  },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 text-lg">Chargement du tableau de bord...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Tableau de bord</h1>
      <p className="text-gray-500 mb-8">Vue d'ensemble de l'activité du cabinet</p>

      {/* Cartes stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map(({ label, value, icon: Icon, color, to }) => (
          <Link
            key={label}
            to={to}
            className="bg-white rounded-xl shadow-sm p-6 flex items-center gap-4 hover:shadow-md transition-all"
          >
            <div className={`${color} text-white p-3 rounded-xl`}>
              <Icon size={24} />
            </div>
            <div>
              <p className="text-gray-500 text-sm">{label}</p>
              <p className="text-3xl font-bold text-gray-800">{value}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Graphiques ligne 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

        {/* Consultations par mois */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            📈 Consultations par mois
          </h2>
          {monthlyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                />
                <Bar dataKey="count" name="Consultations" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400">
              Aucune donnée disponible
            </div>
          )}
        </div>

        {/* Statuts des rendez-vous */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            📅 Statuts des rendez-vous
          </h2>
          {appointmentStatusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={appointmentStatusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {appointmentStatusData.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400">
              Aucune donnée disponible
            </div>
          )}
        </div>
      </div>

      {/* Graphiques ligne 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

        {/* Top diagnostics */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            🩺 Pathologies les plus fréquentes
          </h2>
          {diagnosisData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={diagnosisData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 12 }} allowDecimals={false} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={100} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                />
                <Bar dataKey="value" name="Cas" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400">
              Aucune donnée disponible
            </div>
          )}
        </div>

        {/* Utilisation IA */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            🤖 Utilisation du module IA
          </h2>
          {stats.consultations > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Avec IA', value: stats.ia_used },
                      { name: 'Sans IA', value: stats.consultations - stats.ia_used },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                  >
                    <Cell fill="#8b5cf6" />
                    <Cell fill="#e5e7eb" />
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div className="text-center mt-2">
                <span className="text-2xl font-bold text-purple-600">
                  {stats.consultations > 0
                    ? Math.round((stats.ia_used / stats.consultations) * 100)
                    : 0}%
                </span>
                <p className="text-gray-500 text-sm">des consultations utilisent l'IA</p>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400">
              Aucune donnée disponible
            </div>
          )}
        </div>
      </div>

      {/* Accès rapides */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">⚡ Accès rapides</h2>
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Nouveau patient',      to: '/patients',       emoji: '👤' },
            { label: 'Nouveau rendez-vous',  to: '/appointments',   emoji: '📅' },
            { label: 'Nouvelle consultation',to: '/consultations',  emoji: '🩺' },
            { label: 'Nouvelle ordonnance',  to: '/prescriptions',  emoji: '💊' },
          ].map(({ label, to, emoji }) => (
            <Link
              key={to}
              to={to}
              className="flex flex-col items-center p-4 border-2 border-dashed border-gray-200 rounded-xl hover:border-blue-400 hover:bg-blue-50 transition-all"
            >
              <span className="text-3xl mb-2">{emoji}</span>
              <span className="text-sm font-medium text-gray-600 text-center">{label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}