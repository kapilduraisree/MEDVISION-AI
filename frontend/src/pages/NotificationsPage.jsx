import React, { useEffect, useState } from 'react';
import { Bell, CheckCheck, AlertTriangle, Calendar, FileText, Pill } from 'lucide-react';
import { notificationsAPI } from '../services/api';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

const TYPE_ICONS = {
  reminder:    <Pill className="w-4 h-4 text-green-500" />,
  appointment: <Calendar className="w-4 h-4 text-blue-500" />,
  report:      <FileText className="w-4 h-4 text-primary-500" />,
  emergency:   <AlertTriangle className="w-4 h-4 text-red-500" />,
  doctor_note: <FileText className="w-4 h-4 text-purple-500" />,
  system:      <Bell className="w-4 h-4 text-gray-500" />,
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [unread, setUnread]               = useState(0);
  const [loading, setLoading]             = useState(true);

  const load = () => {
    notificationsAPI.list().then(r => { setNotifications(r.data.notifications || []); setUnread(r.data.unread_count || 0); }).catch(() => {}).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const markRead = async (id) => {
    await notificationsAPI.markRead(id);
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    setUnread(u => Math.max(0, u - 1));
  };

  const markAllRead = async () => {
    await notificationsAPI.markAllRead();
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    setUnread(0);
    toast.success('All marked as read');
  };

  return (
    <div className="max-w-3xl space-y-5 animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="text-sm text-gray-500">{unread} unread</p>
        </div>
        {unread > 0 && (
          <button onClick={markAllRead} className="btn-secondary text-sm">
            <CheckCheck className="w-4 h-4" /> Mark All Read
          </button>
        )}
      </div>

      {loading ? <LoadingSpinner /> : notifications.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <Bell className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No notifications</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map(n => (
            <div
              key={n.id}
              onClick={() => !n.is_read && markRead(n.id)}
              className={`card py-3 cursor-pointer transition-colors hover:shadow-md ${!n.is_read ? 'border-l-4 border-primary-500 bg-primary-50 dark:bg-primary-900/10' : ''}`}
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center flex-shrink-0">
                  {TYPE_ICONS[n.notification_type] || <Bell className="w-4 h-4 text-gray-500" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className={`text-sm font-medium ${!n.is_read ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-300'}`}>{n.title}</p>
                    {!n.is_read && <span className="w-2 h-2 bg-primary-500 rounded-full flex-shrink-0" />}
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{n.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
