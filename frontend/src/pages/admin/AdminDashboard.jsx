import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Stethoscope, FileText, Calendar, Shield, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

export default function AdminDashboard() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminAPI.getAnalytics().then(r => setData(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;

  const stats = [
    { icon: Users,       label: 'Total Users',    value: data?.totals?.users    ?? 0, color: 'bg-blue-500',   to: '/admin/users'   },
    { icon: Users,       label: 'Patients',        value: data?.totals?.patients ?? 0, color: 'bg-green-500',  to: '/admin/users'   },
    { icon: Stethoscope, label: 'Doctors',          value: data?.totals?.doctors  ?? 0, color: 'bg-purple-500', to: '/admin/doctors' },
    { icon: FileText,    label: 'Reports',          value: data?.totals?.reports  ?? 0, color: 'bg-yellow-500', to: '/admin/users'   },
    { icon: Calendar,    label: 'Appointments',     value: data?.totals?.appointments ?? 0, color: 'bg-pink-500', to: '/admin/users' },
    { icon: Shield,      label: 'Audit Logs',       value: '—',                          color: 'bg-gray-500', to: '/admin/audit-logs' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Admin Dashboard</h1>
          <p className="text-sm text-gray-500">System overview and management</p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map(s => (
          <Link key={s.label} to={s.to} className="card hover:shadow-md transition-shadow flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${s.color}`}><s.icon className="w-6 h-6 text-white" /></div>
            <div><p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p><p className="text-sm text-gray-500">{s.label}</p></div>
          </Link>
        ))}
      </div>

      {data?.monthly_registrations?.length > 0 && (
        <div className="card">
          <h2 className="section-title flex items-center gap-2"><BarChart2 className="w-4 h-4" />Monthly User Registrations</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.monthly_registrations.reverse()} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} tickFormatter={v => new Date(v).toLocaleDateString('en-IN', { month: 'short' })} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip labelFormatter={v => new Date(v).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })} />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Registrations" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { to: '/admin/users',      label: 'Manage Users',    icon: Users       },
          { to: '/admin/doctors',    label: 'Manage Doctors',  icon: Stethoscope },
          { to: '/admin/medicines',  label: 'Medicines DB',    icon: FileText    },
          { to: '/admin/audit-logs', label: 'Audit Logs',      icon: Shield      },
        ].map(a => (
          <Link key={a.to} to={a.to} className="card flex flex-col items-center gap-2 py-5 hover:shadow-md transition-shadow text-center">
            <a.icon className="w-6 h-6 text-primary-500" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{a.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
