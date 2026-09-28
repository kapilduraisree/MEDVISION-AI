import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard, User, FileText, Pill, Bell, Calendar, MessageSquare,
  FolderOpen, Users, AlertTriangle, Settings, LogOut, ChevronLeft,
  ChevronRight, Activity, TrendingUp, Syringe, ShoppingBag, Zap, Heart,
  Stethoscope, Shield
} from 'lucide-react';

const patientNav = [
  { to: '/dashboard',        icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/profile',          icon: User,            label: 'Profile' },
  { to: '/symptoms',         icon: Activity,        label: 'Symptoms' },
  { to: '/reports',          icon: FileText,        label: 'Reports' },
  { to: '/prescriptions',    icon: Syringe,         label: 'Prescriptions' },
  { to: '/medicines',        icon: Pill,            label: 'Medicines' },
  { to: '/reminders',        icon: Bell,            label: 'Reminders' },
  { to: '/pharmacy-bills',   icon: ShoppingBag,     label: 'Pharmacy Bills' },
  { to: '/health-trends',    icon: TrendingUp,      label: 'Health Trends' },
  { to: '/ai-summary',       icon: Zap,             label: 'AI Summary' },
  { to: '/chatbot',          icon: MessageSquare,   label: 'AI Assistant' },
  { to: '/locker',           icon: FolderOpen,      label: 'Medical Locker' },
  { to: '/family',           icon: Users,           label: 'Family' },
  { to: '/appointments',     icon: Calendar,        label: 'Appointments' },
  { to: '/emergency',        icon: AlertTriangle,   label: 'Emergency' },
  { to: '/notifications',    icon: Bell,            label: 'Notifications' },
  { to: '/settings',         icon: Settings,        label: 'Settings' },
];

const doctorNav = [
  { to: '/doctor/dashboard',    icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/doctor/appointments', icon: Calendar,        label: 'Appointments' },
  { to: '/doctor/patients',     icon: Users,           label: 'Patients' },
  { to: '/notifications',       icon: Bell,            label: 'Notifications' },
  { to: '/settings',            icon: Settings,        label: 'Settings' },
];

const adminNav = [
  { to: '/admin/dashboard',   icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/admin/users',       icon: Users,           label: 'Users' },
  { to: '/admin/doctors',     icon: Stethoscope,     label: 'Doctors' },
  { to: '/admin/medicines',   icon: Pill,            label: 'Medicines' },
  { to: '/admin/audit-logs',  icon: Shield,          label: 'Audit Logs' },
  { to: '/settings',          icon: Settings,        label: 'Settings' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const navItems =
    user?.role === 'admin'  ? adminNav :
    user?.role === 'doctor' ? doctorNav : patientNav;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className={`
      flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
      transition-all duration-300 h-screen sticky top-0
      ${collapsed ? 'w-16' : 'w-60'}
    `}>
      {/* Logo */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Heart className="w-7 h-7 text-primary-600" />
            <span className="font-bold text-lg text-primary-600">MedVision</span>
          </div>
        )}
        {collapsed && <Heart className="w-7 h-7 text-primary-600 mx-auto" />}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* User info */}
      {!collapsed && user && (
        <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          <p className="text-sm font-semibold text-gray-800 dark:text-white truncate">{user.full_name}</p>
          <span className="inline-block px-2 py-0.5 text-xs rounded-full bg-primary-100 text-primary-700 capitalize">
            {user.role}
          </span>
        </div>
      )}

      {/* Nav links */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            title={collapsed ? label : undefined}
            className={({ isActive }) => `
              flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium
              transition-colors duration-150
              ${isActive
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'}
            `}
          >
            <Icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm font-medium
                     text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
