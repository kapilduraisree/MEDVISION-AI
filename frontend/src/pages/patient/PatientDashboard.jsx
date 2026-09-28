import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText, Pill, Calendar, AlertTriangle, TrendingUp, Bell,
  Activity, Heart, ChevronRight, CheckCircle, Clock, Zap
} from 'lucide-react';
import { patientsAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import StatusBadge from '../../components/ui/StatusBadge';
import { DisclaimerBox } from '../../components/ui/DisclaimerBox';

function StatCard({ icon: Icon, label, value, color, to }) {
  const content = (
    <div className={`card hover:shadow-md transition-shadow flex items-center gap-4 ${to ? 'cursor-pointer' : ''}`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
      </div>
    </div>
  );
  return to ? <Link to={to}>{content}</Link> : content;
}

export default function PatientDashboard() {
  const { user } = useAuth();
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    patientsAPI.getDashboard()
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Welcome back, {user?.full_name?.split(' ')[0]} 👋</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Here's your health overview for today</p>
        </div>
        <Link to="/ai-summary" className="btn-primary">
          <Zap className="w-4 h-4" /> Generate AI Summary
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText}      label="Total Reports"         value={data?.total_reports ?? 0}          color="bg-blue-500"   to="/reports" />
        <StatCard icon={AlertTriangle} label="Values Need Attention" value={data?.abnormal_count ?? 0}         color="bg-red-500"    to="/reports" />
        <StatCard icon={Pill}          label="Active Medications"    value={data?.active_medications?.length ?? 0} color="bg-green-500"  to="/reminders" />
        <StatCard icon={Calendar}      label="Upcoming Appointments" value={data?.upcoming_appointments ?? 0}  color="bg-purple-500" to="/appointments" />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent reports */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title mb-0">Recent Reports</h2>
            <Link to="/reports" className="text-sm text-primary-600 hover:underline flex items-center gap-1">
              View all <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
          {data?.recent_reports?.length > 0 ? (
            <div className="space-y-3">
              {data.recent_reports.map(r => (
                <Link key={r.id} to={`/reports/${r.id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4 text-primary-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-200 capitalize">
                        {r.report_type?.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-gray-500">
                        {r.lab_name || 'Lab Report'} · {new Date(r.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <FileText className="w-10 h-10 mx-auto mb-2 opacity-40" />
              <p className="text-sm">No reports yet. <Link to="/reports" className="text-primary-600 hover:underline">Upload your first report</Link></p>
            </div>
          )}
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {/* Abnormal values */}
          {data?.abnormal_values?.length > 0 && (
            <div className="card border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/10">
              <h3 className="font-semibold text-red-700 dark:text-red-400 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Values Needing Attention
              </h3>
              <div className="space-y-2">
                {data.abnormal_values.map((v, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300">{v.test_name}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{v.result} {v.unit}</span>
                      <StatusBadge status={v.status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick actions */}
          <div className="card">
            <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { to: '/symptoms',      icon: Activity,  label: 'Add Symptoms' },
                { to: '/reports',       icon: FileText,  label: 'Upload Report' },
                { to: '/prescriptions', icon: Pill,      label: 'Upload Prescription' },
                { to: '/chatbot',       icon: Heart,     label: 'Ask AI Assistant' },
                { to: '/reminders',     icon: Clock,     label: 'Set Reminder' },
              ].map(({ to, icon: Icon, label }) => (
                <Link key={to} to={to}
                  className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group">
                  <Icon className="w-4 h-4 text-primary-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-primary-600">{label}</span>
                  <ChevronRight className="w-3 h-3 text-gray-400 ml-auto" />
                </Link>
              ))}
            </div>
          </div>

          {/* Active meds */}
          {data?.active_medications?.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                <Pill className="w-4 h-4 text-green-500" /> Current Medications
              </h3>
              <div className="space-y-2">
                {data.active_medications.slice(0, 4).map((m, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
                    <span className="text-gray-700 dark:text-gray-300">{m.medicine_name}</span>
                    <span className="text-xs text-gray-400 ml-auto">{m.frequency}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <DisclaimerBox />
    </div>
  );
}
