import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Calendar, Bell, CheckCircle, Clock, ChevronRight, Stethoscope } from 'lucide-react';
import { doctorsAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import StatusBadge from '../../components/ui/StatusBadge';
import { useAuth } from '../../context/AuthContext';

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    doctorsAPI.getDashboard().then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome, {user?.full_name} 👨‍⚕️</h1>
          <p className="text-sm text-gray-500">{data?.specialization || 'Doctor'} · {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Calendar, label: 'Upcoming',        value: data?.upcoming_appointments ?? 0, color: 'bg-blue-500',   to: '/doctor/appointments' },
          { icon: Bell,     label: 'Pending Requests', value: data?.pending_requests ?? 0,       color: 'bg-yellow-500', to: '/doctor/appointments' },
          { icon: Users,    label: 'Notifications',    value: data?.unread_notifications ?? 0,   color: 'bg-red-500',    to: '/notifications' },
          { icon: Stethoscope, label: 'Profile',       value: '—',                               color: 'bg-green-500',  to: '/doctor/patients' },
        ].map(s => (
          <Link key={s.label} to={s.to} className="card hover:shadow-md transition-shadow flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${s.color}`}>
              <s.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
              <p className="text-sm text-gray-500">{s.label}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* Upcoming appointments */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="section-title mb-0">Upcoming Appointments</h2>
          <Link to="/doctor/appointments" className="text-sm text-primary-600 hover:underline flex items-center gap-1">
            View all <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
        {!data?.appointments?.length ? (
          <div className="text-center py-10 text-gray-400">
            <Calendar className="w-10 h-10 mx-auto mb-2 opacity-40" />
            <p className="text-sm">No upcoming appointments</p>
          </div>
        ) : (
          <div className="space-y-3">
            {data.appointments.map(a => (
              <div key={a.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                    <Calendar className="w-4 h-4 text-primary-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200">Patient #{a.patient_id}</p>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(a.appointment_date).toLocaleString('en-IN', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
                <StatusBadge status={a.status} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick actions */}
      <div className="card">
        <h2 className="section-title">Quick Actions</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[
            { to: '/doctor/appointments', icon: Calendar, label: 'Manage Appointments' },
            { to: '/doctor/patients',     icon: Users,    label: 'View Patients' },
            { to: '/notifications',       icon: Bell,     label: 'Notifications' },
            { to: '/chatbot',             icon: Stethoscope, label: 'AI Assistant' },
          ].map(a => (
            <Link key={a.to} to={a.to} className="flex items-center gap-2 p-3 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/10 transition-colors">
              <a.icon className="w-5 h-5 text-primary-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{a.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
