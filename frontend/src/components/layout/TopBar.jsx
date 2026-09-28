import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Sun, Moon, Globe } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { notificationsAPI } from '../../services/api';

export default function TopBar() {
  const { user, updateUser } = useAuth();
  const [unread, setUnread]   = useState(0);
  const [dark, setDark]       = useState(() => document.documentElement.classList.contains('dark'));

  useEffect(() => {
    notificationsAPI.list({ unread_only: true })
      .then(r => setUnread(r.data.unread_count))
      .catch(() => {});
  }, []);

  const toggleDark = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle('dark', next);
    updateUser({ dark_mode: next });
  };

  const toggleLang = () => {
    const next = user?.preferred_language === 'ta' ? 'en' : 'ta';
    updateUser({ preferred_language: next });
  };

  return (
    <header className="h-14 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700
                       flex items-center justify-between px-6 sticky top-0 z-30">
      <div />
      <div className="flex items-center gap-2">
        {/* Language toggle */}
        <button
          onClick={toggleLang}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
                     text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          title="Toggle language"
        >
          <Globe className="w-4 h-4" />
          <span>{user?.preferred_language === 'ta' ? 'தமிழ்' : 'EN'}</span>
        </button>

        {/* Dark mode toggle */}
        <button
          onClick={toggleDark}
          className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          title="Toggle dark mode"
        >
          {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Notifications */}
        <Link
          to="/notifications"
          className="relative p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          <Bell className="w-5 h-5" />
          {unread > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full text-white text-xs flex items-center justify-center font-bold">
              {unread > 9 ? '9+' : unread}
            </span>
          )}
        </Link>

        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-sm font-bold">
          {user?.full_name?.[0]?.toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  );
}
