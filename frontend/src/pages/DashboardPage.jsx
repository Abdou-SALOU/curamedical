import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie,
  Cell, Legend
} from 'recharts'
import { Users, Calendar, Stethoscope, Brain, ArrowRight, BarChart as BarChartIcon, PieChart as PieChartIcon } from 'lucide-react'
import useAuthStore from '../store/authStore'

const COLORS = ['#10b981', '#6366f1', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4']

export default function DashboardPage() {
  const { user } = useAuthStore()
  const isSecretary = user?.role === 'secretary'

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
        const requests = [
          api.get('/api/patients/'),
          api.get('/api/appointments/'),
        ]

        if (!isSecretary) {
          requests.push(api.get('/api/consultations/'))
        }

        const [patients, appointments, consultations] = await Promise.all(requests)

        const patientsList = patients.data.results || patients.data
        const appointmentsList = appointments.data.results || appointments.data
        const consultationsList = consultations?.data.results || consultations?.data || []

        const iaUsed = consultationsList.filter(c => c.ia_used).length

        setStats({
          patients: patientsList.length,
          appointments: appointmentsList.length,
          consultations: consultationsList.length,
          ia_used: iaUsed
        })

        if (!isSecretary) {
          const diagCounts = {}
          consultationsList.forEach(c => {
            if (c.diagnosis) {
              diagCounts[c.diagnosis] = (diagCounts[c.diagnosis] || 0) + 1
            }
          })
          setDiagnosisData(
            Object.entries(diagCounts)
              .map(([name, value]) => ({ name, value }))
              .sort((a, b) => b.value - a.value)
              .slice(0, 6)
          )
        }

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

        if (!isSecretary) {
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
        }

        if (isSecretary) {
          const monthlyCounts = {}
          const monthNames = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
          appointmentsList.forEach(a => {
            const date = new Date(a.scheduled_at)
            const key = monthNames[date.getMonth()]
            monthlyCounts[key] = (monthlyCounts[key] || 0) + 1
          })
          setMonthlyData(
            Object.entries(monthlyCounts).map(([month, count]) => ({ month, count }))
          )
        }

      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [isSecretary])

  const allCards = [
    { label: 'Total Patients', value: stats.patients, icon: Users, gradient: 'from-emerald-400 to-teal-500', shadow: 'shadow-emerald-500/30', to: '/patients', roles: ['admin', 'doctor', 'secretary'] },
    { label: 'Rendez-vous', value: stats.appointments, icon: Calendar, gradient: 'from-indigo-400 to-blue-500', shadow: 'shadow-blue-500/30', to: '/appointments', roles: ['admin', 'doctor', 'secretary'] },
    { label: 'Consultations', value: stats.consultations, icon: Stethoscope, gradient: 'from-purple-400 to-fuchsia-500', shadow: 'shadow-purple-500/30', to: '/consultations', roles: ['admin', 'doctor'] },
    { label: 'Analyses IA', value: stats.ia_used, icon: Brain, gradient: 'from-amber-400 to-orange-500', shadow: 'shadow-orange-500/30', to: '/consultations', roles: ['admin', 'doctor'] },
  ]

  const cards = allCards.filter(c => c.roles.includes(user?.role))

  const allQuickLinks = [
    { label: 'Nouveau patient', to: '/patients', emoji: '🧑‍⚕️', roles: ['admin', 'doctor', 'secretary'] },
    { label: 'Nouveau rd-vs', to: '/appointments', emoji: '📅', roles: ['admin', 'doctor', 'secretary'] },
    { label: 'Créer consultation', to: '/consultations', emoji: '🩺', roles: ['admin', 'doctor'] },
    { label: 'Rédiger ordonnance', to: '/prescriptions', emoji: '💊', roles: ['admin', 'doctor'] },
  ]

  const quickLinks = allQuickLinks.filter(l => l.roles.includes(user?.role))

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-100px)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
          <div className="text-on-surface-variant text-sm font-medium animate-pulse">Chargement de votre tableau de bord...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold text-on-surface tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Aperçu de l'Activité
          </h1>
          <p className="text-on-surface-variant font-medium mt-2 text-sm max-w-lg">
            Gérez vos patients, suivez vos consultations et accédez rapidement à tous les outils nécessaires à votre pratique médicale.
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-white/60 backdrop-blur-md rounded-2xl border border-white/40 shadow-sm">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs font-semibold text-on-surface-variant tracking-wider uppercase">Système en ligne</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => {
          const { label, value, icon: CardIcon, gradient, shadow, to } = card
          return (
            <Link
              key={label}
              to={to}
              className="group relative overflow-hidden bg-white/70 backdrop-blur-xl rounded-3xl p-6 border border-white/80 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-all duration-300 hover:-translate-y-1 block"
            >
              {/* Decals background gradient */}
              <div className={`absolute -right-6 -top-6 w-24 h-24 bg-gradient-to-br ${gradient} rounded-full opacity-10 group-hover:scale-150 transition-transform duration-500 blur-2xl`}></div>
              
              <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-2xl bg-gradient-to-br ${gradient} text-white shadow-lg ${shadow}`}>
                  <CardIcon size={22} strokeWidth={2.5} />
                </div>
                <div className="w-8 h-8 rounded-full bg-surface-container flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity translate-x-4 group-hover:translate-x-0 duration-300">
                  <ArrowRight size={14} className="text-on-surface-variant" />
                </div>
              </div>
              
              <div>
                <h3 className="text-on-surface-variant text-sm font-semibold mb-1">{label}</h3>
                <p className="text-4xl font-extrabold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  {value}
                </p>
              </div>
            </Link>
          )
        })}
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Data */}
        <div className="bg-white/70 backdrop-blur-xl rounded-3xl p-7 border border-white/80 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-500">
              <Calendar size={20} />
            </div>
            <h2 className="text-xl font-bold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Evolution {isSecretary ? 'des rendez-vous' : 'des consultations'}
            </h2>
          </div>
          
          {monthlyData.length > 0 ? (
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={isSecretary ? '#10b981' : '#6366f1'} />
                      <stop offset="100%" stopColor={isSecretary ? '#34d399' : '#818cf8'} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} dy={10} />
                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip 
                    cursor={{ fill: '#f8fafc' }}
                    contentStyle={{ borderRadius: '16px', border: '1px solid rgba(255,255,255,0.8)', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', backdropFilter: 'blur(10px)', padding: '12px 16px', fontWeight: '500' }} 
                    itemStyle={{ color: '#0f172a', fontWeight: '700' }}
                  />
                  <Bar
                    dataKey="count"
                    name={isSecretary ? 'Rendez-vous' : 'Consultations'}
                    fill="url(#colorGradient)"
                    radius={[6, 6, 0, 0]}
                    barSize={32}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-[280px] text-on-surface-variant/60">
              <BarChartIcon size={40} className="mb-2 opacity-20" />
              <p className="font-medium">Aucune donnée sur les mois récents</p>
            </div>
          )}
        </div>

        {/* Appointment Status Pie */}
        <div className="bg-white/70 backdrop-blur-xl rounded-3xl p-7 border border-white/80 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-shadow duration-300">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-500">
              <Users size={20} />
            </div>
            <h2 className="text-xl font-bold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Statut des Rendez-vous
            </h2>
          </div>
          
          {appointmentStatusData.length > 0 ? (
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={appointmentStatusData}
                    cx="50%" cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                    stroke="none"
                  >
                    {appointmentStatusData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} className="drop-shadow-sm hover:opacity-80 transition-opacity" />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ borderRadius: '16px', border: '1px solid rgba(255,255,255,0.8)', boxShadow: '0 10px 25px rgba(0,0,0,0.05)', backgroundColor: 'rgba(255,255,255,0.95)', padding: '12px 16px' }} 
                    itemStyle={{ fontSize: '14px', fontWeight: '600' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-[280px] text-on-surface-variant/60">
              <PieChartIcon size={40} className="mb-2 opacity-20" />
              <p className="font-medium">Aucun rendez-vous enregistré</p>
            </div>
          )}
        </div>
      </div>

      {/* Doctor only charts & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {!isSecretary && (
          <>
            <div className="lg:col-span-1 bg-white/70 backdrop-blur-xl rounded-3xl p-7 border border-white/80 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-shadow duration-300">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 rounded-xl bg-orange-50 text-orange-500">
                  <Brain size={20} />
                </div>
                <h2 className="text-xl font-bold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Aide IA
                </h2>
              </div>
              
              {stats.consultations > 0 ? (
                <div className="flex flex-col items-center justify-center h-[220px] relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Approuvée IA', value: stats.ia_used },
                          { name: 'Classique', value: stats.consultations - stats.ia_used },
                        ]}
                        cx="50%" cy="50%"
                        innerRadius={60}
                        outerRadius={85}
                        startAngle={180}
                        endAngle={-180}
                        paddingAngle={5}
                        stroke="none"
                        dataKey="value"
                      >
                        <Cell fill="#f59e0b" />
                        <Cell fill="#f1f5f9" />
                      </Pie>
                      <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 6px 20px rgba(0,0,0,0.08)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
                    <span className="text-3xl font-black text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>
                      {Math.round((stats.ia_used / stats.consultations) * 100)}%
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/70 mt-1">
                      Adoption
                    </span>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[220px] text-on-surface-variant/60 font-medium">
                  Données insuffisantes
                </div>
              )}
            </div>

            <div className="lg:col-span-2 bg-white/70 backdrop-blur-xl rounded-3xl p-7 border border-white/80 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-shadow duration-300">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2.5 rounded-xl bg-rose-50 text-rose-500">
                  <Stethoscope size={20} />
                </div>
                <h2 className="text-xl font-bold text-on-surface" style={{ fontFamily: 'Manrope, sans-serif' }}>
                  Top Diagnostics
                </h2>
              </div>
              
              {diagnosisData.length > 0 ? (
                <div className="h-[220px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={diagnosisData} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#f1f5f9" />
                      <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
                      <YAxis dataKey="name" type="category" tick={{ fontSize: 12, fill: '#334155', fontWeight: 500 }} axisLine={false} tickLine={false} width={120} />
                      <Tooltip 
                        cursor={{ fill: 'rgba(241, 245, 249, 0.5)' }}
                        contentStyle={{ borderRadius: '12px', border: '1px solid rgba(255,255,255,0.8)', boxShadow: '0 8px 20px rgba(0,0,0,0.06)' }} 
                      />
                      <Bar dataKey="value" name="Cas identifiés" fill="#ec4899" radius={[0, 6, 6, 0]} barSize={20}>
                        {diagnosisData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex items-center justify-center h-[220px] text-on-surface-variant/60 font-medium">
                  Aucun diagnostic enregistré
                </div>
              )}
            </div>
          </>
        )}

        {/* Quick Actions if Secretary or small quick link section */}
        {isSecretary && (
           <div className="lg:col-span-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl p-8 text-white shadow-xl shadow-indigo-500/20 relative overflow-hidden">
             <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
             
             <h2 className="text-2xl font-bold mb-6 relative z-10" style={{ fontFamily: 'Manrope, sans-serif' }}>
               Actions Rapides
             </h2>
             <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
               {quickLinks.map(({ label, to, emoji }) => (
                 <Link
                   key={to}
                   to={to}
                   className="bg-white/10 hover:bg-white/20 backdrop-blur border border-white/20 rounded-2xl p-5 flex flex-col items-center justify-center gap-3 transition-all hover:scale-105 active:scale-95"
                 >
                   <span className="text-4xl drop-shadow-md">{emoji}</span>
                   <span className="text-sm font-semibold text-center">{label}</span>
                 </Link>
               ))}
             </div>
           </div>
        )}
      </div>
      
      {/* Quick Actions for non-secretary */}
      {!isSecretary && (
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl p-8 text-white shadow-xl shadow-emerald-500/20 relative overflow-hidden">
             <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
             
             <h2 className="text-2xl font-bold mb-6 relative z-10" style={{ fontFamily: 'Manrope, sans-serif' }}>
               Raccourcis Cliniques
             </h2>
             <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
               {quickLinks.map(({ label, to, emoji }) => (
                 <Link
                   key={to}
                   to={to}
                   className="bg-white/10 hover:bg-white/20 backdrop-blur border border-white/20 rounded-2xl p-5 flex flex-col items-center justify-center gap-3 transition-all hover:scale-105 active:scale-95"
                 >
                   <span className="text-4xl drop-shadow-md">{emoji}</span>
                   <span className="text-sm font-semibold text-center">{label}</span>
                 </Link>
               ))}
             </div>
        </div>
      )}
    </div>
  )
}